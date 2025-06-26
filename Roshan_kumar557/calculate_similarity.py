from sentence_transformers import  util,SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_similarity(resume_text,job_desc):
    embeddings=model.encode([resume_text,job_desc],convert_to_tensor=True)
    score=util.cos_sim(embeddings[0],embeddings[1]).items()
    return round(score*100,2)