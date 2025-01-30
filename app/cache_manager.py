from cachetools import TTLCache

# In-memory cache with a time-to-live (TTL) of 10 minutes
cache = TTLCache(maxsize=1000, ttl=600)
