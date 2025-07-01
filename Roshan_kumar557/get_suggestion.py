import google.generativeai as genai
import os
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
from abc import ABC,abstractmethod
from dotenv import load_dotenv
load_dotenv()
class ResumeSuggestionsStrategy(ABC):
    @abstractmethod
    def get_suggestions(self):
        pass
class SimpleResumeSuggestions(ResumeSuggestionsStrategy):
    def __init__(self,resume:str,job_description:str):
        self.resume=resume
        self.job_description=job_description
    def get_suggestions(self):
        try:
            if self.resume and self.job_description:
                logging.info("Suggetion started.")
                prompt = f"""
                    You are an expert resume advisor. Given the resume and job description below, provide the following:

                    1. Decision: Is the candidate a good match? (Yes/No)
                    2. Three tips to improve the resume for this role.
                    3. A short improved resume snippet that reflects those tips.

                    Resume:
                    {self.resume}

                    Job Description:
                    {self.job_description}
                    """

                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')  
                    response = model.generate_content(prompt)

                    # Handle both response types
                    feedback = getattr(response, 'text', None)
                    if not feedback and hasattr(response, 'parts'):
                        feedback = "".join(part.text for part in response.parts if hasattr(part, 'text'))

                    if not feedback:
                        return "Could not generate suggestions. Please try again later."

                    return feedback.strip()

                except Exception as e:
                    print(f"[Gemini API Error]: {e}")
                    return "An error occurred while generating suggestions. Please try again later."
        except ValueError as e:
            logging.error(f"Invalid resume :{e}")
            return None
class ResumeSuggestion:
    def __init__(self,strategy:ResumeSuggestionsStrategy):
        self._strategy=strategy
    def suggest(self):
        return self._strategy.get_suggestions()
