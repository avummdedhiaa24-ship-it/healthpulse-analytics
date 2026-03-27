import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    PROJECT_NAME = "HealthPulse API"
    ENV = os.getenv("ENV", "development")


settings = Settings()
