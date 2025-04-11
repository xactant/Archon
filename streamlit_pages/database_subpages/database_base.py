from abc import ABC, abstractmethod
from archon.db.db_client import DbClient
import asyncio

class DatabaseBase(ABC):
    def __init__(self, db_client: DbClient):
        self.db_client = db_client
    
    @abstractmethod
    def get_not_setup_message(self):
        pass

    @abstractmethod
    def show_manual_sql_instructions(self, st, sql, vector_dim, recreate=False):
        pass
    
    @abstractmethod
    def show_manual_truncate_instructions(self, st):
        pass
    
    def check_table_exists(self):
        """
        Check if the site_pages table exists.
        """
        return asyncio.run(self.db_client.check_table_exists())
    
    def count_site_pages(self):
        """
        Count the total number of records in the site_pages table.
        """
        return asyncio.run(self.db_client.count_site_pages())
    
    def clear_site_pages(self):
        """
        Clear all records from the site_pages table.
        """
        return asyncio.run(self.db_client.clear_site_pages())
    
    def clear_by_source(self, source):
        """
        Clear all records from the site_pages table for a specific source.
        """
        return asyncio.run(self.db_client.clear_by_source(source))
    
    def get_site_pages_sql(self, sql_template: str, vector_dim: int):
        """
        Replace the vector dimensions in the SQL
        """
         # Replace the vector dimensions in the SQL
        sql = sql_template.replace("vector(1536)", f"vector({vector_dim})")
        # Also update the match_site_pages function dimensions
        sql = sql.replace("query_embedding vector(1536)", f"query_embedding vector({vector_dim})")
        return sql