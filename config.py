import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///ecommerce.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "default-key-change-me")
    STRIPE_TEST_KEY = os.getenv("STRIPE_TEST_KEY", "pk_test_mock")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_mock")
    MOCK_PAYMENT_MODE = os.getenv("MOCK_PAYMENT_MODE", "always_succeed")
    MOCK_FAILURE_RATE = float(os.getenv("MOCK_FAILURE_RATE", "0.0"))
    MOCK_PROCESSING_DELAY = float(os.getenv("MOCK_PROCESSING_DELAY", "0.5"))
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    SSL_CERT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ssl", "cert.pem")
    SSL_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ssl", "key.pem")
    SSL_ENABLED = os.path.exists(SSL_CERT_FILE) and os.path.exists(SSL_KEY_FILE)
    SESSION_COOKIE_SECURE = SSL_ENABLED or os.getenv("FLASK_ENV") == "production"
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123456")
    SECURITY_HEADERS_ENABLED = os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true"

    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM = os.getenv("MAIL_FROM", "noreply@smarttrade.africa")
    MAIL_TO = os.getenv("MAIL_TO", "support@smarttrade.africa")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    HOST = os.getenv("HOST", "127.0.0.1")

    # Auth0
    AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "")
    AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID", "")
    AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET", "")
    AUTH0_SECRET = os.getenv("AUTH0_SECRET", "")
    AUTH0_REDIRECT_URI = os.getenv("AUTH0_REDIRECT_URI", "http://localhost:5000/auth0/callback")
