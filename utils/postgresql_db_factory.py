import os
import sys
import psycopg2

class PostgresqlDbFactory:
    def createClient(self):
        dbConn = None
        try:
            # Initialize PostgreSQL connection
            dbConn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("POSTGRES_HOST"),
                port=os.getenv("POSTGRES_PORT")
            )
        except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                sys.exit(1)

        return dbConn
    
def create_postgresql_db_connection():
    return PostgresqlDbFactory()