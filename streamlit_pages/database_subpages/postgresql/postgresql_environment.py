from archon.db.db_client import DbClient
from .. import EnvironmentBase

class PostgresqlEnvironment(EnvironmentBase):
    def __init__(self, db_client: DbClient):
        super().__init__(db_client)

    def get_database_configuration(self, st, profile_env_vars, updated_values):
        """
        Get the database configuration settings.
        """
        postgres_url = st.text_input(
            "POSTGRES_HOST:",
            value=profile_env_vars.get("POSTGRES_HOST", ""),
            key="input_POSTGRES_HOST"
        )
        updated_values["POSTGRES_HOST"] = postgres_url
        
        # If there's already a value, show asterisks in the placeholder
        postgres_port = st.text_input(
            "POSTGRES_PORT:",
            value=profile_env_vars.get("POSTGRES_PORT", "5432"),
            key="input_POSTGRES_PORT"
        )
        # Only update if user entered something (to avoid overwriting with empty string)
        if postgres_port:
            updated_values["POSTGRES_PORT"] = postgres_port
        
        # If there's already a value, show asterisks in the placeholder
        postgres_db = st.text_input(
            "POSTGRES_DB:",
            value=profile_env_vars.get("POSTGRES_DB", "postgres"),
            key="input_POSTGRES_DB"
        )
        # Only update if user entered something (to avoid overwriting with empty string)
        if postgres_db:
            updated_values["POSTGRES_DB"] = postgres_db
        
        # If there's already a value, show asterisks in the placeholder
        postgres_user = st.text_input(
            "POSTGRES_USER:",
            value=profile_env_vars.get("POSTGRES_USER", "postgres"),
            key="input_POSTGRES_USER"
        )
        # Only update if user entered something (to avoid overwriting with empty string)
        if postgres_user:
            updated_values["POSTGRES_USER"] = postgres_user

        # If there's already a value, show asterisks in the placeholder
        postgres_password = st.text_input(
            "POSTGRES_PASSWORD:",
            type="password",
            value=profile_env_vars.get("POSTGRES_PASSWORD", ""),
            key="input_POSTGRES_PASSWORD",
            placeholder="Pasword is set but hidden"
        )
        # Only update if user entered something (to avoid overwriting with empty string)
        if postgres_password:
            updated_values["POSTGRES_PASSWORD"] = postgres_password
 
    def get_not_setup_message(self):
        """
        Returns a message indicating that the PostgreSQL database is not set up.
        """
        return "PostgreSQL database is not set up. Please configure it in the environment settings."
