from typing import Union, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
import os
from typing import Optional
from datetime import datetime
from redis import Redis
import json
import time


# Environment variables for database connection
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
REDIS_HOST = os.getenv('REDIS_HOST','redis')
REDIS_PORT = os.getenv('REDIS_PORT','6379')

# Create the database connection string
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
app = FastAPI()


# Set up SQLAlchemy
engine = create_engine(DATABASE_URL)
metadata = MetaData()
crawl_table = Table("crawl", metadata, autoload_with=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

redis_client = Redis(host=REDIS_HOST,port=REDIS_PORT,db=0)

@app.get("/")
def read_root():
    return {"message": "Helloo_world"}

# Define the Pydantic model for response
class CrawlResponse(BaseModel):
    urlkey: Optional[str]
    timestamp: Optional[datetime]
    url: Optional[str]
    mime: Optional[str]
    mime_detected: Optional[str] = Field(alias='mime-detected')
    status: Optional[int]
    digest: Optional[str]
    length: Optional[int]
    offset: Optional[int]
    filename: Optional[str]
    redirect: Optional[str]  
    charset: Optional[str]
    languages: Optional[str]

    class Config:
        allow_population_by_field_name = True


def json_serializer(data):
    return json.dumps(data, default=lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if isinstance(x, datetime) else x)

# Endpoint to get data by urlkey
@app.get("/crawl/{urlkey}", response_model=List[CrawlResponse])
async def get_data_by_urlkey(urlkey: str):
    start_time = time.perf_counter()
    session = SessionLocal()
    try:
        cached_data = redis_client.get(urlkey)

        if cached_data:
            duration = time.perf_counter() - start_time
            print(f"Time taken with cache: {duration} seconds")
            return json.loads(cached_data)

        # Execute the query and get the first result
        results = session.query(crawl_table).filter(crawl_table.c.urlkey == urlkey).all()


        if not results:
            raise HTTPException(status_code=404, detail="Data not found for the provided urlkey")

        # Convert SQLAlchemy result to dictionary
        data_list =  [{column.name:getattr(result, column.name) for column in crawl_table.columns} for result in results]

        redis_client.set(urlkey,json_serializer(data_list))
        duration = time.perf_counter() - start_time
        print(f"Time taken without cache: {duration} seconds")


        return data_list


    finally:
        session.close()

# New endpoint to get data by status
@app.get("/crawl/status/{status}", response_model=List[CrawlResponse])
async def get_data_by_status(status: int):
    session = SessionLocal()
    try:
        # Execute the query and get all results for the given status
        results = session.query(crawl_table).filter(crawl_table.c.status == status).all()

        if not results:
            raise HTTPException(status_code=404, detail="No data found for the provided status")

        # Convert SQLAlchemy results to a list of dictionaries
        return [{column.name: getattr(result, column.name) for column in crawl_table.columns} for result in results]

    finally:
        session.close()
