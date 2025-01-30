import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import uuid4

from app.cache_manager import cache
from app.database import get_session
from app.models import CachedResult
from app.schemas import PayloadRequest, PayloadResponse
from app.utils import transformer_function, generate_hash

# API Router for cache endpoints
router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)


# Endpoint to cache created payload
@router.post("/payload", response_model=dict)
async def create_payload(request: PayloadRequest, session: AsyncSession = Depends(get_session)):
    """
        Create a payload by transforming input lists and caching results.
    """
    # Input Validations
    if not request.list_1 or not request.list_2:
        logger.error("Invalid input: Lists cannot be empty.")
        raise HTTPException(status_code=400, detail="Lists cannot be empty.")

    if len(request.list_1) != len(request.list_2):
        logger.error("Invalid input: Lists must be of the same length.")
        raise HTTPException(status_code=400, detail="Lists must be of the same length.")

    # Get Unique Identifier for the input lists
    input_hash = generate_hash(request.list_1, request.list_2)

    # Check in-memory cache first with the unique identifier
    if input_hash in cache:
        logger.info(f"✅ Cache Hit: Returning cached result for hash {input_hash}")
        return {"id": input_hash}

    async with session.begin():
        # Check if the result is already cached in the database
        result = await session.execute(select(CachedResult).where(CachedResult.input_hash == input_hash))
        cached = result.scalars().first()
        if cached:
            logger.info(f"✅ Database Cache Hit: Found result for hash {input_hash}")
            cache[input_hash] = cached.transformed_output
            return {"id": input_hash}

        # Transform input list if it's not cached in-memory and db
        transformed_1 = [transformer_function(item) for item in request.list_1]
        transformed_2 = [transformer_function(item) for item in request.list_2]
        interleaved = [val for pair in zip(transformed_1, transformed_2) for val in pair]
        transformed_output = ", ".join(interleaved)

        # Store new Payload with input hash to db and update in-memory cache
        new_cache = CachedResult(input_hash=input_hash, transformed_output=transformed_output)
        session.add(new_cache)
        cache[input_hash] = transformed_output

        logger.info(f"✅ New Payload Cached: {input_hash}")

        return {"id": input_hash}


@router.get("/payload/{payload_id}", response_model=PayloadResponse)
async def read_payload(payload_id: str, session: AsyncSession = Depends(get_session)):
    """
         Retrieve a payload by ID from cache or database.
     """
    if payload_id in cache:
        logger.info(f"✅ Cache Hit: Retrieved payload {payload_id} from memory cache")
        return PayloadResponse(output=cache[payload_id])

    async with session.begin():
        cached = await session.get(CachedResult, payload_id)
        if not cached:
            logger.error(f"❌ Payload Not Found: {payload_id}")
            raise HTTPException(status_code=404, detail="Payload not found.")

        cache[payload_id] = cached.transformed_output
        logger.info(f"✅ Database Hit: Retrieved payload {payload_id} from database")
        return PayloadResponse(output=cached.transformed_output)
