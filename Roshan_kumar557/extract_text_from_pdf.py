import pdfplumber
from abc import ABC,abstractmethod
import logging 
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ExtractTextPdf(ABC):
    @abstractmethod
    def extract_text_from_pdf(self,pdf_path:str):
        pass
class simpleExtractTextPdf(ExtractTextPdf):
    def extract_text_from_pdf(self,pdf_path:str):
        try:
            if not isinstance(pdf_path,str):
                logging.error("Pdf path is not in string format.")
            else:
                logging.info("Lodding pdf path")
                text = ""
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ''
                return text.strip()
        except ValueError as e:
            logging.error("Check pdf path")
            return None
class ExtractText:
    def __init__(self,strategy:ExtractTextPdf):
        self._strategy=strategy
    def extractTextFromPdf(self,pdf_path:str):
        return self._strategy.extract_text_from_pdf(pdf_path)