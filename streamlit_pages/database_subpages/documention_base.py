from abc import ABC, abstractmethod
import asyncio
from archon.db.db_client import DbClient

class DocumentationBase(ABC):
    """
    Base class for documentation subpages.
    """
    def __init__(self, db_client: DbClient):
        self.db_client = db_client
    
    @abstractmethod
    def get_db_name(self) -> str:
        pass

    @abstractmethod
    def get_not_setup_message(self):
        pass
    
    def get_sample_data(self, source: str, limit: int):
        """
        Get sample data from the database.
        """
        print("Getting sample data")
        return self.db_client.get_example_data(source, limit)

    def db_client_configured(self):
        """
        Check if the database client is configured.
        """
        print("Checking if db client is configured")
        return self.db_client.client_configured()
    
    def count_site_pages(self):
        """
        Count the total number of records in the site_pages table.
        """
        print("Counting site pages")
        return self.db_client.count_site_pages()
    