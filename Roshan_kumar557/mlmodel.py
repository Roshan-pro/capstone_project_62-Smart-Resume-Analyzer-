from sklearn.neighbors import KNeighborsClassifier
from abc import ABC,abstractmethod
from sklearn.metrics import  accuracy_score
import pandas as pd 
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
        model=self.model.fit(self.x_train,self.y_train)
        y_pred=model.predict(self.x_test)
        print("Test_Accuracy:",accuracy_score(self.y_test,y_pred))
        print("Train_Accuracy:",accuracy_score(self.y_train,model.predict(self.x_train)))
        return model 
class TrainModel:
    def __init__(self,strategy:KNeighborsClassifierStrategy):
        self._strategy=strategy
    def trainModel(self):
        return self._strategy.train_model()