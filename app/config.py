from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str  # This will hold your secret key
    ALGORITHM: str = "HS256"  # This sets the default algorithm
    DATABASE_URL: str
    MY_GMAIL_SECRET_KEY_CONTACT: str  # Add this field if you need it
    POSTGRES_HOST: str = "127.0.0.1"  # Explicitly set to IPv4 loopback address
    POSTGRES_PORT: int = 5433  # Custom PostgreSQL port
    PG_PASSWORD: str  # Fixed annotation
    PG_DB: str  # Fixed annotation
    POSTGRES_USER: str  # Add this field if needed


    class Config:
        env_file = ".env"  # This allows you to load settings from a .env file
  

# Create an instance of the Settings class
settings = Settings()



# from pydantic import BaseSettings

# class Settings(BaseSettings):
#     postgres_user: str
#     pg_password: str
#     pg_db: str

#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"
#         env = {
#             'postgres_user': 'POSTGRES_USER',
#             'pg_password': 'POSTGRES_PASSWORD',
#             'pg_db': 'POSTGRES_DB',
#         }
