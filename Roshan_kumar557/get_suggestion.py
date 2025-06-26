import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

from dotenv import load_dotenv
load_dotenv()
def get_suggestions(resume, job_description):
    prompt = f"""
You are an expert resume advisor. Given the resume and job description below, provide the following:

1. Decision: Is the candidate a good match? (Yes/No)
2. Three tips to improve the resume for this role.
3. A short improved resume snippet that reflects those tips.

Resume:
{resume}

Job Description:
{job_description}
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
