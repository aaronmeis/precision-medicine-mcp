"""
SSO Authentication utilities for Streamlit UI
Extracts user information from OAuth2 Proxy headers for HIPAA-compliant user tracking
"""

import streamlit as st
from typing import Optional, Dict
import hashlib
from datetime import datetime


def get_authenticated_user() -> Optional[Dict[str, str]]:
    """
    Extract authenticated user information from OAuth2 Proxy headers.

    OAuth2 Proxy sets these headers after successful Azure AD authentication:
    - X-Forwarded-Email: User's email address
    - X-Forwarded-User: User's username
    - X-Forwarded-Preferred-Username: User's preferred username
    - X-Forwarded-Access-Token: OAuth access token (not used for security)

    Returns:
        dict: User information with keys: email, username, user_id, display_name
        None: If authentication headers are missing (should never happen in production)

    Raises:
        SystemExit: If running in production and authentication is missing
    """
    # Get OAuth2 Proxy headers from request context
    # In local development, these may not be present
    try:
        headers = st.context.headers
    except AttributeError:
        # Running in local development without OAuth2 Proxy
        return _get_development_user()

    # Extract user information from headers
    email = headers.get("X-Forwarded-Email")
    username = headers.get("X-Forwarded-User")
    preferred_username = headers.get("X-Forwarded-Preferred-Username")

    # Check if authentication headers are present
    if not email:
        # No authentication headers - check if we're in development mode
        if _is_development_mode():
            return _get_development_user()
        else:
            # Production mode - authentication is required
            st.error("🔒 Authentication Required")
            st.error("You must be logged in via Azure AD SSO to access this application.")
            st.error("Please contact your IT department if you're having trouble logging in.")
            st.stop()

    # Generate deterministic user ID from email (for audit logging)
    user_id = _generate_user_id(email)

    # Extract display name from email or use username
    display_name = _extract_display_name(email, username, preferred_username)

    return {
        "email": email,
        "username": username or email.split("@")[0],
        "preferred_username": preferred_username,
        "user_id": user_id,
        "display_name": display_name,
        "authenticated_at": datetime.utcnow().isoformat()
    }


def _is_development_mode() -> bool:
    """
    Check if running in development mode.

    Returns:
        bool: True if in development mode, False if in production
    """
    import os
    return os.getenv("ENVIRONMENT", "production").lower() in ["dev", "development", "local"]


def _get_development_user() -> Dict[str, str]:
    """
    Get mock user for local development.

    Returns:
        dict: Mock user information
    """
    import os
    dev_email = os.getenv("DEV_USER_EMAIL", "developer@localhost")

    return {
        "email": dev_email,
        "username": "developer",
        "preferred_username": "Local Developer",
        "user_id": _generate_user_id(dev_email),
        "display_name": "Local Developer (DEV MODE)",
        "authenticated_at": datetime.utcnow().isoformat()
    }


def _generate_user_id(email: str) -> str:
    """
    Generate deterministic user ID from email for audit logging.
    Uses SHA-256 hash to create a consistent identifier.

    Args:
        email: User's email address

    Returns:
        str: First 12 characters of SHA-256 hash
    """
    return hashlib.sha256(email.encode()).hexdigest()[:12]


def _extract_display_name(
    email: str,
    username: Optional[str],
    preferred_username: Optional[str]
) -> str:
    """
    Extract user's display name from available information.

    Priority:
    1. Preferred username (from Azure AD)
    2. Username
    3. Email prefix

    Args:
        email: User's email address
        username: Username from OAuth2 Proxy
        preferred_username: Preferred username from Azure AD

    Returns:
        str: Display name
    """
    if preferred_username:
        return preferred_username
    elif username:
        return username.replace(".", " ").title()
    else:
        return email.split("@")[0].replace(".", " ").title()


def display_user_info(user: Dict[str, str], location: str = "sidebar"):
    """
    Display user information in Streamlit UI.

    Args:
        user: User information dictionary
        location: Where to display ("sidebar" or "main")
    """
    display_fn = st.sidebar if location == "sidebar" else st

    with display_fn:
        st.markdown("---")
        st.markdown("### 👤 Logged In User")
        st.markdown(f"**{user['display_name']}**")
        st.caption(f"📧 {user['email']}")

        # Show development mode warning
        if _is_development_mode():
            st.warning("⚠️ Development Mode - SSO Disabled")


def require_authentication() -> Dict[str, str]:
    """
    Require authentication and return user information.
    This is the main function to use in Streamlit pages.

    Returns:
        dict: Authenticated user information

    Raises:
        SystemExit: If authentication fails in production mode
    """
    user = get_authenticated_user()

    # Store user in session state for access throughout the app
    if "user" not in st.session_state:
        st.session_state.user = user

    return user


def check_user_authorization(user: Dict[str, str], required_group: Optional[str] = None) -> bool:
    """
    Check if user is authorized to access the application.

    In the simplified hospital deployment (Phase 1), all users get same access.
    This function is a placeholder for future RBAC implementation.

    Args:
        user: User information dictionary
        required_group: Azure AD group required (not used in Phase 1)

    Returns:
        bool: True if user is authorized
    """
    # Phase 1: All authenticated users are authorized
    # Phase 2: Can check Azure AD group membership here
    return True


def logout_url() -> str:
    """
    Get the OAuth2 Proxy logout URL.

    Returns:
        str: Logout URL
    """
    # OAuth2 Proxy logout endpoint
    return "/oauth2/sign_out"


def display_logout_button():
    """Display logout button in Streamlit UI."""
    if st.sidebar.button("🚪 Logout"):
        # Redirect to OAuth2 Proxy logout
        st.markdown(
            f'<meta http-equiv="refresh" content="0; url={logout_url()}" />',
            unsafe_allow_html=True
        )


# Example usage in Streamlit app:
"""
import streamlit as st
from utils.auth import require_authentication, display_user_info, display_logout_button

# At the start of your app
st.set_page_config(page_title="MCP Chat", page_icon="💬")

# Require authentication
user = require_authentication()

# Display user info in sidebar
display_user_info(user)
display_logout_button()

# Rest of your app...
st.title("MCP Chat")
st.write(f"Welcome, {user['display_name']}!")
"""
