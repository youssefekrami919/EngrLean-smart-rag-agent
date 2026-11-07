"""Central configuration for EngrLean Smart RAG Agent."""
from pathlib import Path
from pydantic import BaseModel, Field

class CompanyProfile(BaseModel):
    name: str = "EngrLean"
    ceo: str = "Eng. Mohamed Yahia"
    website: str = "https://engrlean.com/"
    taglines: list[str] = [
        "Built on engineering. Driven by technology.",
        "Engineering meets Technology."
    ]
    support_email: str = "contact@engrlean.com"
    support_phone: str = "+20 100 000 0000"
    support_whatsapp: str = "+20 100 000 0000"
    whatsapp_link: str = "https://wa.me/201000000000"


class AgentSettings(BaseModel):
    name: str = "LeanBot"
    persona: str = "EngrLean Intelligent Engineering & Technology Consultant"
    tone: str = "Friendly, highly professional, precise, and engineering-grounded"
    system_language_policy: str = "Bilingual (Fluent in Arabic and English)"


class ModelSettings(BaseModel):
    llm_model: str = "gemini-3.8-flash"
    embedding_model: str = "models/gemini-embedding-001"
    temperature: float = 0.2
    max_output_tokens: int = 2048


class RAGSettings(BaseModel):
    chunk_size: int = 1000
    chunk_overlap: int = 150
    top_k: int = 4
    collection_name: str = "engrlean_knowledge"


class Settings(BaseModel):
    company: CompanyProfile = Field(default_factory=CompanyProfile)
    agent: AgentSettings = Field(default_factory=AgentSettings)
    models: ModelSettings = Field(default_factory=ModelSettings)
    rag: RAGSettings = Field(default_factory=RAGSettings)

    # File System Paths
    root_dir: Path = Path(__file__).resolve().parent.parent.parent
    knowledge_dir: Path = root_dir / "data" / "knowledge"
    chroma_dir: Path = root_dir / "chroma_db"


settings = Settings()

