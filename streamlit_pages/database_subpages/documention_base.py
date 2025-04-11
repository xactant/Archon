from abc import ABC, abstractmethod
from archon.db.db_client import DbClient

class DocumentationBase:
    def __init__(self, db_client: DbClient):
        self.db_client = db_client