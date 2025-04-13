from abc import ABC, abstractmethod
import asyncio
from archon.db.db_client import DbClient

class DocumentationBase(ABC):
    def __init__(self, db_client: DbClient):
        self.db_client = db_client
    
    @abstractmethod
    def get_db_name(self) -> str:
        pass

    @abstractmethod
    def get_not_setup_message(self):
        pass
    
    @abstractmethod
    def get_sample_data(self):
        pass

    def db_client_configured(self):
        return self.db_client.client_configured()
    
    def count_site_pages(self):
        """
        Count the total number of records in the site_pages table.
        """
        return asyncio.run(self.db_client.count_site_pages())
    