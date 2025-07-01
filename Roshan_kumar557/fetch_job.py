import requests
import os  
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
from dotenv import load_dotenv
load_dotenv()
from abc import ABC,abstractmethod
class FetchJobsStrategy(ABC):
    @abstractmethod
    def fetchJobs(self):
        pass
class SimpleFetchJobsStrategy(FetchJobsStrategy):
    def __init__(self,category:str):
        self.category=category
    def fetchJobs(self,Location:str="India",page=1):
        try:
            if not isinstance(self.category,str):
                logging.error("Category is not in str.It should be string.")
            else:
                logging.info(f"Fetching job started for :{self.category}")
                url = "https://jsearch.p.rapidapi.com/search"

                headers = {
                    "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
                    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
                }

                params = {
                    "query": self.category,
                    "page": page,
                    "num_pages": 1,
                    "date_posted": "week" # Added to get fresh results (can be 'today', 'month', 'all_time')
                }

                # logging.info(f"Fetching jobs with query: {self.category}") # Good for debugging
                response = requests.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    return response.json().get("data", [])
                else:
                    
                    logging.info("API Error:", response.status_code, response.text)
                    return []
        except ValueError as e:
            logging.error("Invalid category")
            return None
class FindJobs:
    def __init__(self,strategy:FetchJobsStrategy):
        self._strategy=strategy
    def findJobs(self):
        return self._strategy.fetchJobs()
