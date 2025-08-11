import socketio
from app.core.auth.permission_checker import PermissionChecker
from app.core.auth.session_manager import SessionManager
from app.utils.logging import create_logger
from functools import wraps
from typing import Callable, Any

logger = create_logger(__name__)

def create_auth_decorators(session_manager:SessionManager, sio:socketio.AsyncServer):
    """Factory function that returns decorators with injected dependencies"""

    def require_permission(permission: str):
        """Decorator to check permissions before executing event handler"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(sid: str, *args, **kwargs) -> Any:
                session = await session_manager.get_session(sid)
                if not session:
                    logger.warning(f"Session not found for sid: {sid}")
                    await sio.emit('error', {'message': 'Session not found'}, room=sid)
                    return

                if not PermissionChecker.has_permission(session, permission):
                    logger.warning(f"Permission denied for sid: {sid}, permission: {permission}")
                    await sio.emit('error', {'message': 'Permission denied'}, room=sid)
                    return

                await session_manager.update_session_activity(sid)
                logger.debug(f"Executing {func.__name__} for sid: {sid} with session: {session}")
                return await func(sid, session, *args, **kwargs)
            return wrapper
        return decorator

    def require_role(role: str):
        """Decorator to check roles before executing event handler"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(sid: str, *args, **kwargs) -> Any:
                session = await session_manager.get_session(sid)
                if not session:
                    logger.warning(f"Session not found for sid: {sid}")
                    await sio.emit('error', {'message': 'Session not found'}, room=sid)
                    return

                if not PermissionChecker.has_role(session, role):
                    logger.warning(f"Role {role} required for sid: {sid}")
                    await sio.emit('error', {'message': 'Role required'}, room=sid)
                    return

                await session_manager.update_session_activity(sid)
                logger.debug(f"Executing {func.__name__} for sid: {sid} with session: {session}")
                return await func(sid, session, *args, **kwargs)
            return wrapper
        return decorator

    def authenticated_only(func: Callable) -> Callable:
        """Decorator to ensure user is authenticated"""
        @wraps(func)
        async def wrapper(sid: str, *args, **kwargs) -> Any:
            session = await session_manager.get_session(sid)
            if not session:
                await sio.emit('error', {'message': 'Authentication required'}, room=sid)
                return

            await session_manager.update_session_activity(sid)
            return await func(sid, session, *args, **kwargs)
        return wrapper

    return {
        'require_permission': require_permission,
        'require_role': require_role,
        'authenticated_only': authenticated_only
    }
