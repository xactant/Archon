"""
Factory for creating database subpage instances based on the database type.
"""

from .supabase import SupabaseDatabase, SupabaseDocumentation, SupabaseEnvironment
from .postgresql import PostgresqlDatabase, PostgresqlDocumentation, PostgresqlEnvironment
from archon.db.db_client import DbClient

class DatabaseSubpagesFactory:
    """Factory class for creating database subpage instances."""
    
    def __init__(self, db_client: DbClient):
        """Initialize the factory with a database client."""
        self.db_client = db_client

    def get_subpage(self, page_type: str):
        """Get the appropriate subpage instance based on the database type."""
        db_type = self.db_client.db_name().lower()
        
        if db_type == 'supabase':
            if page_type == 'database':
                return SupabaseDatabase(self.db_client)
            elif page_type == 'documentation':
                return SupabaseDocumentation(self.db_client)
            elif page_type == 'environment':
                return SupabaseEnvironment(self.db_client)
        elif db_type == 'postgresql':
            if page_type == 'database':
                return PostgresqlDatabase(self.db_client)
            elif page_type == 'documentation':
                return PostgresqlDocumentation(self.db_client)
            elif page_type == 'environment':
                return PostgresqlEnvironment(self.db_client)
        
        raise ValueError(f"Invalid database type '{db_type}' or page type '{page_type}'")