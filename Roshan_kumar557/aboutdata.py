import pandas as pd  
from cleantext import *
import matplotlib.pyplot as plt
import seaborn as sns
resume_data=pd.read_csv(r"C:\Users\rk186\OneDrive\Desktop\62_capstone\UpdatedResumeDataSet.csv")
print("shape :",resume_data.shape)

print(resume_data['Resume'][0]) #checking first resume
print("Resume info :",resume_data.info())

#visualize
plt.figure(figsize=(8,7))
sns.countplot(resume_data["Category"])
plt.xticks(rotation=90)
plt.show()
