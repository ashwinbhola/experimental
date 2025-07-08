from datetime import timedelta
import os

from dotenv import load_dotenv
from redis import Redis


load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = Redis(host="127.0.0.1", port=6379)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30) 
    SESSION_COOKIE_NAME = "session_cookie"