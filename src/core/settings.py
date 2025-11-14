from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os
import re

URL_REGEX = re.compile(r'^https?://')

class Settings(BaseSettings):
    # Application environment
    app_env: str = Field(default="development", description="Application environment (development, production, etc.)")
    
    # CORS configuration
    cors_allow_urls: str = Field(default="")
    
    # Debugpy settings
    debugpy_enabled: bool = Field(default=False, description="Enable debugpy for remote debugging")
    debugpy_port: int = Field(default=5678, description="Port for debugpy to listen on")
    debugpy_wait: bool = Field(default=False, description="Whether debugpy should wait for a connection")

    @property
    def cors_allow_urls_list(self) -> List[str]:
        v = self.cors_allow_urls
        if not isinstance(v, str) or not v.strip():
            raise ValueError("CORS_ALLOW_URLS must be a non-empty comma-separated string of URLs.")
        urls = [url.strip() for url in v.split(',') if url.strip()]
        if not urls:
            raise ValueError("CORS_ALLOW_URLS must contain at least one valid URL.")
        
        valid_urls = []
        for url in urls:
            if URL_REGEX.match(url):
                valid_urls.append(url)
            else:
                raise ValueError(f"Invalid CORS origin: {url}. Must be a valid http(s) URL.")
        if not valid_urls:
            raise ValueError("CORS_ALLOW_URLS must contain at least one valid URL.")
        return valid_urls

    @property
    def is_development(self) -> bool:
        """Check if the application is running in development mode"""
        return self.app_env.lower() in ['development', 'dev']
    
    @property
    def is_production(self) -> bool:
        """Check if the application is running in production mode"""
        return self.app_env.lower() in ['production', 'prod']

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 