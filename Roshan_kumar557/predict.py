
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from cleantext import *
from aboutdata import *
from sklearn import preprocessing
import numpy as np
from sklearn.model_selection import StratifiedKFold,train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, accuracy_score



resume_data["Clean_resume"]=resume_data['Resume'].apply(preprocess_text)
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
encoder=preprocessing.LabelEncoder()
resume_data['lable_category']=encoder.fit_transform(resume_data["Category"])
x=vectorizer.fit_transform(resume_data['Clean_resume'])
y=resume_data['Category']
sf=StratifiedKFold(n_splits=10,shuffle=True, random_state=42)
for fold, (train_index,test_index) in enumerate(sf.split(x,y)):
    x_train,x_test=x[train_index],x[test_index]
    y_train,y_test=y[train_index],y[test_index]
knn=KNeighborsClassifier()
knn.fit(x_train,y_train)
y_pred=knn.predict(x_test)
print("Test_Accuracy:",accuracy_score(y_test,y_pred))
print("Train_Accuracy:",accuracy_score(y_train,knn.predict(x_train)))
###less overfitting overfitting train accuracy : 0.9930715935334873,test accuracy :100
# Example: New resume as raw text
new_resume = """
Name: Priya Sharma
Phone: +91-9876543210
Email: priya.sharma@email.com
LinkedIn: linkedin.com/in/priyasharma
Location: Mumbai, India

🎯 Objective
Creative and results-driven marketing professional with 3+ years of experience in digital marketing, brand management, and campaign strategy. Seeking to leverage data-driven strategies to boost brand visibility and customer engagement at a dynamic organization.

💼 Experience
Digital Marketing Executive
ABC Tech Solutions, Mumbai
June 2021 – Present

Planned and executed digital campaigns across Google Ads and Facebook, resulting in a 45% increase in website traffic.

Managed SEO and content strategies, improving keyword rankings by 60% in 6 months.

Designed monthly reports and dashboards to analyze campaign performance.

Collaborated with sales to align lead generation efforts.

Marketing Intern
XYZ Marketing Agency, Pune
Jan 2021 – May 2021

Conducted competitor research and prepared reports for client presentations.

Assisted in developing social media content and calendar.

Supported email campaign execution with Mailchimp and HubSpot.

📚 Education
Bachelor of Business Administration (BBA)
University of Mumbai
2018 – 2021

Specialization: Marketing

CGPA: 8.2/10

🛠 Skills
Digital Marketing (Google Ads, Facebook Ads)

SEO & SEM

Google Analytics

Content Marketing

Email Marketing (Mailchimp, HubSpot)

Market Research

MS Excel & PowerPoint

📈 Certifications
Google Digital Marketing Certification

HubSpot Content Marketing Certificate

SEO Fundamentals – SEMrush Academy

🏆 Achievements
Won 1st prize in national-level marketing case competition (2020)

Increased Instagram followers by 150% in 4 months for an NGO campaign


"""

# Step 1: Preprocess the text
cleaned_resume = preprocess_text(new_resume)

# Step 2: Vectorize using the same TF-IDF vectorizer used in training
resume_vector = vectorizer.transform([cleaned_resume])  # Note: Pass as list

# Step 3: Predict using the trained KNN model
predicted_category = knn.predict(resume_vector)[0]

print("Predicted Resume Category:", predicted_category)
import pickle

# After training
with open('resume_category_model.pkl', 'wb') as f:
    pickle.dump(knn, f)

# Also save your vectorizer (e.g., TF-IDF)
with open('tfidf_vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
print("Done")