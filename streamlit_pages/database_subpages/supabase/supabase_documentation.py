from archon.db.db_client import DbClient
from .. import DocumentationBase


class SupabaseDocumentation(DocumentationBase):
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

    def get_sample_data(self):
        """
        Get sample data for the documentation.
        
        Returns:
            str: Sample data for the documentation.
        """
        return self.db_client.table("site_pages").select("url,title,summary,chunk_number").eq("metadata->>source", "pydantic_ai_docs").limit(10).execute()