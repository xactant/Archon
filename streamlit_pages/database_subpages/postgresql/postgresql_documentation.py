from archon.db.db_client import DbClient
from .. import DocumentationBase

class PostgresqlDocumentation(DocumentationBase):
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
        """
        Returns a message indicating that the PostgreSQL database is not set up.
        """
        return "PostgreSQL database is not set up. Please configure it in the environment settings."
