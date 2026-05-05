"""轻量级异步任务队列 — 基于 asyncio + ThreadPoolExecutor，无外部依赖"""
import asyncio
import uuid
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

logger = logging.getLogger(__name__)

# 任务状态常量
PENDING = "pending"
RUNNING = "running"
DONE = "done"
ERROR = "error"

# 默认配置
MAX_CONCURRENT = int(__import__("os").getenv("MAX_CONCURRENT_TASKS", "5"))
TASK_TTL_SECONDS = 3600  # 完成任务保留 1 小时


class TaskQueue:
    """单例任务队列：管理后台任务的提交、状态查询和自动清理"""

    def __init__(self, max_workers: int = MAX_CONCURRENT):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks: dict[str, dict] = {}
        self._lock = __import__("threading").Lock()
        self._cleanup_started = False

    def submit_task(self, name: str, func: Callable, *args, **kwargs) -> str:
        """提交后台任务，返回 task_id"""
        task_id = f"{name}-{uuid.uuid4().hex[:8]}"
        with self._lock:
            self._tasks[task_id] = {
                "name": name,
                "status": PENDING,
                "total": 0,
                "processed": 0,
                "success": 0,
                "fail": 0,
                "result": None,
                "error": None,
                "created_at": time.time(),
            }

        future = self._executor.submit(self._run_wrapper, task_id, func, *args, **kwargs)
        future.add_done_callback(lambda f: self._on_complete(task_id, f))

        self._maybe_start_cleanup()
        logger.info(f"任务已提交: {task_id}")
        return task_id

    def _run_wrapper(self, task_id: str, func: Callable, *args, **kwargs):
        """包装执行函数，更新状态为 running"""
        with self._lock:
            self._tasks[task_id]["status"] = RUNNING
        return func(task_id, *args, **kwargs)

    def _on_complete(self, task_id: str, future):
        """任务完成回调"""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return
            exc = future.exception()
            if exc:
                task["status"] = ERROR
                task["error"] = str(exc)
                logger.error(f"任务失败: {task_id}: {exc}")
            elif task["status"] not in (DONE, ERROR):
                task["status"] = DONE

    def get_task_status(self, task_id: str) -> dict | None:
        """查询任务状态"""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None
            return dict(task)

    def update_task(self, task_id: str, **updates):
        """后台任务内部调用：更新进度"""
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id].update(updates)

    def _maybe_start_cleanup(self):
        """启动自动清理协程（仅启动一次）"""
        if self._cleanup_started:
            return
        self._cleanup_started = True
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self._cleanup_loop())
        except RuntimeError:
            # 没有事件循环时跳过，任务会在下次 submit 时重试
            self._cleanup_started = False

    async def _cleanup_loop(self):
        """定期清理过期任务"""
        while True:
            await asyncio.sleep(300)  # 每 5 分钟清理一次
            now = time.time()
            with self._lock:
                expired = [
                    tid for tid, t in self._tasks.items()
                    if t["status"] in (DONE, ERROR) and now - t["created_at"] > TASK_TTL_SECONDS
                ]
                for tid in expired:
                    del self._tasks[tid]
            if expired:
                logger.info(f"已清理 {len(expired)} 个过期任务")


# 全局单例
task_queue = TaskQueue()
