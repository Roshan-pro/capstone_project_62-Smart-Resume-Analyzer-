import pdfplumber
from abc import ABC,abstractmethod
class ExtractTextPdf(ABC):
    @abstractmethod
    def extract_text_from_pdf(self,pdf_path:str):
        pass
class simpleExtractTextPdf(ExtractTextPdf):
    def extract_text_from_pdf(self,pdf_path:str):
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ''
        return text.strip()
# def extract_text_from_pdf(pdf_path):
#     text = ""
#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             text += page.extract_text() or ''
#     return text.strip()
class ExtractText:
    def __init__(self,strategy:ExtractTextPdf):
        self._strategy=strategy
    def extractTextFromPdf(self,pdf_path:str):
        return self._strategy.extract_text_from_pdf(pdf_path)