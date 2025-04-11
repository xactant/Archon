from dataclasses import dataclass
from typing import Dict, List, Any
from enum import Enum

class DatabaseClients(str, Enum):
    SUPABASE = "supabase"
    POSTGRESQL = "postgresql"

@dataclass
class ProcessedChunk:
    """A processed document chunk ready for database insertion."""
    url: str
    chunk_number: int
    title: str
    summary: str
    content: str
    metadata: Dict[str, Any]
    embedding: List[float]