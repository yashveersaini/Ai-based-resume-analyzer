import os
from functools import wraps

from clerk_backend_api import Clerk, authenticate_request
from clerk_backend_api.security.types import AuthenticateRequestOptions
from flask import current_app, g, jsonify, redirect, request, session, url_for

from utils.database import get_or_create_user_from_clerk


def _env_csv(key: str) -> list[str]:
    raw = os.environ.get(key)
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def _auth_options() -> AuthenticateRequestOptions:
    parties = current_app.config.get("CLERK_AUTHORIZED_PARTIES") or None
    return AuthenticateRequestOptions(
        secret_key=current_app.config["CLERK_SECRET_KEY"],
        jwt_key=current_app.config.get("CLERK_JWT_KEY"),
        authorized_parties=parties,
        accepts_token=["session_token"],
    )


def authenticate_clerk_request():
    return authenticate_request(request, _auth_options())


def _clerk_user_profile(clerk_user_id: str) -> tuple[str, str]:
    clerk = Clerk(bearer_auth=current_app.config["CLERK_SECRET_KEY"])
    clerk_user = clerk.users.get(user_id=clerk_user_id)
    if clerk_user is None:
        raise ValueError(f"Clerk user not found: {clerk_user_id}")

    email = ""
    if clerk_user.email_addresses:
        primary_id = clerk_user.primary_email_address_id
        primary = None
        if primary_id:
            primary = next(
                (entry for entry in clerk_user.email_addresses if entry.id == primary_id),
                None,
            )
        email = (primary or clerk_user.email_addresses[0]).email_address

    name_parts = [clerk_user.first_name or "", clerk_user.last_name or ""]
    name = " ".join(part for part in name_parts if part).strip()
    if not name and clerk_user.username:
        name = clerk_user.username
    if not name:
        name = email.split("@")[0] if email else "User"

    return name, email


def _set_session_user(user: dict) -> int:
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["user_email"] = user["email"]
    return user["id"]


def resolve_session_user() -> int | None:
    """Resolve the local DB user from Flask session or Clerk session token."""
    if "user_id" in session:
        return session["user_id"]

    state = authenticate_clerk_request()
    if not state.is_signed_in:
        return None

    clerk_user_id = state.payload["sub"]

    try:
        name, email = _clerk_user_profile(clerk_user_id)
    except Exception as exc:
        print(f"Failed to fetch Clerk user: {exc}")
        return None

    user = get_or_create_user_from_clerk(clerk_user_id, name, email)
    if user is None:
        return None

    return _set_session_user(user)


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user_id = resolve_session_user()
        if user_id is None:
            return jsonify({"error": "Authentication required"}), 401
        g.user_id = user_id
        return view(*args, **kwargs)

    return wrapper


def page_login_required():
    """For HTML page routes. Returns a redirect if the user is not authenticated."""
    if resolve_session_user() is None:
        return redirect(url_for("login_page"))
    return None


def init_clerk_config(app) -> None:
    app.config["CLERK_SECRET_KEY"] = os.getenv("CLERK_SECRET_KEY")
    app.config["CLERK_JWT_KEY"] = os.getenv("CLERK_JWT_KEY")
    app.config["CLERK_AUTHORIZED_PARTIES"] = _env_csv("CLERK_AUTHORIZED_PARTIES")
