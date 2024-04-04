from components.data_extraction import DataLoader
from utilities.config import DataConstants
from components.data_splitting import DataSplitting
from database.database_operation import DatabaseOperation
from components.data_deduplication import DataDeduplication
from langchain.document_transformers import Html2TextTransformer
from logger import logger
import os


class Pipelinee:
    all_splits=[]
    @staticmethod
    def run_pipelinee():
        try:
            DatabaseOperation.connect_and_create_table()
            data_constants = DataConstants()
            deduplication = DataDeduplication()
            all_unique_chunks = [] 
            for filename in os.listdir(data_constants.folder_path):
                file_path = os.path.join(data_constants.folder_path,filename)
                if os.path.isfile(file_path):
                    if filename.endswith('.txt'):
                        unique_chunks = []
                        data,date=DataLoader.load_text_doc(file_path)
                        splits = DataSplitting.split_text(data, data_constants.max_chunk_size)
                        Pipelinee.all_splits.append(splits)
                        unique_chunks = deduplication.deduplicate_chunks(splits, date)
                        print(len(unique_chunks))

                    elif filename.endswith('.pptx'):
                        unique_chunks= []
                        data,date=DataLoader.load_ppt(file_path)
                        splits = DataSplitting.split_text(data, data_constants.max_chunk_size)
                        Pipelinee.all_splits.append(splits)
                        unique_chunks = deduplication.deduplicate_chunks(splits, date)
                        print(len(unique_chunks))
 
                    elif filename.endswith('.pdf'):
                        unique_chunks = []
                        data,date=DataLoader.load_pdf(file_path)
                        splits = DataSplitting.split_text(data, data_constants.max_chunk_size)
                        Pipelinee.all_splits.append(splits)
                        unique_chunks = deduplication.deduplicate_chunks(splits, date)
                        print(len(unique_chunks))
                       
                    elif filename.endswith('.csv'):
                        unique_chunks = []
                        data,date=DataLoader.load_csv(file_path)
                        splits = DataSplitting.split_text(data, data_constants.max_chunk_size)
                        Pipelinee.all_splits.append(splits)
                        unique_chunks = deduplication.deduplicate_chunks(splits, date)
                        print(len(unique_chunks))
               
                    else:
                        logger.error("Unsupported file type:", filename)  
            
            url=data_constants.URL
            data,date=DataLoader.web_scrapping(url)
            html2text = Html2TextTransformer()
            data_transformed= html2text.transform_documents(data)
            splits = DataSplitting.split_text(data_transformed, data_constants.max_chunk_size)
            Pipelinee.all_splits.append(splits)
            unique_chunks = deduplication.deduplicate_chunks(splits, date)

            DatabaseOperation.store_data(unique_chunks)  
            logger.info("Pipeline successfully executed")
        
        except Exception as e:
            logger.error(f"Error in pipeline execution: {e}")
