"""
本地模型推理服务 - 支持离线环境运行

支持方式:
1. llama-cpp-python: GGUF 格式本地模型
2. HuggingFace Transformers: 本地预训练模型
3. Ollama: 本地模型服务

使用方式:
  在 .env 中设置:
  USE_LOCAL_MODEL=true
  LOCAL_MODEL_PATH=./models/feedback-analyzer.gguf
  LOCAL_MODEL_BACKEND=llamacpp  # llamacpp | transformers | ollama
  OLLAMA_BASE_URL=http://localhost:11434
"""
import json
import os
from config import get_settings

settings = get_settings()


class LocalAnalyzer:
    """本地模型分析器"""

    def __init__(self):
        self.backend = os.getenv("LOCAL_MODEL_BACKEND", "ollama")
        self._init_backend()

    def _init_backend(self):
        if self.backend == "ollama":
            self._init_ollama()
        elif self.backend == "llamacpp":
            self._init_llamacpp()
        elif self.backend == "transformers":
            self._init_transformers()

    def _init_ollama(self):
        """Ollama - 最简单的本地模型方案"""
        import httpx
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        self._httpx = httpx

    def _init_llamacpp(self):
        """llama-cpp-python - GGUF 格式模型"""
        try:
            from llama_cpp import Llama
            model_path = os.getenv("LOCAL_MODEL_PATH", "./models/model.gguf")
            self.llm = Llama(model_path=model_path, n_ctx=2048, n_gpu_layers=-1)
        except ImportError:
            raise ImportError("请安装: pip install llama-cpp-python")

    def _init_transformers(self):
        """HuggingFace Transformers"""
        try:
            from transformers import pipeline
            model_name = os.getenv("HF_MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")
            self.pipe = pipeline("text-generation", model=model_name, device_map="auto")
        except ImportError:
            raise ImportError("请安装: pip install transformers torch")

    def analyze(self, content: str) -> dict:
        """分析单条反馈"""
        prompt = f"""分析以下客户反馈，返回JSON:
{{"sentiment": "positive/neutral/negative", "topics": ["主题"], "confidence": 0.0-1.0}}

反馈: {content}

JSON:"""

        if self.backend == "ollama":
            resp = self._httpx.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30,
            )
            text = resp.json().get("response", "")
        elif self.backend == "llamacpp":
            output = self.llm(prompt, max_tokens=200, temperature=0.1)
            text = output["choices"][0]["text"]
        elif self.backend == "transformers":
            result = self.pipe(prompt, max_new_tokens=200, temperature=0.1)
            text = result[0]["generated_text"]
        else:
            raise ValueError(f"不支持的后端: {self.backend}")

        # 提取 JSON
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            result = json.loads(text[start:end])
            return {
                "sentiment": result.get("sentiment", "neutral"),
                "topics": result.get("topics", []),
                "confidence": float(result.get("confidence", 0.5)),
            }
        except (json.JSONDecodeError, ValueError):
            return {"sentiment": "neutral", "topics": [], "confidence": 0.0}


# 全局实例（延迟初始化）
_analyzer: LocalAnalyzer | None = None


def get_local_analyzer() -> LocalAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = LocalAnalyzer()
    return _analyzer
