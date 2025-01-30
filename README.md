# Python Backend: Caching Service

## Overview
FastAPI Cache Service is a high-performance caching layer built using FastAPI, SQLModel, and cachetools. It provides an API to store and retrieve cached payloads efficiently.

## Features
- **FastAPI-based API** for handling payloads
- **In-memory caching** using `cachetools.TTLCache`
- **Persistent caching** with PostgreSQL and SQLModel
- **Dockerized environment** for easy deployment
- **Comprehensive unit and integration tests**

## Installation
### Prerequisites
- Python 3.8+
- Docker & Docker Compose

### Steps 
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd fastapi-cache-service

#### Using Virtual Environment (Recommended)
2. To keep dependencies isolated, create and activate a virtual environment:

```bash
  python -m venv cache_service_env
  source cache_service_env/bin/activate  # On Windows use: venv\Scripts\activate
```
3. Install dependencies:    
 ```bash 
    pip install -r requirements.txt
```
4. This Servive uses PostgresSQL. Make sure you've the postgres running locally or in a container.
5. Make sure you've the right variables setup in the `.env ` file
6. Running the service 
```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
7. Running the tests
```bash
   pytest tests/
```
### Running with docker

```shell
   docker-compose up --build
```
