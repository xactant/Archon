from abc import ABC, abstractmethod
from archon.db.db_client import DbClient

class EnvironmentBase(ABC):
    """
    Base class for environment subpages.
    """
    def __init__(self, db_client: DbClient):
        self.db_client = db_client
     
    @abstractmethod
    def get_database_configuration(self, st, profile_env_vars, updated_values):
        """
        Get the database configuration settings.
        """
        pass
 
    @abstractmethod
    def get_not_setup_message(self):
       pass

    @abstractmethod
    def get_not_setup_message(self):
        pass