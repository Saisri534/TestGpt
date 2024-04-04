import hashlib
from database.database_operation import DatabaseOperation
from logger import logger

class DataDeduplication:
    def __init__(self):
        self.unique_chunks = []

    def calculate_hash(self, text):
        """Calculate a hash for a given text."""
        try:
            return hashlib.md5(text.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash: {e}")
            return None

    def deduplicate_chunks(self, splits, date):
        """Perform data deduplication on a list of text splits."""
        try:
            for splt in splits:
                split_content=splt.page_content
                split_hash = self.calculate_hash(split_content)
                if split_hash is not None:
                    exist = DatabaseOperation.is_hash_in_database(split_hash)
                    if not exist:
                        DatabaseOperation.insert_data(split_hash, date, split_content)
                        self.unique_chunks.append(splt)
            logger.info("Unique hash values are pushed into hash_table")
            return self.unique_chunks
        except Exception as e:
            logger.error(f"Error deduplicating chunks: {e}")
            return []
