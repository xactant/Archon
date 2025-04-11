from archon.db.db_client import DbClient
from utils.env_utils import get_env_var
from .. import DatabaseBase


class SupabaseDatabase(DatabaseBase):
    def __init__(self, db_client: DbClient):
        super().__init__(db_client)
        
    def get_not_setup_message(self):
        """Get the message to display if Supabase is not configured"""
        return "Supabase is not configured. Please set your Supabase URL and Service Key in the Environment tab."
        
    def get_supabase_sql_editor_url(self, supabase_url):
        """Get the URL for the Supabase SQL Editor"""
        try:
            # Extract the project reference from the URL
            # Format is typically: https://<project-ref>.supabase.co
            if '//' in supabase_url and 'supabase' in supabase_url:
                parts = supabase_url.split('//')
                if len(parts) > 1:
                    domain_parts = parts[1].split('.')
                    if len(domain_parts) > 0:
                        project_ref = domain_parts[0]
                        return f"https://supabase.com/dashboard/project/{project_ref}/sql/new"
            
            # Fallback to a generic URL
            return "https://supabase.com/dashboard"
        except Exception:
            return "https://supabase.com/dashboard"

    def show_manual_sql_instructions(self, st, sql, vector_dim, recreate=False):
        """Show instructions for manually executing SQL in Supabase"""
        st.info("### Manual SQL Execution Instructions")
        
        # Provide a link to the Supabase SQL Editor
        supabase_url = get_env_var("SUPABASE_URL")
        if supabase_url:
            dashboard_url = self.get_supabase_sql_editor_url(supabase_url)
            st.markdown(f"**Step 1:** [Open Your Supabase SQL Editor with this URL]({dashboard_url})")
        else:
            st.markdown("**Step 1:** Open your Supabase Dashboard and navigate to the SQL Editor")
        
        st.markdown("**Step 2:** Create a new SQL query")
        
        if recreate:
            st.markdown("**Step 3:** Copy and execute the following SQL:")
            drop_sql = f"DROP FUNCTION IF EXISTS match_site_pages(vector({vector_dim}), int, jsonb);\nDROP TABLE IF EXISTS site_pages CASCADE;"
            st.code(drop_sql, language="sql")
            
            st.markdown("**Step 4:** Then copy and execute this SQL:")
            st.code(sql, language="sql")
        else:
            st.markdown("**Step 3:** Copy and execute the following SQL:")
            st.code(sql, language="sql")
        
        st.success("After executing the SQL, return to this page and refresh to see the updated table status.")
    
    def show_manual_truncate_instructions(self, st):# Replace the vector dimensions in the SQL
        """Show instructions for manually truncating the table in Supabase"""
        st.info("Execute this SQL in your Supabase SQL Editor to clear the table data.")
        
        # Provide a link to the Supabase SQL Editor
        supabase_url = get_env_var("SUPABASE_URL")
        if supabase_url:
            dashboard_url = self.get_supabase_sql_editor_url(supabase_url)
            st.markdown(f"[Open Your Supabase SQL Editor with this URL]({dashboard_url})")    