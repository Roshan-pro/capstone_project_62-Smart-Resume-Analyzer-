import string
import contractions
from sklearn.preprocessing import LabelEncoder
from bs4 import BeautifulSoup
import re
import nltk
import pandas as pd 
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

from abc import ABC,abstractmethod
nltk.download('stopwords')
nltk.download('wordnet')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
class CleanTextStrategy(ABC):
    @abstractmethod
    def clean_text(self):
        pass
class SimpleCleanText(CleanTextStrategy):
    def __init__(self,text:str):
        self.text=text
    def clean_text(self):
        try:
            if self.text:
                text=BeautifulSoup(self.text,"html.parser").get_text()#Remove HTML tags
                text=contractions.fix(text)# Expand contractions (e.g., "can't" -> "cannot")
                text = text.lower()
                text = re.sub(r"http\S+|www\S+|https\S+", '', text)
                text = re.sub(r'@\w+|#\w+', '', text)
                text = text.translate(str.maketrans('', '', string.punctuation))
                text = re.sub(r'\d+', '', text)
                text = ' '.join([word for word in text.split() if word not in stop_words])
                text = re.sub('[^a-zA-Z]', ' ', text)
                text = re.sub('\s+', ' ', text)
                text = ' '.join([lemmatizer.lemmatize(word) for word in text.split()])
                return text.strip()
        except ValueError as e:
            logging.error(f"Text is not provided :{e}")
            return None
class LabelEncoderStep(CleanTextStrategy):
    def __init__(self,df:pd.DataFrame,Categorical_col:str):
        self.encoder=LabelEncoder()
        self.df=df
        self.Categorical_col=Categorical_col
    def clean_text(self):
        try:
            if self.df is not None and not self.df.empty and self.Categorical_col in self.df.columns:
                logging.info("Labelling categorys started")
                self.df[self.Categorical_col]=self.encoder.fit_transform(self.df[self.Categorical_col])
                logging.info("Labelling done")
                return self.df[self.Categorical_col],self.encoder
        except ValueError as e:
            logging.error(f"Check data and categoricl cols:{e}")
            return None
class cleanText:
    def __init__(self,strategy:CleanTextStrategy):
        self._strategy=strategy
    def set_strategy(self,strategy:CleanTextStrategy):
        logging.info("New strategy set succesfully")
        self._strategy=strategy
    def clean(self):
        return self._strategy.clean_text()
        
