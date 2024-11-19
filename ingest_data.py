import pandas as pd
import os
from sqlalchemy import create_engine

# Define the local JSON file path
LOCAL_JSON_FILE = "data.json"  # Change this to your actual JSON file path
DB_TABLE = "crawl"
POSTGRES_USER =os.getenv('POSTGRES_USER') 
POSTGRES_PASSWORD =os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB =os.getenv('POSTGRES_DB')

def main():
    # Read the JSON data into a DataFrame
    df = pd.read_json(LOCAL_JSON_FILE)

    # Create a SQLAlchemy engine for PostgreSQL
    db_uri = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/{POSTGRES_DB}"

    engine = create_engine(db_uri)
    # Insert the DataFrame into the PostgreSQL table
    df.to_sql(DB_TABLE, engine, if_exists='append', index=False)

    print("Data ingested successfully!")
if __name__ == "__main__":
    main()
