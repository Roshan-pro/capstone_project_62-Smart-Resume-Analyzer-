import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import logging
import mlflow

from cleantext import cleanText, SimpleCleanText, LabelEncoderStep
from data_splitter import simpleSplitData, DataSplit
from mlmodel import SimpleKNeighborsClassifier, TrainModel
from extract_text_from_pdf import ExtractText, simpleExtractTextPdf
from fetch_job import SimpleFetchJobsStrategy, FindJobs
from get_suggestion import SimpleResumeSuggestions, ResumeSuggestion
from calculate_similarity import Similarity, SimplecalculateSimilarity

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def analyze_resume(pdf_path: str):
    mlflow.autolog()

    with mlflow.start_run():
        data = pd.read_csv("UpdatedResumeDataSet.csv")
        data["Clean_Resume"] = data["Resume"].apply(lambda x: cleanText(SimpleCleanText(x)).clean())
        data["Label_cat"], encoder = cleanText(LabelEncoderStep(data, "Category")).clean()

        x_train, x_test, y_train, y_test, vectorizer = DataSplit(simpleSplitData("Clean_Resume")).split_data(data, target_col="Label_cat")

        classifier = SimpleKNeighborsClassifier(x_train, y_train, x_test, y_test)
        classifier.vectorizer = vectorizer
        model = TrainModel(classifier).trainModel()

        raw_text = ExtractText(simpleExtractTextPdf()).extractTextFromPdf(pdf_path)
        cleaned_resume = cleanText(SimpleCleanText(raw_text)).clean()

        resume_vector = vectorizer.transform([cleaned_resume])
        predicted_category_num = classifier.model.predict(resume_vector)[0]
        predicted_category = encoder.inverse_transform([predicted_category_num])[0]

        job_fetcher = FindJobs(SimpleFetchJobsStrategy(predicted_category))
        jobs = job_fetcher.findJobs()

        score = 0
        tips = "No suggestions available."
        job_desc = ""

        if jobs:
            job_desc = jobs[0].get("job_description", "")
            score = Similarity(SimplecalculateSimilarity(raw_text, job_desc)).calculate_similarity()
            tips = ResumeSuggestion(SimpleResumeSuggestions(raw_text, job_desc)).suggest()

        job_list = []
        for job in jobs[:5]:
            job_list.append({
                "title": job.get("job_title"),
                "company": job.get("employer_name"),
                "location": job.get("job_city"),
                "link": job.get("job_apply_link")
            })
            #to check 
        # logging.info(f"score:{score}")
        # logging.info(f"tips;{tips}")
        # logging.info(f"predicted_category :{predicted_category}")
        # logging.info(f"jobs:{job_list}")
        return {
            "score": f"{score}%",
            "tips": tips,
            "predicted_category": predicted_category,
            "jobs": job_list
        }
if __name__=="__main__":
    analyze_resume(r"C:\Users\rk186\OneDrive\Desktop\62_capstone\Roshan_kumar557\Roshan_ds_resume.pdf")