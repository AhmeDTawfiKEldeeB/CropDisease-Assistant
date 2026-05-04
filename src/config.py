import os
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar


class QdrantSettings(BaseModel):
    url: str = Field(default="", description="Qdrant API URL")
    api_key: str = Field(default="", description="Qdrant API key")
    collection_name: str = Field(default="plant_diseases3", description="Qdrant collection name")
    upload_batch_size: int = Field(default=64, description="Batch size used during point upload")
    data_json_path: str = Field(default="Knowledge_Base/diseases_from_md.json", description="Path to cleaned disease JSON data")


class HuggingFaceSettings(BaseModel):
    model_name: str = Field(
        default="intfloat/multilingual-e5-large",
        description="Multilingual embedding model"
    )
    model_dimensions: int = Field(default=1024, description="Dimensionality of the model's output embeddings")


class GroqSettings(BaseModel):
    api_key: str = Field(default="", description="Groq API key")
    base_url: str = Field(default="https://api.groq.com/openai/v1", description="Groq OpenAI-compatible base URL")
    model: str = Field(default="openai/gpt-oss-120b", description="Groq model name")
    temperature: float = Field(default=0.3, description="Sampling temperature")
    max_tokens: int = Field(default=400, description="Max tokens in response")


class LangSmithSettings(BaseModel):
    api_key: str = Field(default="", description="LangSmith API key")
    tracing: bool = Field(default=True, description="Enable LangSmith tracing")
    endpoint: str = Field(default="https://api.smith.langchain.com", description="LangSmith endpoint")
    project: str = Field(default="CropDisease", description="LangSmith project name")


class Settings(BaseSettings):
    qdrant: QdrantSettings = Field(default_factory=QdrantSettings)
    huggingface: HuggingFaceSettings = Field(default_factory=HuggingFaceSettings)
    groq: GroqSettings = Field(default_factory=GroqSettings)
    langsmith: LangSmithSettings = Field(default_factory=LangSmithSettings)

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=[".env"],
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
        case_sensitive=False,
        frozen=True,
    )


settings = Settings()