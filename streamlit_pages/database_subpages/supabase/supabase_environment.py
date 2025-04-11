from archon.db.db_client import DbClient
from .. import EnvironmentBase


class SupabaseEnvironment(EnvironmentBase):
    def __init__(self, db_client: DbClient):
        super().__init__(db_client)
        
        
        
        