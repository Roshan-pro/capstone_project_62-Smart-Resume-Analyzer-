from sklearn.neighbors import KNeighborsClassifier
from abc import ABC,abstractmethod
from sklearn.metrics import  accuracy_score
import pandas as pd 
import logging 
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class KNeighborsClassifierStrategy(ABC):
    @abstractmethod
    def train_model(self,x_train:pd.DataFrame,y_train:pd.DataFrame):
        pass 
class SimpleKNeighborsClassifier(KNeighborsClassifierStrategy):
    def __init__(self,x_train:pd.DataFrame,y_train:pd.DataFrame,x_test:pd.Series,y_test:pd.Series):
        self.x_train=x_train
        self.y_train=y_train
        self.x_test=x_test
        self.y_test=y_test
        self.model=KNeighborsClassifier()
    def train_model(self):
        logging.info("Training Model..")
        model=self.model.fit(self.x_train,self.y_train)
        y_pred=model.predict(self.x_test)
        logging.info("Model is Ready.")
        logging.info("Train_Accuracy: %s", accuracy_score(self.y_train, model.predict(self.x_train)))
        logging.info("Test_Accuracy: %s", accuracy_score(self.y_test, y_pred))

        return model 
class TrainModel:
    def __init__(self,strategy:KNeighborsClassifierStrategy):
        self._strategy=strategy
    def trainModel(self):
        return self._strategy.train_model()