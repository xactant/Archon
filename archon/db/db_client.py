from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple

from archon.db.models import ProcessedChunk


class DbClient(ABC):
    """
    Abstract base class for database interactions.
    
    This class defines the interface for database operations that were previously
    implemented using Supabase RPC calls. Implementations of this class should
    provide concrete implementations for each method.
    """
    def __init__(self, name: str):
        self.name = name

    def db_name(self):
        return self.name
    
    @abstractmethod
    async def match_site_pages(
        self, 
        query_embedding: List[float], 
        match_count: int, 
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find pages that match the given query embedding using vector similarity search.
        
        Args:
            query_embedding: A vector embedding of the user's query
            match_count: Number of matches to return
            filter: Optional filter criteria, e.g. {'source': 'pydantic_ai_docs'}
            
        Returns:
            List of matching documents/pages with their metadata
        """
        pass
    
    @abstractmethod
    async def insert_chunk(
        self,
        chunk: ProcessedChunk
    ) -> Union[Dict[str, Any], None]:
        """
        Insert a processed document chunk into the database.
        
        Args:
            chunk: A ProcessedChunk object containing all data for the document chunk
            
        Returns:
            Result of the insert operation, or None if an error occurred
        """
        pass
    
    @abstractmethod
    async def list_documentation_pages(
        self,
        source: str = 'pydantic_ai_docs'
    ) -> List[str]:
        """
        Retrieve a list of all available documentation pages for a specific source.
        
        Args:
            source: The source identifier for the documentation pages (default: 'pydantic_ai_docs')
            
        Returns:
            List of unique URLs for all documentation pages from the specified source
        """
        pass
    
    @abstractmethod
    async def get_page_content(
        self,
        url: str,
        source: str = 'pydantic_ai_docs'
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the content of a specific documentation page by URL.
        
        Args:
            url: The URL of the page to retrieve
            source: The source identifier for the documentation (default: 'pydantic_ai_docs')
            
        Returns:
            List of page chunks with title, content, and chunk_number, ordered by chunk_number
        """
        pass
    
    @abstractmethod
    async def count_site_pages(self) -> int:
        """
        Count the total number of records in the site_pages table.
        
        Returns:
            The exact count of records in the site_pages table
        """
        pass
    
    @abstractmethod
    async def check_table_exists(self) -> bool:
        """
        Check if the site_pages table exists and has at least one record.
        
        Returns:
            True if the table exists and has at least one record, False otherwise
        """
        pass
    
    @abstractmethod
    async def clear_site_pages(self, exclude_ids: Optional[List[int]] = None) -> Union[Dict[str, Any], None]:
        """
        Clear all records from the site_pages table, optionally excluding specific IDs.
        
        Args:
            exclude_ids: Optional list of record IDs to exclude from deletion
            
        Returns:
            Result of the deletion operation, or None if an error occurred
        """
        pass
    
    @abstractmethod
    async def clear_by_source(self, source: str) -> Union[Dict[str, Any], None]:
        """
        Clear all records with a specific source from the site_pages table.
        
        Args:
            source: The source identifier to clear (e.g., 'pydantic_ai_docs')
            
        Returns:
            Result of the deletion operation, or None if an error occurred
        """
        pass
        
    @abstractmethod
    async def client_configured(self) -> bool:
        """
        Check if the database client is configured.
        
        Returns:
            True if the client is configured, False otherwise
        """
        pass

    @abstractmethod
    async def get_example_data(self, source: str, limit: int) -> List[Dict[str, Any]]:
        """
        Get example data from the database.
        
        Args:
            source: The source identifier for the example data
            
        Returns:
            List of example data records
        """
        pass
  