from google import genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_cover_letter(resume_text, job):

    resume_summary = resume_text[:1200] 

    prompt = f"""
    Write a short professional cover letter for the following job.

    Resume:
    {resume_text}

    Job Title: {job['title']}
    Company: {job['company']}

    Job Description:
    {job['description']}

    The cover letter should be concise, professional, and tailored to the job.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def suggest_resume_improvements(resume_text, job):

    prompt = f"""
    Compare the resume with the job description.

    Resume:
    {resume_text}

    Job Description:
    {job['description']}

    Suggest improvements to make the resume better match the role.
    Focus on missing skills, project highlights, and keywords.
    """

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

    return response.text