from sentence_transformers import  util,SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
from abc import ABC,abstractmethod
class calculateSimilarityStrategy(ABC):
    def __init__(self,resume_text:str,job_desc:str):
        self.resume_text=resume_text
        self.job_desc=job_desc
    @abstractmethod
    def calculate_similarity(self):
        pass
class SimplecalculateSimilarity(calculateSimilarityStrategy):
    def __init__(self,resume_text:str,job_desc:str):
        self.resume_text=resume_text
        self.job_desc=job_desc
    def calculate_similarity(self):
        embeddings=model.encode([self.resume_text,self.job_desc],convert_to_tensor=True)
        score=util.cos_sim(embeddings[0],embeddings[1]).item()
        return round(score*100,2)
class Similarity:
    def __init__(self,strategy:calculateSimilarityStrategy):
        self._Strategy=strategy
    def calculate_similarity(self):
        return self._Strategy.calculate_similarity()
