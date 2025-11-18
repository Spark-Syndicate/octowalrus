from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, model_validator
from typing import List, Literal, Optional, cast, get_args
from urllib.parse import urlparse
import os
import re

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
VALID_LOG_LEVELS: set[LogLevel] = set(get_args(LogLevel))

URL_REGEX = re.compile(r"^https?://")


class Settings(BaseSettings):
    # Application environment
    app_env: str = Field(
        default_factory=lambda: os.getenv("APP_ENV", "development"),
        description="Application environment (development, production, etc.)",
    )

    # CORS configuration
    cors_allow_urls: str = Field(
        default_factory=lambda: os.getenv("CORS_ALLOW_URLS", ""),
        description="Comma-separated list of allowed CORS origins",
    )

    # Logging configuration
    log_level: LogLevel = Field(
        default_factory=lambda: cast(LogLevel, os.getenv("LOG_LEVEL", "INFO")),
        description=f"Logging level ({', '.join(sorted(VALID_LOG_LEVELS))})",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> LogLevel:
        """Validate that log_level is one of the allowed values."""
        upper_v = v.upper()
        if upper_v not in VALID_LOG_LEVELS:
            raise ValueError(
                f"Invalid log_level: {v}. Must be one of: {', '.join(sorted(VALID_LOG_LEVELS))}"
            )
        return cast(LogLevel, upper_v)

    # Debugpy settings
    debugpy_enabled: bool = Field(
        default_factory=lambda: os.getenv("DEBUGPY_ENABLED", "false").lower() == "true",
        description="Enable debugpy for remote debugging",
    )
    debugpy_port: int = Field(
        default_factory=lambda: int(os.getenv("DEBUGPY_PORT", "5678")),
        description="Port for debugpy to listen on",
    )
    debugpy_wait: bool = Field(
        default_factory=lambda: os.getenv("DEBUGPY_WAIT", "false").lower() == "true",
        description="Whether debugpy should wait for a connection",
    )

    # S3-compatible storage settings
    s3_endpoint_url: str = Field(
        default_factory=lambda: os.getenv("S3_ENDPOINT_URL", ""),
        description="S3-compatible storage endpoint URL (e.g., http://octowalrus-minio:9000 or https://s3.amazonaws.com)",
    )
    s3_bucket: str = Field(
        default_factory=lambda: os.getenv("S3_BUCKET", ""),
        description="S3-compatible storage bucket name",
    )
    s3_access_key: str = Field(
        default_factory=lambda: os.getenv("S3_ACCESS_KEY")
        or os.getenv("MINIO_ROOT_USER", ""),
        description="S3-compatible storage access key (S3_ACCESS_KEY or MINIO_ROOT_USER for backward compatibility)",
    )
    s3_secret_key: str = Field(
        default_factory=lambda: os.getenv("S3_SECRET_KEY")
        or os.getenv("MINIO_ROOT_PASSWORD", ""),
        description="S3-compatible storage secret key (S3_SECRET_KEY or MINIO_ROOT_PASSWORD for backward compatibility)",
    )
    s3_external_url: str = Field(
        default_factory=lambda: os.getenv("S3_EXTERNAL_URL", ""),
        description="External URL for browser access via port forwarding (e.g., http://localhost:19000). Optional.",
    )
    s3_region: str = Field(
        default_factory=lambda: os.getenv("S3_REGION", "us-east-1"),
        description="S3 region (used for AWS S3, optional for other S3-compatible services)",
    )
    s3_upload_expiration: int = Field(
        default_factory=lambda: int(os.getenv("S3_UPLOAD_EXPIRATION", "3600")),
        description="Presigned URL expiration time in seconds (default: 1 hour)",
    )
    s3_use_ssl: Optional[bool] = Field(
        default=None,
        description="Whether to use SSL. If not set, inferred from endpoint URL scheme.",
    )

    @field_validator("s3_endpoint_url")
    @classmethod
    def validate_endpoint_url(cls, v: str) -> str:
        """Validate that endpoint URL is provided and is a valid URL."""
        if not v or not v.strip():
            raise ValueError("S3_ENDPOINT_URL must be configured")
        if not URL_REGEX.match(v):
            raise ValueError(
                f"Invalid S3_ENDPOINT_URL: {v}. Must be a valid http(s) URL."
            )
        return v.strip()

    @field_validator("s3_bucket")
    @classmethod
    def validate_bucket(cls, v: str) -> str:
        """Validate that bucket name is provided."""
        res = (v or "").strip()
        if not res:
            raise ValueError("S3_BUCKET must be configured")
        return res

    @field_validator("s3_access_key")
    @classmethod
    def validate_access_key(cls, v: str) -> str:
        """Validate that access key is provided."""
        res = (v or "").strip()
        if not res:
            raise ValueError("S3_ACCESS_KEY/MINIO_ROOT_USER must be configured")
        return res

    @field_validator("s3_secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate that secret key is provided."""
        res = (v or "").strip()
        if not res:
            raise ValueError("S3_SECRET_KEY/MINIO_ROOT_PASSWORD must be configured")
        return res

    @model_validator(mode="after")
    def infer_ssl_from_endpoint(self):
        """Infer SSL setting from endpoint URL scheme if not explicitly set."""
        if self.s3_use_ssl is None:
            if self.s3_endpoint_url:
                parsed = urlparse(self.s3_endpoint_url)
                self.s3_use_ssl = parsed.scheme == "https"
            else:
                # Default to False if endpoint URL is not set (shouldn't happen due to validation)
                self.s3_use_ssl = False
        return self

    @property
    def cors_allow_urls_list(self) -> List[str]:
        v = self.cors_allow_urls
        if not isinstance(v, str) or not v.strip():
            raise ValueError(
                "CORS_ALLOW_URLS must be a non-empty comma-separated string of URLs."
            )
        urls = [url.strip() for url in v.split(",") if url.strip()]
        if not urls:
            raise ValueError("CORS_ALLOW_URLS must contain at least one valid URL.")

        valid_urls = []
        for url in urls:
            if URL_REGEX.match(url):
                valid_urls.append(url)
            else:
                raise ValueError(
                    f"Invalid CORS origin: {url}. Must be a valid http(s) URL."
                )
        if not valid_urls:
            raise ValueError("CORS_ALLOW_URLS must contain at least one valid URL.")
        return valid_urls

    @property
    def is_development(self) -> bool:
        """Check if the application is running in development mode"""
        return self.app_env.lower() in ["development", "dev"]

    @property
    def is_production(self) -> bool:
        """Check if the application is running in production mode"""
        return self.app_env.lower() in ["production", "prod"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
