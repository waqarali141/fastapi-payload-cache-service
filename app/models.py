from sqlmodel import SQLModel, Field
from uuid import uuid4


# Cached Result DB class to store and retrieve payload from database
class CachedResult(SQLModel, table=True):
    input_hash: str = Field(primary_key=True)
    transformed_output: str
