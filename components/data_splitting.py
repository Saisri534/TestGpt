from utilities.config import max_chunk_size
from logger import logger
from langchain.text_splitter import SpacyTextSplitter

class DataSplitting:
    @staticmethod
    def split_text(data , max_chunk_size):
        try:
            # Initialize SpacyTextSplitter with chunk size
            text_splitter = SpacyTextSplitter(chunk_size=max_chunk_size)
            docs = text_splitter.split_documents(data)
            return docs
        except Exception as e:
            logger.error(f"Error occurred while splitting documents: {e}")
            return []

