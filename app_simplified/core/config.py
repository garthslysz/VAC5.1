"""
Configuration management
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    debug: bool = True
    port: int = 8000
    log_level: str = "INFO"
    
    # CORS settings (as string, will be split later)
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    
    # OpenAI Configuration (regular OpenAI API)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_timeout: int = 30
    
    # Authentication
    auth_disabled: bool = False
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    
    # File processing
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: str = ".pdf,.docx,.txt,.json"
    
    # Data paths
    rules_path: str = "app_simplified/data/rules"
    documents_path: str = "app_simplified/data/documents"
    
    # Development settings
    enable_detailed_logging: bool = True
    mock_auth_user_id: str = "test-user-001"
    default_case_id: str = "demo-case-001"
    
    # Local storage settings
    use_local_file_storage: bool = True
    local_file_storage_path: str = "./local_uploads"
    
    # Debug settings
    enable_api_debug: bool = True
    save_conversation_logs: bool = False
    
    # Optional Azure Storage (for production)
    azure_storage_connection_string: str = ""
    azure_storage_container: str = "vac-assessment-files"
    
    # Helper properties
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins to list"""
        if self.cors_origins:
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return ["http://localhost:3000", "http://localhost:8000"]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Convert comma-separated file types to list"""
        if self.allowed_file_types:
            return [ext.strip() for ext in self.allowed_file_types.split(",")]
        return [".pdf", ".docx", ".txt", ".json"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

def get_settings() -> Settings:
    return Settings()
