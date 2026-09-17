"""Production WSGI entry point; load settings before importing the app factory."""
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / '.env')

from app import create_app

application = create_app()
