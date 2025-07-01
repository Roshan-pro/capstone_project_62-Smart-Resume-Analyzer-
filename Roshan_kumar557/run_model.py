import pandas as pd 
from sklearn.feature_extraction.text import TfidfVectorizer
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

from cleantext import cleanText, SimpleCleanText, LabelEncoderStep
from data_splitter import simpleSplitData, DataSplit
from mlmodel import SimpleKNeighborsClassifier, TrainModel
from sklearn.preprocessing import LabelEncoder
from extract_text_from_pdf import ExtractText, simpleExtractTextPdf
from fetch_job import SimpleFetchJobsStrategy, FindJobs
from get_suggestion import SimpleResumeSuggestions, ResumeSuggestion
from calculate_similarity import Similarity,SimplecalculateSimilarity
import mlflow
import mlflow.sklearn

def ml_pipeline(pdf_path: str):
    mlflow.autolog()
    
    with mlflow.start_run():
        data = pd.read_csv(r"C:\Users\rk186\OneDrive\Desktop\62_capstone\UpdatedResumeDataSet.csv")
        logging.info("Cleaining text started.")
        data["Clean_Resume"] = data["Resume"].apply(lambda x: cleanText(SimpleCleanText(x)).clean())
        logging.info("Cleaing text done.")

        encoder_strategy = cleanText(LabelEncoderStep(data, "Category"))
        data["Label_cat"] ,encoder= encoder_strategy.clean()

        train_test_split = DataSplit(simpleSplitData("Clean_Resume"))
        x_train, x_test, y_train, y_test, vectorizer = train_test_split.split_data(data, target_col="Label_cat")
        
        classifier = SimpleKNeighborsClassifier(x_train, y_train, x_test, y_test)
        classifier.vectorizer = vectorizer  # Manually attach vectorizer for later use
        knn_model = TrainModel(classifier).trainModel()

        # Extract and clean resume text from uploaded PDF
        raw_text = ExtractText(simpleExtractTextPdf()).extractTextFromPdf(pdf_path)
        cleaned_resume = cleanText(SimpleCleanText(raw_text)).clean()

        tfidf = classifier.vectorizer
        resume_vector = tfidf.transform([cleaned_resume])
        predicted_category_num = classifier.model.predict(resume_vector)[0]
        predicted_category = encoder.inverse_transform([predicted_category_num])[0]

        print("\nPredicted Resume Category:", predicted_category)

    while True:
        print("\nChoose an option:")
        print("1. Get top job listings")
        print("2. Get resume suggestions using Gemini")
        print("3. Get resume-job similarity score")
        print("4. Exit")
        choice = input("Enter your choice (1/2/3/4): ").strip()

        if choice == "1":
            job_fetcher = FindJobs(SimpleFetchJobsStrategy(predicted_category))
            jobs = job_fetcher.findJobs()
            print("\n[Top Jobs Found]")
            for job in jobs[:10]:
                print("-", job.get("job_title"), "at", job.get("employer_name"))

        elif choice == "2":
            job_fetcher = FindJobs(SimpleFetchJobsStrategy(predicted_category))
            jobs = job_fetcher.findJobs()
            if jobs:
                job_description = jobs[0].get("job_description", "")
                sugg_engine = ResumeSuggestion(SimpleResumeSuggestions(raw_text, job_description))
                print("\n[Resume Suggestions]\n", sugg_engine.suggest())
            else:
                print("No job description available to generate suggestions.")
        elif choice == "3":
            job_fetcher = FindJobs(SimpleFetchJobsStrategy(predicted_category))
            jobs = job_fetcher.findJobs()
            if jobs:
                job_description = jobs[0].get("job_description", "")
                score = Similarity(SimplecalculateSimilarity(raw_text, job_description)).calculate_similarity()
                print(f"\n[Similarity Score]: {score}%")
            else:
                print("No job description available to calculate similarity.")

        elif choice == "4": 
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    pdf_path = input("Enter the path to your resume PDF: ").strip()
    ml_pipeline(pdf_path)
