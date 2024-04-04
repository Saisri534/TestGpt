from langchain_community.vectorstores.pgvector import PGVector
from components.embedding_model import EmbeddingModel
from utilities.config import DataConstants
from components.data_splitting import DataSplitting
import psycopg2
from logger import logger
from pipeline import Pipelinee


class Retriever:
    @staticmethod
    def get_retriever():
        try:
            splits=Pipelinee.all_splits
            data_constants = DataConstants()
            model = EmbeddingModel.initialize_model()
            retriever = PGVector.from_documents(
                embedding=model,
                documents=splits,
                collection_name=data_constants.collection_name,
                connection_string=data_constants.connection_string,
            ).as_retriever(search_type="similarity", search_kwargs={"k": 3})
            return retriever    

        except Exception as e:
            logger.error(f"Error initializing retriever: {e}")
            return None
            