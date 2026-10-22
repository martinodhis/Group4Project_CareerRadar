import os

from dotenv import load_dotenv

load_dotenv()

database_uri = (
    os.getenv("DATABASE_URI")
    or os.getenv("DATABASE_URL")
    or "postgresql://localhost/careerradar"
)
if database_uri.startswith("postgres://"):
    database_uri = database_uri.replace("postgres://", "postgresql://", 1)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    SQLALCHEMY_DATABASE_URI = database_uri

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    JWT_DECODE_LEEWAY = 60

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
