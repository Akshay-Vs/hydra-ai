from clerk_backend_api import User
from app.core.auth.user_session import UserSession
from app.utils.logging import create_logger
from typing import Dict, Set, Any
from fastapi import HTTPException
from datetime import datetime
import asyncio

logger = create_logger(__name__)


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}  # sid -> UserSession
        self.user_sessions: Dict[str, Set[str]] = {}  # user_id -> set of sids
        self.org_rooms: Dict[str, Set[str]] = {}  # org_id -> set of sids
        self.custom_rooms: Dict[str, Set[str]] = {}  # room_name -> set of sids
        self._lock = asyncio.Lock()

    def _get_required_field(
        self, payload: Dict[str, Any], field: str, field_name: str
    ) -> str:
        """Get required field from payload or raise HTTPException"""
        value = payload.get(field)
        if not value:
            raise HTTPException(
                status_code=401, detail=f"Unauthorized: Missing {field_name}"
            )
        return str(value)

    async def create_session(self, sid, user: User) -> UserSession:
        async with self._lock:
            user_session = UserSession(
                user_id=user.id,
                username=user.username,
                email=user.email_addresses,
                org_id="NOT_IMPLEMENTED",  #! Placeholder, org_id should be set properly
                roles= ["user"],  #! Placeholder, roles should be set properly
                permissions= {'read', 'chat'},  #! Placeholder, permissions should be set properly
                connected_at=datetime.now(),
                last_activity=datetime.now(),
            )

        self.sessions[sid] = user_session

        # Track user sessions
        logger.debug(f"Creating session {sid} for user {user_session.username}")
        if user_session.user_id not in self.user_sessions:
            self.user_sessions[user_session.user_id] = set()
        self.user_sessions[user_session.user_id].add(sid)

        # Track organization rooms
        logger.debug(f"Adding session {sid} to organization {user_session.org_id}")
        if user_session.org_id not in self.org_rooms:
            self.org_rooms[user_session.org_id] = set()
        self.org_rooms[user_session.org_id].add(sid)

        logger.info(
            f"Session created for user {user_session.username} (ID: {user_session.user_id})"
        )
        return user_session

    async def get_session(self, sid: str) -> UserSession:
        async with self._lock:
            session = self.sessions.get(sid)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            return session

    async def delete_session(self, sid: str) -> None:
        async with self._lock:
            if sid not in self.sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            user_session = self.sessions.pop(sid)

            # Remove from user sessions tracking
            logger.debug(
                f"Deleting session {sid} for user {user_session.username} (ID: {user_session.user_id})"
            )
            if user_session.user_id in self.user_sessions:
                self.user_sessions[user_session.user_id].discard(sid)
                if not self.user_sessions[user_session.user_id]:
                    del self.user_sessions[user_session.user_id]

            # Remove from organization rooms tracking
            logger.debug(
                f"Removing session {sid} from organization {user_session.org_id}"
            )
            if user_session.org_id in self.org_rooms:
                self.org_rooms[user_session.org_id].discard(sid)
                if not self.org_rooms[user_session.org_id]:
                    del self.org_rooms[user_session.org_id]

            # Remove from custom rooms tracking
            logger.debug(f"Removing session {sid} from custom rooms")
            for room_name, sids in self.custom_rooms.items():
                if sid in sids:
                    sids.discard(sid)
                    if not sids:
                        del self.custom_rooms[room_name]

            del self.sessions[sid]

            logger.info(
                f"Session {sid} deleted for user {user_session.username} (ID: {user_session.user_id})"
            )

    async def join_room(self, sid: str, room_name: str) -> None:
        async with self._lock:
            if sid not in self.sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            if room_name not in self.custom_rooms:
                self.custom_rooms[room_name] = set()
            self.custom_rooms[room_name].add(sid)

            logger.debug(f"Session {sid} joined room {room_name}")

    async def leave_room(self, sid: str, room_name: str) -> None:
        async with self._lock:
            if sid not in self.sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            if room_name in self.custom_rooms and sid in self.custom_rooms[room_name]:
                self.custom_rooms[room_name].discard(sid)
                if not self.custom_rooms[room_name]:
                    del self.custom_rooms[room_name]

                logger.debug(f"Session {sid} left room {room_name}")
            else:
                raise HTTPException(status_code=404, detail="Room not found")

    async def get_org_members(self, org_id: str) -> Set[str]:
        return self.org_rooms.get(org_id, set()).copy()

    async def get_user_sessions(self, user_id: str) -> Set[str]:
        return self.user_sessions.get(user_id, set()).copy()

    async def update_session_activity(self, sid: str) -> None:
        if sid in self.sessions:
            self.sessions[sid].last_activity = datetime.now()
