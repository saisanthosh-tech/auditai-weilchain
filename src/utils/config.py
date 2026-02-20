"""
AuditAI - Configuration Loader

Loads and validates configuration from environment variables.
Uses pydantic-settings for type-safe configuration management.
"""

from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field

class LLMConfig(BaseSettings):
    """LLM provider configuration."""

    model_config = {"env_prefix": ""}
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-4", alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.1, alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=4096, alias="LLM_MAX_TOKENS")

class WeilchainConfig(BaseSettings):
    """Weilchain blockchain configuration."""

    model_config = {"env_prefix": ""}
    rpc_url: str = Field(default="https://rpc.weilchain.io", alias="WEILCHAIN_RPC_URL")
    chain_id: int = Field(default=1, alias="WEILCHAIN_CHAIN_ID")
    wallet_key: str = Field(default="", alias="WEILCHAIN_WALLET_KEY")
    wallet_address: str = Field(default="", alias="WEILCHAIN_WALLET_ADDRESS")

class WeillipticConfig(BaseSettings):
    """Weilliptic SDK configuration."""

    model_config = {"env_prefix": ""}
    api_key: str = Field(default="", alias="WEILLIPTIC_API_KEY")
    api_url: str = Field(default="https://api.weilliptic.ai", alias="WEILLIPTIC_API_URL")
    applet_id: str = Field(default="", alias="WEILLIPTIC_APPLET_ID")

class AuditConfig(BaseSettings):
    """Audit logging configuration."""

    model_config = {"env_prefix": "AUDIT_"}
    log_level: str = Field(default="detailed", alias="AUDIT_LOG_LEVEL")
    on_chain: bool = Field(default=True, alias="AUDIT_ON_CHAIN")
    local_file: bool = Field(default=True, alias="AUDIT_LOCAL_FILE")
    local_file_path: str = Field(default="./logs/audit.jsonl", alias="AUDIT_LOCAL_FILE_PATH")

class AgentConfig(BaseSettings):
    """Agent behavior configuration."""

    model_config = {"env_prefix": "AGENT_"}
    max_iterations: int = Field(default=10, alias="AGENT_MAX_ITERATIONS")
    verbose: bool = Field(default=False, alias="AGENT_VERBOSE")

class AppConfig(BaseSettings):
    """Root application configuration."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    llm: LLMConfig = Field(default_factory=LLMConfig)
    weilchain: WeilchainConfig = Field(default_factory=WeilchainConfig)
    weilliptic: WeillipticConfig = Field(default_factory=WeillipticConfig)
    audit: AuditConfig = Field(default_factory=AuditConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)

@lru_cache()
def get_config() -> AppConfig:
    """Get the application configuration (cached singleton)."""
    return AppConfig()
