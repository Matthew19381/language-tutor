import logging
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/settings/gdrive/auth")
async def gdrive_auth():
    """Return Google Drive OAuth2 authorization URL."""
    try:
        from backend.services.google_drive_service import get_auth_url, is_authorized
        if is_authorized():
            return {"authorized": True, "message": "Google Drive already authorized"}
        url = get_auth_url()
        return {"authorized": False, "auth_url": url}
    except FileNotFoundError:
        return {
            "authorized": False,
            "auth_url": None,
            "error": "gdrive_credentials.json not found. Download OAuth2 credentials from Google Cloud Console and save as backend/gdrive_credentials.json"
        }
    except Exception as e:
        logger.error(f"Error getting GDrive auth URL: {e}")
        return {"authorized": False, "auth_url": None, "error": str(e)}


@router.get("/api/settings/gdrive/callback")
async def gdrive_callback(code: str):
    """Handle Google Drive OAuth2 callback and save token."""
    try:
        from backend.services.google_drive_service import save_token_from_code
        success = save_token_from_code(code)
        if success:
            return {"success": True, "message": "Google Drive authorized successfully! You can now upload Obsidian exports."}
        return {"success": False, "message": "Failed to save authorization token"}
    except Exception as e:
        logger.error(f"GDrive callback error: {e}")
        return {"success": False, "message": str(e)}


@router.get("/api/settings/gdrive/status")
async def gdrive_status():
    """Check if Google Drive is authorized."""
    try:
        from backend.services.google_drive_service import is_authorized
        return {"authorized": is_authorized()}
    except Exception:
        return {"authorized": False}
