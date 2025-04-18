import asyncio
from archon.db.db_client import DbClient
from .. import DocumentationBase


class SupabaseDocumentation(DocumentationBase):
    """
    Subclass for Supabase documentation operations.
    """
    def __init__(self, db_client: DbClient):
        super().__init__(db_client)
        
    def get_db_name(self) -> str:
        """
        Get the name of the database client.
        
        Returns:
            str: The name of the database client.
        """
        return self.db_client.db_name().capitalize()   
    
    def get_not_setup_message(self):
        """Get the message to display if Supabase is not configured"""
        return "Supabase is not configured. Please set your Supabase URL and Service Key in the Environment tab."

    def count_site_pages(self):
        """
        Count the total number of records in the site_pages table.
        """
        result = self._run_async(self.db_client.count_site_pages())
        return result.count if hasattr(result, "count") else 0