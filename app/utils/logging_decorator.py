import logging
import functools
import time
import asyncio
from typing import Iterable, Any
from app.config.logging_config import get_logger

DEFAULT_REDACT = {"password", "token", "api_key", "secret", "authorization", "session"}


def _safe_repr(value: Any, max_len: int = 300):
    try:
        s = repr(value)
    except Exception:
        return "<unreprable>"
    if len(s) > max_len:
        return s[:max_len] + "...(truncated)"
    return s


def _redact_kwargs(kwargs: dict, redact_keys: Iterable[str]):
    redacted = {}
    for k, v in kwargs.items():
        if any(r in k.lower() for r in redact_keys):
            redacted[k] = "<REDACTED>"
        else:
            redacted[k] = _safe_repr(v)
    return redacted


def log_call(logger: str | logging.Logger | None = None,
             level: int = logging.INFO,
             log_args: bool = True,
             log_result: bool = False,
             redact: Iterable[str] | None = None,
             timed: bool = True):
    """Decorator to log function entry/exit for sync and async functions.

    Use for database fetch and registration functions. Keep logging of sensitive
    fields disabled via redaction.
    """
    if redact is None:
        redact = DEFAULT_REDACT

    def decorator(fn):
        chosen_logger = None
        if isinstance(logger, str):
            chosen_logger = get_logger(logger)

        is_coro = asyncio.iscoroutinefunction(fn)

        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs):
            nonlocal chosen_logger
            if chosen_logger is None:
                chosen_logger = get_logger(fn.__module__)

            start = time.time() if timed else None
            try:
                if log_args:
                    try:
                        rkwargs = _redact_kwargs(kwargs, redact)
                        chosen_logger.log(level, f"CALL {fn.__qualname__} args={[_safe_repr(a) for a in args]} kwargs={rkwargs}")
                    except Exception:
                        chosen_logger.log(level, f"CALL {fn.__qualname__} (args hidden)")
                else:
                    chosen_logger.log(level, f"CALL {fn.__qualname__}")

                result = await fn(*args, **kwargs)

                if log_result:
                    chosen_logger.log(level, f"RETURN {fn.__qualname__} -> {_safe_repr(result)}")
                if timed:
                    chosen_logger.log(level, f"DONE {fn.__qualname__} in {time.time()-start:.3f}s")
                return result
            except Exception:
                chosen_logger.exception(f"EXCEPTION in {fn.__qualname__}")
                raise

        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):
            nonlocal chosen_logger
            if chosen_logger is None:
                chosen_logger = get_logger(fn.__module__)

            start = time.time() if timed else None
            try:
                if log_args:
                    try:
                        rkwargs = _redact_kwargs(kwargs, redact)
                        chosen_logger.log(level, f"CALL {fn.__qualname__} args={[_safe_repr(a) for a in args]} kwargs={rkwargs}")
                    except Exception:
                        chosen_logger.log(level, f"CALL {fn.__qualname__} (args hidden)")
                else:
                    chosen_logger.log(level, f"CALL {fn.__qualname__}")

                result = fn(*args, **kwargs)

                if log_result:
                    chosen_logger.log(level, f"RETURN {fn.__qualname__} -> {_safe_repr(result)}")
                if timed:
                    chosen_logger.log(level, f"DONE {fn.__qualname__} in {time.time()-start:.3f}s")
                return result
            except Exception:
                chosen_logger.exception(f"EXCEPTION in {fn.__qualname__}")
                raise

        return async_wrapper if is_coro else sync_wrapper

    return decorator
