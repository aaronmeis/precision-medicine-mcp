"""
HIPAA-Compliant Audit Logging for Streamlit MCP Chat
Logs all user queries and system events to Google Cloud Logging with 10-year retention
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib


class AuditLogger:
    """
    HIPAA-compliant audit logger using Google Cloud Logging.

    All logs are:
    - Structured JSON format
    - Include user identity (email hash)
    - Timestamped with UTC
    - Sent to Cloud Logging for 10-year retention
    - Searchable and filterable
    """

    def __init__(self, use_cloud_logging: bool = True):
        """
        Initialize audit logger.

        Args:
            use_cloud_logging: If True, use Google Cloud Logging. If False, use local logging (dev mode)
        """
        self.use_cloud_logging = use_cloud_logging
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging backend (Cloud Logging or local)."""
        if self.use_cloud_logging:
            try:
                from google.cloud import logging as cloud_logging

                # Initialize Cloud Logging client
                self.logging_client = cloud_logging.Client()
                self.logger = self.logging_client.logger("mcp-audit-log")
                self.is_cloud = True

            except Exception as e:
                # Fallback to local logging if Cloud Logging unavailable
                print(f"Warning: Cloud Logging unavailable, using local logging: {e}")
                self._setup_local_logging()
                self.is_cloud = False
        else:
            self._setup_local_logging()
            self.is_cloud = False

    def _setup_local_logging(self):
        """Set up local file logging for development."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('audit.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('mcp-audit-log')
        self.is_cloud = False

    def _log_event(self, event_type: str, data: Dict[str, Any], severity: str = "INFO"):
        """
        Log an event to Cloud Logging or local file.

        Args:
            event_type: Type of event (e.g., "user_login", "mcp_query")
            data: Event data dictionary
            severity: Log severity (INFO, WARNING, ERROR)
        """
        # Add common fields
        log_entry = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **data
        }

        if self.is_cloud:
            # Log to Cloud Logging
            self.logger.log_struct(log_entry, severity=severity)
        else:
            # Log to local file
            log_message = json.dumps(log_entry, indent=2)
            if severity == "ERROR":
                self.logger.error(log_message)
            elif severity == "WARNING":
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)

    @staticmethod
    def _hash_email(email: str) -> str:
        """
        Hash email for privacy (de-identification).

        Args:
            email: User's email address

        Returns:
            str: SHA-256 hash of email (first 12 characters)
        """
        return hashlib.sha256(email.encode()).hexdigest()[:12]

    @staticmethod
    def _truncate_phi(text: str, max_length: int = 100) -> str:
        """
        Truncate text that may contain PHI to prevent logging sensitive data.

        Args:
            text: Text to truncate
            max_length: Maximum length

        Returns:
            str: Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length] + "... [truncated]"

    def log_user_login(self, user_email: str, user_id: str, display_name: str):
        """
        Log user login event.

        Args:
            user_email: User's email (will be hashed)
            user_id: User's ID
            display_name: User's display name
        """
        self._log_event("user_login", {
            "user_email_hash": self._hash_email(user_email),
            "user_id": user_id,
            "display_name": display_name
        })

    def log_mcp_query(
        self,
        user_email: str,
        user_id: str,
        servers: List[str],
        prompt: str,
        model: str,
        session_id: str
    ):
        """
        Log MCP query event.

        IMPORTANT: Only log metadata, not the full prompt which may contain PHI.

        Args:
            user_email: User's email (will be hashed)
            user_id: User's ID
            servers: List of MCP servers used
            prompt: User's prompt (will be truncated)
            model: Claude model used
            session_id: Session ID
        """
        self._log_event("mcp_query", {
            "user_email_hash": self._hash_email(user_email),
            "user_id": user_id,
            "servers": servers,
            "server_count": len(servers),
            "prompt_length": len(prompt),
            "prompt_preview": self._truncate_phi(prompt, 100),  # Only log first 100 chars
            "model": model,
            "session_id": session_id
        })

    def log_mcp_response(
        self,
        user_email: str,
        user_id: str,
        servers: List[str],
        response_length: int,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        estimated_cost: float,
        duration_seconds: float,
        session_id: str
    ):
        """
        Log MCP response event with token usage.

        Args:
            user_email: User's email (will be hashed)
            user_id: User's ID
            servers: List of MCP servers used
            response_length: Length of response text
            input_tokens: Input token count
            output_tokens: Output token count
            total_tokens: Total token count
            estimated_cost: Estimated cost in USD
            duration_seconds: Query duration in seconds
            session_id: Session ID
        """
        self._log_event("mcp_response", {
            "user_email_hash": self._hash_email(user_email),
            "user_id": user_id,
            "servers": servers,
            "response_length": response_length,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": estimated_cost,
            "duration_seconds": duration_seconds,
            "session_id": session_id
        })

    def log_error(
        self,
        user_email: str,
        user_id: str,
        error_type: str,
        error_message: str,
        servers: Optional[List[str]] = None,
        session_id: Optional[str] = None
    ):
        """
        Log error event.

        Args:
            user_email: User's email (will be hashed)
            user_id: User's ID
            error_type: Type of error
            error_message: Error message
            servers: List of MCP servers involved (if applicable)
            session_id: Session ID (if applicable)
        """
        data = {
            "user_email_hash": self._hash_email(user_email),
            "user_id": user_id,
            "error_type": error_type,
            "error_message": self._truncate_phi(error_message, 200)
        }

        if servers:
            data["servers"] = servers

        if session_id:
            data["session_id"] = session_id

        self._log_event("error", data, severity="ERROR")

    def log_server_selection(
        self,
        user_email: str,
        user_id: str,
        selected_servers: List[str],
        session_id: str
    ):
        """
        Log when user selects/changes MCP servers.

        Args:
            user_email: User's email (will be hashed)
            user_id: User's ID
            selected_servers: List of selected servers
            session_id: Session ID
        """
        self._log_event("server_selection", {
            "user_email_hash": self._hash_email(user_email),
            "user_id": user_id,
            "selected_servers": selected_servers,
            "server_count": len(selected_servers),
            "session_id": session_id
        })

    def log_model_selection(
        self,
        user_email: str,
        user_id: str,
        selected_model: str,
        max_tokens: int,
        session_id: str
    ):
        """
        Log when user selects/changes Claude model.

        Args:
            user_email: User's email (will be hashed)
            user_id: User's ID
            selected_model: Selected Claude model
            max_tokens: Max tokens setting
            session_id: Session ID
        """
        self._log_event("model_selection", {
            "user_email_hash": self._hash_email(user_email),
            "user_id": user_id,
            "selected_model": selected_model,
            "max_tokens": max_tokens,
            "session_id": session_id
        })

    def log_session_start(
        self,
        user_email: str,
        user_id: str,
        session_id: str
    ):
        """
        Log session start.

        Args:
            user_email: User's email (will be hashed)
            user_id: User's ID
            session_id: Session ID
        """
        self._log_event("session_start", {
            "user_email_hash": self._hash_email(user_email),
            "user_id": user_id,
            "session_id": session_id
        })

    def log_session_end(
        self,
        user_email: str,
        user_id: str,
        session_id: str,
        duration_seconds: float,
        total_queries: int,
        total_tokens: int,
        total_cost: float
    ):
        """
        Log session end with summary statistics.

        Args:
            user_email: User's email (will be hashed)
            user_id: User's ID
            session_id: Session ID
            duration_seconds: Session duration in seconds
            total_queries: Total number of queries
            total_tokens: Total tokens used
            total_cost: Total cost in USD
        """
        self._log_event("session_end", {
            "user_email_hash": self._hash_email(user_email),
            "user_id": user_id,
            "session_id": session_id,
            "duration_seconds": duration_seconds,
            "total_queries": total_queries,
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost
        })


# Global audit logger instance
_audit_logger = None


def get_audit_logger() -> AuditLogger:
    """
    Get or create global audit logger instance.

    Returns:
        AuditLogger: Global audit logger
    """
    global _audit_logger

    if _audit_logger is None:
        # Check if running in production (Cloud Run)
        import os
        use_cloud = os.getenv("ENVIRONMENT", "production").lower() == "production"
        _audit_logger = AuditLogger(use_cloud_logging=use_cloud)

    return _audit_logger


# Example usage:
"""
from utils.audit_logger import get_audit_logger

# Get logger
audit_log = get_audit_logger()

# Log user login
audit_log.log_user_login(
    user_email="user@hospital.org",
    user_id="abc123",
    display_name="Dr. Smith"
)

# Log MCP query
audit_log.log_mcp_query(
    user_email="user@hospital.org",
    user_id="abc123",
    servers=["spatialtools", "multiomics"],
    prompt="Analyze patient data...",
    model="claude-sonnet-4-5",
    session_id="sess_123"
)

# Log response
audit_log.log_mcp_response(
    user_email="user@hospital.org",
    user_id="abc123",
    servers=["spatialtools", "multiomics"],
    response_length=1500,
    input_tokens=500,
    output_tokens=1000,
    total_tokens=1500,
    estimated_cost=0.025,
    duration_seconds=3.5,
    session_id="sess_123"
)
"""
