from abc import ABC,abstractmethod
from sklearn.model_selection import StratifiedKFold
import pandas as pd 
from sklearn.feature_extraction.text import TfidfVectorizer
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class SplitDataStrategy(ABC):
    @abstractmethod
    def split(self,df:pd.DataFrame,target_col:str):
        pass
class simpleSplitData(SplitDataStrategy):
    def __init__(self,target_col:str="Resume"):
        self.target_col=target_col
        self.tdf=TfidfVectorizer(stop_words='english', max_features=5000)
    def split(self, df:pd.DataFrame, target_col:str):
        try:
            if  not isinstance(df,pd.DataFrame):
                logging.error("Provied df is not pandas Data frame.")
            elif not isinstance(target_col,str):
                logging.error("Provide target columns is not string,please convert it to string.")
            else:
                x=self.tdf.fit_transform(df[self.target_col].astype(str))
                y=df[target_col]
                sf=StratifiedKFold(n_splits=10,shuffle=True, random_state=42)
                for fold, (train_index,test_index) in enumerate(sf.split(x,y)):
                    x_train,x_test=x[train_index],x[test_index]
                    y_train,y_test=y[train_index],y[test_index]
                    
                return x_train,x_test,y_train,y_test,self.tdf
        except ValueError as e:
            logging.error(f"df or target columns is not provide :{e}")
            return None
class DataSplit:
    def __init__(self,strategy:SplitDataStrategy):
        self._strategy=strategy
    def split_data(self,df:pd.DataFrame,target_col:str):
        return self._strategy.split(df,target_col)