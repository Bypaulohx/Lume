"""
Session management for Lume V2.0
Handles HTTP connections with proper pooling and timeout management
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional


def build_session(
    timeout: float = 10.0,
    verify_tls: bool = True,
    user_agent: str = "Lume/2.0 (+https://github.com/lume-security/lume)",
    max_retries: int = 2,
    pool_connections: int = 10,
    pool_maxsize: int = 10,
) -> requests.Session:
    """
    Build a requests Session with proper connection pooling and retry strategy.
    
    Args:
        timeout: Request timeout in seconds
        verify_tls: Whether to verify TLS certificates
        user_agent: User-Agent header
        max_retries: Maximum retries for failed connections
        pool_connections: Number of connection pools
        pool_maxsize: Maximum size of connection pool
        
    Returns:
        Configured requests.Session instance
    """
    
    session = requests.Session()
    
    # Set headers
    session.headers.update({
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    
    # TLS verification
    session.verify = verify_tls
    
    # Timeout
    session.timeout = timeout
    
    # Retry strategy
    retry_strategy = Retry(
        total=max_retries,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
    )
    
    # HTTP Adapter with connection pooling
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=pool_connections,
        pool_maxsize=pool_maxsize,
        pool_block=False
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


class SessionManager:
    """Manages multiple sessions for concurrent operations"""
    
    def __init__(self, session_count: int = 4, **session_kwargs):
        """
        Initialize SessionManager.
        
        Args:
            session_count: Number of sessions to maintain
            **session_kwargs: Keyword arguments passed to build_session
        """
        self.sessions = [build_session(**session_kwargs) for _ in range(session_count)]
        self._current = 0
    
    def get(self) -> requests.Session:
        """Get next available session (round-robin)"""
        session = self.sessions[self._current]
        self._current = (self._current + 1) % len(self.sessions)
        return session
    
    def close_all(self):
        """Close all sessions"""
        for session in self.sessions:
            session.close()
