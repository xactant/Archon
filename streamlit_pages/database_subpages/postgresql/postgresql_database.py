from archon.db.db_client import DbClient
from utils.env_utils import get_env_var
from .. import DatabaseBase

class PostgresqlDatabase(DatabaseBase):
    """
    Subclass for PostgreSQL database operations.
    """
    def __init__(self, db_client: DbClient):
        super().__init__(db_client)
    
    def get_not_setup_message(self):
        """
        Returns a message indicating that the PostgreSQL database is not set up.
        """
        return "PostgreSQL database is not set up. Please configure it in the environment settings."

    def show_manual_sql_instructions(self, st, sql, vector_dim, recreate=False):
        """Show instructions for manually executing SQL in PostgreSQL"""
        st.info("### Manual SQL Execution Instructions")
        
        # Provide a link to the Postgres SQL Editor
        if not self.show_postgres_markdown(st):
            st.markdown("**Step 1:** Open your Postgres Editor and navigate to the SQL Editor")
        
        st.markdown("**Step 2:** Create a new SQL query")
        
        if recreate:
            st.markdown("**Step 3:** Copy and execute the following SQL:")
            drop_sql = f"DROP FUNCTION IF EXISTS match_site_pages(vector({vector_dim}), int, jsonb);\nDELETE FROM site_pages;"
            st.code(drop_sql, language="sql")
            
            st.markdown("**Step 4:** Then copy and execute this SQL:")
            st.code(sql, language="sql")
        else:
            st.markdown("**Step 3:** Copy and execute the following SQL:")
            st.code(sql, language="sql")
        
        st.success("After executing the SQL, return to this page and refresh to see the updated table status.")
    
    
    def show_manual_truncate_instructions(self, st):
        st.info("Execute this SQL in your Postgres SQL Editor to clear the table data.")

        if not self.show_postgres_markdown(st):
            st.markdown("Open your Postgres Editor and navigate to the SQL Editor")  
    
    def show_postgres_markdown(self, st) -> bool:
        """
        Show the PostgreSQL database markdown.
        """
        response = False

        # Provide a link to the Postgres SQL Editor
        postgres_url = get_env_var("POSTGRES_HOST")
        postgres_port = get_env_var("POSTGRES_PORT")
        postgres_db = get_env_var("POSTGRES_DB")
        postgres_user = get_env_var("POSTGRES_USER")

        if postgres_url:
            st.markdown(f"**Step 1:** Open Your Postgres SQL Editor with this information:")
            st.markdown(f"**Host:** {postgres_url}")
            st.markdown(f"**Port:** {postgres_port}")
            st.markdown(f"**Database:** {postgres_db}")
            st.markdown(f"**User:** {postgres_user}")   
            response = True

        return response
    
    def count_site_pages(self):
        """
        Count the total number of records in the site_pages table.
        """
        return self.db_client.count_site_pages()