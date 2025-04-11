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

class DbFactory:
    """
    Factory class to create and manage database connections.
    
    This class is responsible for creating instances of the database client
    based on the configuration provided. It abstracts the details of the
    underlying database technology, allowing for easy switching between
    different databases in the future.
    """
    _instance = None
    _loop = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DbFactory, cls).__new__(cls)
            cls._instance.db_client = None
            cls._instance.db_type = None
        return cls._instance

    def _get_event_loop(self):
        """Get or create an event loop for async operations."""
        try:
            # First try to get the current event loop
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists, create a new one
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop

    def create_client(self, database_client) -> DbClient:
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
        self.db_client = None

        match database_client:
            case DatabaseClients.SUPABASE:
                self.db_client = SupabaseClient()
                
            case DatabaseClients.POSTGRESQL:
                # Read PostgreSQL connection parameters from environment variables
                try:
                    # Get or create an event loop
                    loop = self._get_event_loop()
                    host = os.getenv('POSTGRES_HOST', 'localhost')
                    port = int(os.getenv('POSTGRES_PORT', '5432'))
                    user = os.getenv('POSTGRES_USER', 'postgres')
                    password = os.getenv('POSTGRES_PASSWORD', '')
                    database = os.getenv('POSTGRES_DB', 'postgres')
                    min_size = int(os.getenv('POSTGRES_MIN_CONN', '1'))
                    max_size = int(os.getenv('POSTGRES_MAX_CONN', '10'))
                    
                    # Create the connection pool in a new event loop if needed
                    if loop.is_running():
                        # If loop is running (e.g., in Streamlit), create a new one
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        connection_pool = new_loop.run_until_complete(asyncpg.create_pool(
                            host=host,
                            port=port,
                            user=user,
                            password=password,
                            database=database,
                            min_size=min_size,
                            max_size=max_size
                        ))
                        asyncio.set_event_loop(loop)  # Restore original loop
                    else:
                        # Use the current loop if it's not running
                        connection_pool = loop.run_until_complete(asyncpg.create_pool(
                            host=host,
                            port=port,
                            user=user,
                            password=password,
                            database=database,
                            min_size=min_size,
                            max_size=max_size
                        ))
                    
                    self.db_client = PostgreSqlClient(connection_pool)
                except Exception as e:
                    error_msg = f"Failed to create PostgreSQL connection: {str(e)}"
                    print(error_msg)
                    write_to_log(error_msg)
                    raise ValueError(error_msg)
                
            # Add more cases for other database clients as needed
            case _:
                raise ValueError(f"Unsupported database client: {database_client}")
        
        self.db_type = database_client

        # Log the type of database client created
        print(f"Database client created: {self.db_type}")
        write_to_log(f"Database client created: {self.db_type}")

        self.db_client.which_db()
        
        # Return the created database client instance
        return self.db_client
