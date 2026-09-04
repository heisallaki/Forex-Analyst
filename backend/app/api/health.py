from fastapi import APIRouter, Request

from app.core.system_state import get_last_tick_at, seconds_since_last_tick

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check(request: Request) -> dict:
    stream_task = getattr(request.app.state, "stream_task", None)
    monitor_task = getattr(request.app.state, "monitor_task", None)
    last_tick_at = get_last_tick_at()

    return {
        "status": "ok",
        "market_stream_task_running": stream_task is not None and not stream_task.done(),
        "position_monitor_task_running": monitor_task is not None and not monitor_task.done(),
        "last_tick_at": last_tick_at.isoformat() if last_tick_at else None,
        "seconds_since_last_tick": seconds_since_last_tick(),
    }