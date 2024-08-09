from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


# load_dotenv()
BASE_DIR = Path(__file__).parent.parent
load_dotenv(dotenv_path=BASE_DIR/".env-dev")

class DbSettings(BaseModel):
    username: str = os.getenv("DATABASE_USER")
    password: str = os.getenv("DATABASE_PASSWORD")
    host: str = os.getenv("DATABASE_HOST")
    name: str = os.getenv("DATABASE_NAME")
    echo: bool = False

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}/{self.name}"


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / os.getenv("JWT_PRIVATE_KEY_PATH")
    public_key_path: Path = BASE_DIR / os.getenv("JWT_PUBLIC_KEY_PATH")
    algorithm: str = os.getenv("JWT_ALGORITHM")
    access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))
    refresh_token_expire_days: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS"))


class AWS_Settings(BaseSettings):
    AWS_DEFAULT_REGION: str = os.getenv("AWS_DEFAULT_REGION")
    AWS_BUCKET_NAME: str = os.getenv("AWS_BUCKET_NAME")
    AWS_SPLITS_PATH: str = os.getenv("SPLITS_PATH")
    AWS_ROUTES_PATH: str = os.getenv("ROUTES_PATH")
    AWS_RESULTS_PATH: str = os.getenv("RESULTS_PATH")

class Settings(BaseSettings):
    api_v1_prefix: str = os.getenv("API_V1_PREFIX")
    db: DbSettings = DbSettings()
    auth_jwt: AuthJWT = AuthJWT()
    aws: AWS_Settings = AWS_Settings()




settings = Settings()
