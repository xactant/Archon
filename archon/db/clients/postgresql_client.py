from typing import Dict, List, Any, Optional, Union
import asyncio
import asyncpg
import json

from archon.db.db_client import DbClient
from archon.db.models import ProcessedChunk
from utils.env_utils import write_to_log


class PostgreSqlClient(DbClient):
    """
    PostgreSQL implementation of the DbClient interface.
    
    This class provides concrete implementations of database operations
    using PostgreSQL as the backend.
    """
    
    def __init__(self, connection_pool: asyncpg.Pool):
        """
        Initialize the PostgreSqlClient with a connection pool.
        
        Args:
            connection_pool: An initialized asyncpg connection pool
        """
        super().__init__('postgresql')
        self.pool = connection_pool
        self._current_db = None
        self._loop = None
    
    def _get_event_loop(self):
        """Get or create an event loop for async operations."""
        if self._loop is None:
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop
    
    def which_db(self):
        """Get the current database name synchronously."""
        if self._current_db is None:
            try:
                # Get the event loop
                loop = self._get_event_loop()
                
                # Run the async operation in a new loop if the current one is running
                if loop.is_running():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    self._current_db = new_loop.run_until_complete(self._which_db())
                    asyncio.set_event_loop(loop)  # Restore original loop
                else:
                    self._current_db = loop.run_until_complete(self._which_db())
            except Exception as e:
                print(f"Error retrieving database name: {e}")
                write_to_log(f"Error retrieving database name: {e}")
                self._current_db = []
        
        print(f"Current database: {self._current_db}")
        return self._current_db
    
    async def _which_db(
            self,
            source: str = 'pydantic_ai_docs'
        ) -> List[str]:
        try:
            # Query for current database
            sql = """
            SELECT current_database();
            """
            
            # Execute query
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(sql)
                
                # Extract the database name
                db_names = [row['current_database'] for row in rows]
                return db_names
        except Exception as e:
            print(f"Error retrieving database name: {e}")
            write_to_log(f"Error retrieving database name: {e}")
            return []
    
    async def match_site_pages(
        self, 
        query_embedding: List[float], 
        match_count: int, 
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find pages that match the given query embedding using vector similarity search.
        
        Args:
            query_embedding: A vector embedding of the user's query
            match_count: Number of matches to return
            filter: Optional filter criteria, e.g. {'source': 'pydantic_ai_docs'}
            
        Returns:
            List of matching documents/pages with their metadata
        """
        try:
            # Build the SQL query with vector similarity search using cosine distance
            sql = """
            SELECT 
                id, url, chunk_number, title, summary, content, metadata,
                1 - (embedding <=> $1) as similarity
            FROM site_pages
            """
            
            # Add filter conditions if provided
            params = [query_embedding]
            if filter and 'source' in filter:
                sql += " WHERE metadata->>'source' = $2"
                params.append(filter['source'])
            
            # Add ordering and limit
            sql += """
            ORDER BY similarity DESC
            LIMIT ${}
            """.format(len(params) + 1)
            
            params.append(match_count)
            
            # Execute the query
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(sql, *params)
                
                # Convert rows to dictionaries
                result = []
                for row in rows:
                    # Convert Row to dict and ensure metadata is properly parsed
                    row_dict = dict(row)
                    if isinstance(row_dict['metadata'], str):
                        row_dict['metadata'] = json.loads(row_dict['metadata'])
                    result.append(row_dict)
                
                return result
        except Exception as e:
            print(f"Error in match_site_pages: {e}")
            write_to_log(f"Error in match_site_pages: {e}")
            return []
    
    async def insert_chunk(
        self,
        chunk: ProcessedChunk
    ) -> Union[Dict[str, Any], None]:
        """
        Insert a processed document chunk into the database.
        
        Args:
            chunk: A ProcessedChunk object containing all data for the document chunk
            
        Returns:
            Result of the insert operation, or None if an error occurred
        """
        try:
            # Insert the chunk into the database
            sql = """
            INSERT INTO site_pages(url, chunk_number, title, summary, content, metadata, embedding)
            VALUES($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
            """
            
            # Insert with asyncpg
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    sql, 
                    chunk.url,
                    chunk.chunk_number,
                    chunk.title,
                    chunk.summary,
                    chunk.content,
                    json.dumps(chunk.metadata),
                    chunk.embedding
                )
                
                # Return the inserted row with ID
                if row:
                    return {
                        "id": row['id'],
                        "url": chunk.url,
                        "chunk_number": chunk.chunk_number,
                        "title": chunk.title,
                        "summary": chunk.summary,
                        "content": chunk.content,
                        "metadata": chunk.metadata,
                        "embedding": chunk.embedding
                    }
                return None
        except Exception as e:
            print(f"Error inserting chunk: {e}")
            write_to_log(f"Error inserting chunk: {e}")
            return None
    
    async def list_documentation_pages(
        self,
        source: str = 'pydantic_ai_docs'
    ) -> List[str]:
        """
        Retrieve a list of all available documentation pages for a specific source.
        
        Args:
            source: The source identifier for the documentation pages (default: 'pydantic_ai_docs')
            
        Returns:
            List of unique URLs for all documentation pages from the specified source
        """
        try:
            # Query for unique URLs
            sql = """
            SELECT DISTINCT url
            FROM site_pages
            WHERE metadata->>'source' = $1
            """
            
            # Execute query
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(sql, source)
                
                # Extract URLs
                urls = [row['url'] for row in rows]
                return urls
        except Exception as e:
            print(f"Error listing documentation pages: {e}")
            write_to_log(f"Error listing documentation pages: {e}")
            return []
    
    async def get_page_content(
        self,
        url: str,
        source: str = 'pydantic_ai_docs'
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the content of a specific documentation page by URL.
        
        Args:
            url: The URL of the page to retrieve
            source: The source identifier for the documentation (default: 'pydantic_ai_docs')
            
        Returns:
            List of page chunks with title, content, and chunk_number, ordered by chunk_number
        """
        try:
            # Query for page content
            sql = """
            SELECT title, content, chunk_number
            FROM site_pages
            WHERE url = $1 AND metadata->>'source' = $2
            ORDER BY chunk_number
            """
            
            # Execute query
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(sql, url, source)
                
                # Convert to dictionaries
                result = []
                for row in rows:
                    result.append(dict(row))
                
                return result
        except Exception as e:
            print(f"Error retrieving page content: {e}")
            write_to_log(f"Error retrieving page content: {e}")
            return []
    
    async def count_site_pages(self) -> int:
        """
        Count the total number of records in the site_pages table.
        
        Returns:
            The exact count of records in the site_pages table
        """
        try:
            # Query for count
            sql = "SELECT COUNT(*) FROM site_pages"
            
            # Execute query
            async with self.pool.acquire() as conn:
                count = await conn.fetchval(sql)
                return count
        except Exception as e:
            print(f"Error counting site pages: {e}")
            write_to_log(f"Error counting site pages: {e}")
            return 0
    
    async def check_table_exists(self) -> bool:
        """
        Check if the site_pages table exists and has at least one record.
        
        Returns:
            True if the table exists and has at least one record, False otherwise
        """
        try:
            # First check if the table exists in the schema
            sql = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'site_pages'
            )
            """
            
            # Execute query
            async with self.pool.acquire() as conn:
                exists = await conn.fetchval(sql)
                if not exists:
                    return False
                
                # If table exists, check if it has any records
                has_records = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM site_pages LIMIT 1)")
                return has_records
        except Exception as e:
            print(f"Error checking if table exists: {e}")
            write_to_log(f"Error checking if table exists: {e}")
            return False
    
    async def clear_site_pages(self, exclude_ids: Optional[List[int]] = None) -> Union[Dict[str, Any], None]:
        """
        Clear all records from the site_pages table, optionally excluding specific IDs.
        
        Args:
            exclude_ids: Optional list of record IDs to exclude from deletion
            
        Returns:
            Result of the deletion operation, or None if an error occurred
        """
        try:
            sql = "DELETE FROM site_pages"
            params = []
            
            # Add condition to exclude specific IDs
            if exclude_ids and len(exclude_ids) > 0:
                sql += " WHERE id NOT IN ("
                placeholders = []
                for i, _ in enumerate(exclude_ids):
                    placeholders.append(f"${i+1}")
                    params.append(_)
                sql += ", ".join(placeholders) + ")"
            
            # Execute query
            async with self.pool.acquire() as conn:
                # Get the count of rows that will be deleted
                count_sql = "SELECT COUNT(*) FROM site_pages"
                if exclude_ids and len(exclude_ids) > 0:
                    count_sql += " WHERE id NOT IN ("
                    count_sql += ", ".join([str(id) for id in exclude_ids]) + ")"
                
                count = await conn.fetchval(count_sql)
                
                # Execute the delete
                await conn.execute(sql, *params)
                
                return {"deleted": count}
        except Exception as e:
            print(f"Error clearing site pages: {e}")
            write_to_log(f"Error clearing site pages: {e}")
            return None
    
    async def clear_by_source(self, source: str) -> Union[Dict[str, Any], None]:
        """
        Clear all records with a specific source from the site_pages table.
        
        Args:
            source: The source identifier to clear (e.g., 'pydantic_ai_docs')
            
        Returns:
            Result of the deletion operation, or None if an error occurred
        """
        try:
            # Query to delete records with a specific source
            sql = "DELETE FROM site_pages WHERE metadata->>'source' = $1"
            
            # Execute query
            async with self.pool.acquire() as conn:
                # Get the count of rows that will be deleted
                count = await conn.fetchval("SELECT COUNT(*) FROM site_pages WHERE metadata->>'source' = $1", source)
                
                # Execute the delete
                await conn.execute(sql, source)
                
                return {"deleted": count}
        except Exception as e:
            print(f"Error clearing by source: {e}")
            write_to_log(f"Error clearing by source: {e}")
            return None
        
    async def client_configured(self) -> bool:
        """
        Check if the database client is configured.
        
        Returns:
            True if the client is configured, False otherwise
        """
        try:
            # Check if the connection pool is initialized
            return self.pool is not None
        except Exception as e:
            print(f"Error checking client configuration: {e}")
            write_to_log(f"Error checking client configuration: {e}")
            return False
        
    async def get_example_data(self, source: str, limit: int) -> List[Dict[str, Any]]:
        """
        Get example data from the database.
        
        Args:
            source: The source identifier for the example data
            
        Returns:
            List of example data records
        """
        sql = f"""
            SELECT 
                url, title, summary, chunk_number
            FROM site_pages
            WHERE metadata->>'source' = $1
            LIMIT $2
            """ 
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(sql, source, limit)
                
                # Convert rows to dictionaries
                result = []
                for row in rows:
                    result.append(dict(row))
                
                return result
        except Exception as e:
            print(f"Error retrieving example data: {e}")
            write_to_log(f"Error retrieving example data: {e}")
            return []
        