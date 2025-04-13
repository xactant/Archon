from archon.db.db_client import DbClient
from .. import EnvironmentBase


class SupabaseEnvironment(EnvironmentBase):
    def __init__(self, db_client: DbClient):
        super().__init__(db_client)
        
    def get_database_configuration(self, st, profile_env_vars, updated_values):
        """
        Get the database configuration settings.
        """
        # SUPABASE_URL
        supabase_url_help = "Get your SUPABASE_URL from the API section of your Supabase project settings -\nhttps://supabase.com/dashboard/project/<your project ID>/settings/api"
        
        supabase_url = st.text_input(
            "SUPABASE_URL:",
            value=profile_env_vars.get("SUPABASE_URL", ""),
            help=supabase_url_help,
            key="input_SUPABASE_URL"
        )
        updated_values["SUPABASE_URL"] = supabase_url
        
        # SUPABASE_SERVICE_KEY
        supabase_key_help = "Get your SUPABASE_SERVICE_KEY from the API section of your Supabase project settings -\nhttps://supabase.com/dashboard/project/<your project ID>/settings/api\nOn this page it is called the service_role secret."
        
        # If there's already a value, show asterisks in the placeholder
        placeholder = "Set but hidden" if profile_env_vars.get("SUPABASE_SERVICE_KEY", "") else ""
        supabase_key = st.text_input(
            "SUPABASE_SERVICE_KEY:",
            type="password",
            help=supabase_key_help,
            key="input_SUPABASE_SERVICE_KEY",
            placeholder=placeholder
        )
        # Only update if user entered something (to avoid overwriting with empty string)
        if supabase_key:
            updated_values["SUPABASE_SERVICE_KEY"] = supabase_key
        
    def get_not_setup_message(self):
        """Get the message to display if Supabase is not configured"""
        return "Supabase is not configured. Please set your Supabase URL and Service Key in the Environment tab."
   