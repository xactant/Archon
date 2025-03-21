from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
# from supabase import Client
import psycopg2
import psycopg2.extras
from psycopg2 import sql, connect
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.utils import get_env_var

embedding_model = get_env_var('EMBEDDING_MODEL') or 'text-embedding-3-small'

async def get_embedding(text: str, embedding_client: AsyncOpenAI) -> List[float]:
    """Get embedding vector from OpenAI."""
    try:
        response = await embedding_client.embeddings.create(
            model=embedding_model,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return [0] * 1536  # Return zero vector on error

async def retrieve_relevant_documentation_tool(pg_conn: connect, embedding_client: AsyncOpenAI, user_query: str) -> str:
    try:
        # Get the embedding for the query
        query_embedding = await get_embedding(user_query, embedding_client)
        
        # Query Supabase for relevant documents
        # result = supabase.rpc(
        #     'match_site_pages',
        #     {
        #         'query_embedding': query_embedding,
        #         'match_count': 4,
        #         'filter': {'source': 'pydantic_ai_docs'}
        #     }
        #).execute()
        # Query PostgreSQL for relevant documents using vector similarity
        cursor = pg_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Using PostgreSQL's vector extension for similarity search
        #query = """
        #SELECT title, content
        #FROM site_pages, 
        #     (SELECT embedding <=> %s::vector AS distance) AS distance
        #WHERE metadata::jsonb->>'source' = 'pydantic_ai_docs'
        #ORDER BY distance ASC
        #LIMIT 5
        #"""
        source_val = 'pydantic_ai_docs'

        query = "SELECT title, content, embedding <=> '" + str(query_embedding) + "' AS distance " \
            "FROM site_pages WHERE metadata->>'source' = '" + source_val + "' " \
            "ORDER BY distance LIMIT 5"
        
        cursor.execute(query, (query_embedding,))
        result = cursor.fetchall()
        cursor.close()
        if not result: # .data:
            return "No relevant documentation found."
            
        # Format the results
        formatted_chunks = []
        for doc in result: #.data:
            chunk_text = f"""
# {doc['title']}

{doc['content']}
"""
            formatted_chunks.append(chunk_text)
            
        # Join all chunks with a separator
        return "\n\n---\n\n".join(formatted_chunks)
        
    except Exception as e:
        print(f"Error retrieving documentation: {e}")
        return f"Error retrieving documentation: {str(e)}" 

async def list_documentation_pages_tool(pg_conn: connect) -> List[str]:
    """
    Function to retrieve a list of all available Pydantic AI documentation pages.
    This is called by the list_documentation_pages tool and also externally
    to fetch documentation pages for the reasoner LLM.
    
    Returns:
        List[str]: List of unique URLs for all documentation pages
    """
    try:
        # Query Supabase for unique URLs where source is pydantic_ai_docs
        #result = supabase.from_('site_pages') \
        #    .select('url') \
        #    .eq('metadata->>source', 'pydantic_ai_docs') \
        #    .execute()
                # Query PostgreSQL for unique URLs where source is pydantic_ai_docs
        cursor = pg_conn.cursor()
        query = "SELECT DISTINCT url FROM site_pages WHERE metadata::jsonb->>'source' = 'pydantic_ai_docs'"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()

        if not result: #.data:
            return []
            
        # Extract unique URLs
        # urls = sorted(set(doc['url'] for doc in result.data))
        urls = sorted(set(row[0] for row in result))
        return urls
        
    except Exception as e:
        print(f"Error retrieving documentation pages: {e}")
        return []

async def get_page_content_tool(pg_conn: connect, url: str) -> str:
    """
    Retrieve the full content of a specific documentation page by combining all its chunks.
    
    Args:
        ctx: The context including the PostgreSql client
        url: The URL of the page to retrieve
        
    Returns:
        str: The complete page content with all chunks combined in order
    """
    try:
        # Query Supabase for all chunks of this URL, ordered by chunk_number
        #result = supabase.from_('site_pages') \
        #    .select('title, content, chunk_number') \
        #    .eq('url', url) \
        #    .eq('metadata->>source', 'pydantic_ai_docs') \
        #    .order('chunk_number') \
        #    .execute()
        
        # Query PostgreSQL for all chunks of this URL, ordered by chunk_number
        cursor = pg_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = """
        SELECT title, content, chunk_number 
        FROM site_pages 
        WHERE url = %s AND metadata::jsonb->>'source' = 'pydantic_ai_docs' 
        ORDER BY chunk_number
        """
        cursor.execute(query, (url,))
        result = cursor.fetchall()
        cursor.close()

        if not result: #.data:
            return f"No content found for URL: {url}"
            
        # Format the page with its title and all chunks
        # page_title = result.data[0]['title'].split(' - ')[0]  # Get the main title
        page_title = result[0]['title'].split(' - ')[0]  # Get the main title
        formatted_content = [f"# {page_title}\n"]
        
        # Add each chunk's content
        for chunk in result: # .data:
            formatted_content.append(chunk['content'])
            
        # Join everything together but limit the characters in case the page is massive (there are a coule big ones)
        # This will be improved later so if the page is too big RAG will be performed on the page itself
        return "\n\n".join(formatted_content)[:20000]
        
    except Exception as e:
        print(f"Error retrieving page content: {e}")
        return f"Error retrieving page content: {str(e)}"
