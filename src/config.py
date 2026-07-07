from pathlib import Path
from typing import ClassVar, List

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class QdrantSettings(BaseModel):
    url: str = Field(default="", description="Qdrant API URL")
    api_key: str = Field(default="", description="Qdrant API key")
    collection_name: str = Field(default="plant_diseases", description="Qdrant collection name")
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
    max_tokens: int = Field(default=500, description="Max tokens in response")


class LangSmithSettings(BaseModel):
    api_key: str = Field(default="", description="LangSmith API key")
    tracing: bool = Field(default=True, description="Enable LangSmith tracing")
    endpoint: str = Field(default="https://api.smith.langchain.com", description="LangSmith endpoint")
    project: str = Field(default="CropDisease", description="LangSmith project name")


class CVSettings(BaseModel):
    model_path: str = Field(default=str(Path("src") / "cv" / "models" / "resnet50_plant_38class_best.pth.zip"),description="Path to the trained ResNet50 checkpoint",)
    num_classes: int = Field(default=38, description="Number of plant disease classes")
    image_size: int = Field(default=224, description="Input image size in pixels")
    normalize_mean: List[float] = Field(default=[0.485, 0.456, 0.406],description="ImageNet normalization mean",)
    normalize_std: List[float] = Field(default=[0.229, 0.224, 0.225],description="ImageNet normalization std",)
    entropy_threshold: float = Field(default=0.4,description="Normalized entropy threshold below which a prediction is considered reliable",)
    gap_threshold: float = Field(default=5.0,description="Minimum confidence gap (percentage points) between top-1 and top-2 for reliability",)
    tta_enabled: bool = Field(default=False,description="Enable test-time augmentation for more robust predictions",)
    tta_transforms: int = Field(default=3,ge=1,le=8,description="Number of TTA transforms to apply (including the original image)",)
    temperature: float = Field(default=1.0,gt=0.0,le=2.0,description="Softmax temperature for confidence calibration (<1 sharper, >1 softer)",)
    device: str = Field(default="auto",description="Device to run inference on: 'auto', 'cpu', or 'cuda'",)


class Settings(BaseSettings):
    qdrant: QdrantSettings = Field(default_factory=QdrantSettings)
    huggingface: HuggingFaceSettings = Field(default_factory=HuggingFaceSettings)
    groq: GroqSettings = Field(default_factory=GroqSettings)
    langsmith: LangSmithSettings = Field(default_factory=LangSmithSettings)
    cv: CVSettings = Field(default_factory=CVSettings)

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=[".env"],
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
        case_sensitive=False,
        frozen=True,
    )

settings = Settings()