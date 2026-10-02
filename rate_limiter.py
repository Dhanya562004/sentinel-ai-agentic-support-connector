"""
SentinelAI - Rate Limiting & Request Control Engine
Controls session usage and prevents abuse by enforcing request quotas.
"""

import time
from typing import Dict, Tuple, Any

class RateLimiter:
    """Session-based rate limiter enforcing request quotas."""

    def __init__(self, max_requests: int = 5, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # session_id -> list of timestamps
        self._session_history: Dict[str, list] = {}

    def is_allowed(self, session_id: str = "default") -> Tuple[bool, str, int]:
        """
        Checks whether the session is allowed to make a request.
        Returns: (is_allowed: bool, message: str, remaining_requests: int)
        """
        now = time.time()
        timestamps = self._session_history.get(session_id, [])

        # Filter out timestamps outside the sliding window
        valid_timestamps = [t for t in timestamps if (now - t) < self.window_seconds]
        self._session_history[session_id] = valid_timestamps

        remaining = self.max_requests - len(valid_timestamps)

        if len(valid_timestamps) >= self.max_requests:
            return (
                False, 
                f"Rate limit exceeded! Maximum {self.max_requests} requests allowed per session. Please wait or reset limit.",
                0
            )

        return (True, "Request within allowed limit.", remaining)

    def record_request(self, session_id: str = "default") -> int:
        """Records a request timestamp for the session. Returns remaining requests."""
        now = time.time()
        if session_id not in self._session_history:
            self._session_history[session_id] = []
        
        self._session_history[session_id].append(now)
        _, _, remaining = self.is_allowed(session_id)
        return remaining

    def reset_limit(self, session_id: str = "default"):
        """Resets the request count for a given session."""
        self._session_history[session_id] = []

    def get_remaining(self, session_id: str = "default") -> int:
        """Gets remaining allowed requests for a session."""
        _, _, remaining = self.is_allowed(session_id)
        return max(0, remaining)


if __name__ == "__main__":
    limiter = RateLimiter(max_requests=5)
    sid = "test_user"
    for i in range(6):
        allowed, msg, rem = limiter.is_allowed(sid)
        print(f"Request #{i+1}: Allowed={allowed}, Remaining={rem}, Message='{msg}'")
        if allowed:
            limiter.record_request(sid)
