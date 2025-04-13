
from archon.db.db_client import DbClient
from supabase.supabase_database import SupabaseDatabase
from supabase.supabase_documentation import SupabaseDocumentation
from supabase.supabase_environment import SupabaseEnvironment
from postgresql.postgresql_database import PostgresqlDatabase
from postgresql.postgresql_documentation import PostgresqlDocumentation
from postgresql.postgresql_environment import PostgresqlEnvironment

class DatabaseSubpagesFactory:
    def __init__(self, db_client: DbClient):
        self.db_client = db_client
        
    def get_subpage(self, subpage_name: str):
        db_name = self.db_client.db_name()
        match_name = f'{db_name}_{subpage_name}'
        
        match match_name:
            case 'supabase_database':
                return SupabaseDatabase(self.db_client)
            case 'supabase_documentation':
                return SupabaseDocumentation(self.db_client)
            case 'supabase_environment':
                return SupabaseEnvironment(self.db_client)
            case 'postgresql_database':
                return PostgresqlDatabase(self.db_client)
            case 'postgresql_documentation':
                return PostgresqlDocumentation(self.db_client)
            case 'postgresql_environment':
                return PostgresqlEnvironment(self.db_client) 
            case _:
                raise ValueError(f'Invalid subpage name: {subpage_name}')