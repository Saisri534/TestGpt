from utilities.config import DataConstants
from langchain.document_loaders import TextLoader, CSVLoader, PyPDFLoader, UnstructuredPowerPointLoader
from langchain.document_loaders import AsyncHtmlLoader
import os
from logger import logger
import datetime
import requests
from dateutil import parser

class DataLoader:
    @staticmethod
    def get_pdf_modified_date(file_path):
        try:
            # Get the modification timestamp of the file
            modified_timestamp = os.path.getmtime(file_path)
                
            # Convert the timestamp to a datetime object
            modified_datetime = datetime.datetime.fromtimestamp(modified_timestamp)
                
            return modified_datetime
        except Exception as e:
            logger.error(f"Error getting modification date of file '{file_path}': {e}")
            return None
    
    @staticmethod
    def get_url_modified_date(url):
        try:
            response = requests.head(url)
            last_modified = response.headers.get('Last-Modified')
            last_modified_date = parser.parse(last_modified)
            return last_modified_date
        except Exception as e:
            logger.error(f"Error getting modification date of file '{url}': {e}")
            return None
    
    @staticmethod
    def load_text_doc(file_path):
        try:
            loader = TextLoader(file_path)
            data = loader.load()
            date= DataLoader.get_pdf_modified_date(file_path)
        except Exception as e:
            logger.error(f"Error loading text doc '{filename}': {e}")
        return data,date

    @staticmethod
    def load_csv(file_path):
        try:
            loader = CSVLoader(file_path)
            data = loader.load()
            date= DataLoader.get_pdf_modified_date(file_path)
        except Exception as e:
            logger.error(f"Error loading csv '{filename}': {e}")
        return data,date

    @staticmethod
    def load_pdf(file_path):
        try:
            loader = PyPDFLoader(file_path)
            data = loader.load()
            date= DataLoader.get_pdf_modified_date(file_path)
        except Exception as e:
            logger.error(f"Error loading Pdf '{filename}': {e}")
        return data,date

    @staticmethod
    def load_ppt(file_path):
        try:
            loader = UnstructuredPowerPointLoader(file_path)
            data = loader.load()
            date= DataLoader.get_pdf_modified_date(file_path)
        except Exception as e:
            logger.error(f"Error loading PowerPoint '{filename}': {e}")
        return data,date
    
    @staticmethod
    def web_scrapping(url):
        try:
            loader=AsyncHtmlLoader(url)
            data=loader.load()
            date=DataLoader.get_url_modified_date(url)
        except Exception as e:
            logger.error(f"Error loading URL '{url}': {e}")
        return data,date



