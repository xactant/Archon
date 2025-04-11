from typing import Dict, List, Any, Optional, Union
import sys
import os
from dotenv import load_dotenv

# Make sure the parent directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from supabase import Client
from utils.env_utils import get_env_var, write_to_log
from archon.db.db_client import DbClient
from archon.db.models import ProcessedChunk


class SupabaseClient(DbClient):
    """
    Supabase implementation of the DbClient interface.
    
    This class provides concrete implementations of database operations
    using Supabase as the backend.
    """
    
    def __init__(self):
        """
        Initialize the SupabaseClient with a Supabase client instance.
        It loads environment variables and sets up the Supabase client.
        """
        super().__init__('supabase')
        load_dotenv()
        # Supabase client setup
        self.supabase = None
        supabase_url = get_env_var("SUPABASE_URL")
        supabase_key = get_env_var("SUPABASE_SERVICE_KEY")

        if supabase_url and supabase_key:
            try:
                self.supabase: Client = Client(supabase_url, supabase_key)
            except Exception as e:
                print(f"Failed to initialize Supabase: {e}")
                write_to_log(f"Failed to initialize Supabase: {e}")
                raise
        else:
            raise ValueError("Supabase URL or key not found in environment variables.")
    
    def match_site_pages(
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
        try:
            result = self.supabase.rpc(
                'match_site_pages',
                {
                    'query_embedding': query_embedding,
                    'match_count': match_count,
                    'filter': filter
                }
            ).execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"Error in match_site_pages: {e}")
            return []
    
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
        try:
            data = {
                "url": chunk.url,
                "chunk_number": chunk.chunk_number,
                "title": chunk.title,
                "summary": chunk.summary,
                "content": chunk.content,
                "metadata": chunk.metadata,
                "embedding": chunk.embedding
            }
            
            result = self.supabase.table("site_pages").insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error inserting chunk: {e}")
            return None
    
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
        try:
            result = self.supabase.from_('site_pages') \
                .select('url') \
                .eq('metadata->>source', source) \
                .execute()
            
            if not result.data:
                return []
                
            # Extract unique URLs
            urls = sorted(set(doc['url'] for doc in result.data))
            return urls
        except Exception as e:
            print(f"Error retrieving documentation pages: {e}")
            return []
    
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
        try:
            result = self.supabase.from_('site_pages') \
                .select('title, content, chunk_number') \
                .eq('url', url) \
                .eq('metadata->>source', source) \
                .order('chunk_number') \
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"Error retrieving page content: {e}")
            return []
    
    def count_site_pages(self) -> int:
        """
        Count the total number of records in the site_pages table.
        
        Returns:
            The exact count of records in the site_pages table
        """
        try:
            result = self.supabase.table("site_pages").select("*", count="exact").execute()
            return result.count if hasattr(result, 'count') else 0
        except Exception as e:
            print(f"Error counting site pages: {e}")
            return 0
    
    def check_table_exists(self) -> bool:
        """
        Check if the site_pages table exists and has at least one record.
        
        Returns:
            True if the table exists and has at least one record, False otherwise
        """
        try:
            result = self.supabase.table("site_pages").select("id").limit(1).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error checking if table exists: {e}")
            return False
    
    def clear_site_pages(self, exclude_ids: Optional[List[int]] = None) -> Union[Dict[str, Any], None]:
        """
        Clear all records from the site_pages table, optionally excluding specific IDs.
        
        Args:
            exclude_ids: Optional list of record IDs to exclude from deletion
            
        Returns:
            Result of the deletion operation, or None if an error occurred
        """
        try:
            if exclude_ids:
                # Delete all records except those with IDs in the exclude_ids list
                result = self.supabase.table("site_pages").delete().not_.in_("id", exclude_ids).execute()
            else:
                # Delete all records
                result = self.supabase.table("site_pages").delete().neq("id", 0).execute()
            return result.data
        except Exception as e:
            print(f"Error clearing site pages: {e}")
            return None
    
    def clear_by_source(self, source: str) -> Union[Dict[str, Any], None]:
        """
        Clear all records with a specific source from the site_pages table.
        
        Args:
            source: The source identifier to clear (e.g., 'pydantic_ai_docs')
            
        Returns:
            Result of the deletion operation, or None if an error occurred
        """
        try:
            result = self.supabase.table("site_pages").delete().eq("metadata->>source", source).execute()
            return result.data
        except Exception as e:
            print(f"Error clearing by source: {e}")
            return None