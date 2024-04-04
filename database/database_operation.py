from langchain_community.vectorstores.pgvector import PGVector
from components.embedding_model import EmbeddingModel
from utilities.config import DataConstants
from components.data_splitting import DataSplitting
import psycopg2
from logger import logger

class DatabaseOperation:
    @staticmethod
    def store_data(splits):
        try:
            data_constants = DataConstants()
            model = EmbeddingModel.initialize_model()
            db = PGVector.from_documents(
                embedding=model,
                documents=splits,
                collection_name=data_constants.collection_name,
                connection_string=data_constants.connection_string,
            )
            logger.info("Successfully pushed embeddings into pgvector")
        except Exception as e:
            logger.error(f"Error storing data: {e}")
    
    @staticmethod
    def connect_and_create_table():
        try:
            data_constants = DataConstants()
            DB_NAME = data_constants.db_name
            DB_USER = data_constants.db_user
            DB_PASSWORD = data_constants.db_password
            DB_HOST = data_constants.db_host

            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST
            )
            cur = conn.cursor()

            create_table_query = '''
            CREATE TABLE IF NOT EXISTS hash_data (
                id SERIAL PRIMARY KEY,
                hash_value VARCHAR(100),
                date_modified TIMESTAMP,
                chunk_data TEXT
            );
            '''
            cur.execute(create_table_query)
            conn.commit()

            cur.close()
            conn.close()
            logger.info("Table created successfully.")
        except Exception as e:
            logger.error(f"Error connecting and creating table: {e}")

    @staticmethod
    def insert_data(hash_value, date_modified, chunk_data):
        try:
            data_constants = DataConstants()
            DB_NAME = data_constants.db_name
            DB_USER = data_constants.db_user
            DB_PASSWORD = data_constants.db_password
            DB_HOST = data_constants.db_host

            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST
            )
            cur = conn.cursor()

            insert_query = '''
            INSERT INTO hash_data (hash_value, date_modified, chunk_data)
            VALUES (%s, %s, %s)
            '''
            cur.execute(insert_query, (hash_value, date_modified, chunk_data))
            conn.commit()

            cur.close()
            conn.close()
            logger.info("Data inserted successfully.")
        except Exception as e:
            logger.error(f"Error inserting data: {e}")

    @staticmethod
    def is_hash_in_database(hash_value):
        try:
            data_constants = DataConstants()
            DB_NAME = data_constants.db_name
            DB_USER = data_constants.db_user
            DB_PASSWORD = data_constants.db_password
            DB_HOST = data_constants.db_host

            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST
            )
            cur = conn.cursor()

            query = "SELECT hash_value FROM hash_data WHERE hash_value = %s"
            cur.execute(query, (hash_value,))
            result = cur.fetchone()

            cur.close()
            conn.close()

            return result is not None
        except Exception as e:
            logger.error(f"Error checking hash in database: {e}")
            return False
