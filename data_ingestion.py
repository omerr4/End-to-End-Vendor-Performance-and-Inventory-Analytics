"""
Data Ingestion Module
---------------------
This script automates the ingestion of large CSV datasets into a local SQLite database.
It utilizes chunking to optimize memory usage and handles basic logging for monitoring.
"""

import pandas as pd
import os
import time
import logging
from sqlalchemy import create_engine

# Setup logging configuration
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename='logs/data_ingestion.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

def ingest_data_in_chunks(csv_file_path, table_name, engine, chunk_size=100000):
    """
    Reads a CSV file in chunks and loads it into an SQLite database.
    """
    first_chunk = True
    for chunk in pd.read_csv(csv_file_path, chunksize=chunk_size, low_memory=False):
        if first_chunk:
            chunk.to_sql(table_name, con=engine, if_exists='replace', index=False)
            first_chunk = False
        else:
            chunk.to_sql(table_name, con=engine, if_exists='append', index=False)
        
        logging.info(f"Inserted {len(chunk)} rows into {table_name}.")

def load_raw_data(data_directory='data', db_name='sqlite:///inventory.db'):
    """
    Scans the data directory for CSV files and processes them into the database.
    """
    start_time = time.time()
    engine = create_engine(db_name)
    files_processed = 0
    
    for root, dirs, files in os.walk(data_directory):
        for file in files:
            # Exclude hidden system files (e.g., macOS '._' files)
            if file.endswith('.csv') and not file.startswith('._'):
                file_path = os.path.join(root, file)
                table_name = file[:-4]
                
                logging.info(f"Starting ingestion for: {file}")
                print(f"Processing {file} into table '{table_name}'...")
                
                try:
                    ingest_data_in_chunks(file_path, table_name, engine)
                    logging.info(f"Successfully loaded {file}")
                    files_processed += 1
                except Exception as e:
                    logging.error(f"Error loading {file}: {e}")
                    print(f"Failed to process {file}: {e}")
                    
    total_time = (time.time() - start_time) / 60
    logging.info(f"Ingestion completed. Total time: {total_time:.2f} minutes.")
    print(f"\nIngestion Complete! Processed {files_processed} files in {total_time:.2f} minutes.")

if __name__ == '__main__':
    load_raw_data()