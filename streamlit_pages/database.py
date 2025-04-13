import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from archon.db.db_client import DbClient
from utils.utils import get_env_var
from database_subpages.database_subpages_factory import DatabaseSubpagesFactory
@st.cache_data
def load_sql_template():
    """Load the SQL template file and cache it"""
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "utils", "site_pages.sql"), "r") as f:
        return f.read()

def get_database_subpages(db_client: DbClient):
    factory = DatabaseSubpagesFactory(db_client)
    return factory.get_subpage('database')

def database_tab(db_client: DbClient):
    """Display the database configuration interface"""
    st.header("Database Configuration")
    st.write("Set up and manage your database tables for Archon.")
    
    db_subpage = get_database_subpages(db_client)

    # Check if DB Client is configured
    if not db_client:
        st.error(db_subpage.get_not_setup_message())
        return

    # Site Pages Table Setup
    st.subheader("Site Pages Table")
    st.write("This table stores web page content and embeddings for semantic search.")
    
    # Add information about the table
    with st.expander("About the Site Pages Table", expanded=False):
        st.markdown("""
        This table is used to store:
        - Web page content split into chunks
        - Vector embeddings for semantic search
        - Metadata for filtering results
        
        The table includes:
        - URL and chunk number (unique together)
        - Title and summary of the content
        - Full text content
        - Vector embeddings for similarity search
        - Metadata in JSON format
        
        It also creates:
        - A vector similarity search function
        - Appropriate indexes for performance
        - Row-level security policies
        """)
    
    # Check if the table already exists
    table_exists = False
    table_has_data = False
    
    try:
        # Try to query the table to see if it exists
        table_exists = db_subpage.check_table_exists()
        
        if table_exists:
            # Check if the table has data
            count_response = db_subpage.count_site_pages()
            row_count = count_response.count
            table_has_data = row_count > 0
            
            st.success("✅ The site_pages table already exists in your database.")

            if table_has_data:
                st.info(f"The table contains data ({row_count} rows).")
            else:
                st.info("The table exists but contains no data.")
        else:
            st.info("The site_pages table does not exist yet. You can create it below.")
    except Exception as e:
        error_str = str(e)
        if "relation" in error_str and "does not exist" in error_str:
            st.info("The site_pages table does not exist yet. You can create it below.")
        else:
            st.error(f"Error checking table status: {error_str}")
            st.info("Proceeding with the assumption that the table needs to be created.")
        table_exists = False
    
    # Vector dimensions selection
    st.write("### Vector Dimensions")
    st.write("Select the embedding dimensions based on your embedding model:")
    
    vector_dim = st.selectbox(
        "Embedding Dimensions",
        options=[1536, 768, 384, 1024],
        index=0,
        help="Use 1536 for OpenAI embeddings, 768 for nomic-embed-text with Ollama, or select another dimension based on your model."
    )
    
    # Get the SQL with the selected vector dimensions
    sql_template = load_sql_template()
    
    # Replace the vector dimensions in the SQL
    sql = db_subpage.get_site_pages_sql(sql_template, vector_dim)
    
    # Show the SQL
    with st.expander("View SQL", expanded=False):
        st.code(sql, language="sql")
    
    # Create table button
    if not table_exists:
        if st.button("Get Instructions for Creating Site Pages Table"):
            db_subpage.show_manual_sql_instructions(st, sql, vector_dim)
    else:
        # Option to recreate the table or clear data
        col1, col2 = st.columns(2)
        
        with col1:
            st.warning("⚠️ Recreating will delete all existing data.")
            if st.button("Get Instructions for Recreating Site Pages Table"):
                db_subpage.show_manual_sql_instructions(st, sql, vector_dim, recreate=True)
        
        with col2:
            if table_has_data:
                st.warning("⚠️ Clear all data but keep structure.")
                if st.button("Clear Table Data"):
                    try:
                        with st.spinner("Clearing table data..."):
                            # Use the DB client to delete all rows
                            response = db_subpage.clear_site_pages()
                            st.success("✅ Table data cleared successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error clearing table data: {str(e)}")
                        # Fall back to manual SQL
                        truncate_sql = "TRUNCATE TABLE site_pages;"
                        st.code(truncate_sql, language="sql")

                        db_subpage.show_manual_truncate_instructions(st) 