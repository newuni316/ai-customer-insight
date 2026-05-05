"""自定义异常类 + 全局异常处理器"""
from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """应用异常基类"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, status_code=404)


class ValidationError(AppError):
    def __init__(self, message: str = "请求参数无效"):
        super().__init__(message, status_code=422)


class AuthenticationError(AppError):
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, status_code=401)


class RateLimitError(AppError):
    def __init__(self, message: str = "请求过于频繁"):
        super().__init__(message, status_code=429)


def _error_response(message: str, status_code: int, request: Request) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": message, "path": str(request.url.path)},
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return _error_response(exc.message, exc.status_code, request)


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    # 不暴露内部错误细节
    return _error_response("服务器内部错误", 500, request)


def register_exception_handlers(app):
    """注册全局异常处理器"""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)
