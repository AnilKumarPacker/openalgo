import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def load_environment():
    """
    Load environment variables safely.
    - In local: loads from .env
    - In cloud (Render): skips .env and uses system env vars
    """

    env_path = Path(".env")

    if env_path.exists():
        if load_dotenv:
            load_dotenv(dotenv_path=env_path)
            print("✅ .env file loaded successfully")
        else:
            print("⚠️ python-dotenv not installed, skipping .env loading")
    else:
        print("⚠️ .env file not found. Using system environment variables (expected in cloud).")


def validate_required_vars(required_vars=None):
    """
    Validate required environment variables.
    Does NOT crash — only warns.
    """

    if not required_vars:
        return True

    missing = []

    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print("⚠️ Missing environment variables:")
        for var in missing:
            print(f"   - {var}")
        return False

    print("✅ All required environment variables are set")
    return True


# Auto-run when imported (optional)
load_environment()

# Example usage (customize based on your project)
REQUIRED_VARS = [
    # Add only critical ones
    # "API_KEY",
    # "DB_URL",
]

validate_required_vars(REQUIRED_VARS)