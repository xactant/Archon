import os
import asyncio
import asyncpg
from dotenv import load_dotenv

from archon.db.db_client import DbClient
from archon.db.clients.supabase_client import SupabaseClient
from archon.db.clients.postgresql_client import PostgreSqlClient
from archon.db.models import DatabaseClients

from utils.env_utils import write_to_log

# Load environment variables
load_dotenv()

def _create_db_client(database_client):
    """
    Create a database client based on the provided configuration.
    This method initializes the database client and returns an instance
    of the client for use in the application.
    It supports multiple database types, allowing for easy switching
    between different databases in the future.
    Args:
        database_client: The type of database client to create (e.g., DatabaseClients.SUPABASE).
    Returns:
            An instance of a database client implementing the DbClient interface
    Raises:
        TypeError: If the provided database client is not a valid type.
        ValueError: If the provided database client is not supported.
    """
    print(f"Creating database client: {database_client}")
    write_to_log(f"Creating database client: {database_client}")

    db_client = None
    match database_client:
        case DatabaseClients.SUPABASE:
            db_client = SupabaseClient()
            
        case DatabaseClients.POSTGRESQL:
            db_client = PostgreSqlClient()
            
        # Add more cases for other database clients as needed
        case _:
            raise ValueError(f"Unsupported database client: {database_client}")
    
    return db_client


class DbFactory:
    """
    Factory class to create and manage database connections.
    
    This class is responsible for creating instances of the database client
    based on the configuration provided. It abstracts the details of the
    underlying database technology, allowing for easy switching between
    different databases in the future.
    """

    def get_client(self, database_client) -> DbClient:
        """
        Create a database client based on the provided configuration.
        This method initializes the database client and returns an instance
        of the client for use in the application.
        It supports multiple database types, allowing for easy switching
        between different databases in the future.
        Args:
            database_client: The type of database client to create (e.g., DatabaseClients.SUPABASE).
        Returns:
                An instance of a database client implementing the DbClient interface
        Raises:
            TypeError: If the provided database client is not a valid type.
            ValueError: If the provided database client is not supported.
        """
        print(f"Creating database client: {database_client}")
        write_to_log(f"Creating database client: {database_client}")

        db_client = None
        match database_client:
            case DatabaseClients.SUPABASE:
                db_client = SupabaseClient()
                
            case DatabaseClients.POSTGRESQL:
                db_client = PostgreSqlClient()
                
            # Add more cases for other database clients as needed
            case _:
                raise ValueError(f"Unsupported database client: {database_client}")
        
        return db_client
