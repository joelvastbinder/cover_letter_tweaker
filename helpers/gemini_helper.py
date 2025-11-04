import os
from google import genai
from google.genai import types

from dotenv import load_dotenv

load_dotenv()

# NOTE: Replace 'YOUR_API_KEY' with your actual Gemini API Key.
# If integrating into a web app, you would manage this key securely on the backend.
API_KEY = os.environ.get("GEMINI_API_KEY")

# Configure the client with the API key
client = genai.Client(api_key=API_KEY)

# --- API CORE FUNCTIONS ---

def fetch_job_details(job_url):
    """
    Step 1: Uses Google Search grounding to retrieve the job description text.
    """
    print(f"-> STEP 1: Fetching job details from URL: {job_url}")
    user_query = f"Find the complete job description text and the company's core mission statement from this URL: {job_url}. Extract the full text into a single block."
    
    system_instruction = "You are a web scraping and extraction assistant. Given a URL, your task is to retrieve and return the full, raw text of the job description, including the company name, role title, and mission statement. Present the findings clearly in a raw text format without any conversational wrappers or formatting like markdown headers or bullet points. The output must be the raw text content."
    
    try:
        # Create grounding tool with Google Search
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        
        config = types.GenerateContentConfig(
            tools=[grounding_tool],
            system_instruction=system_instruction
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_query,
            config=config
        )
        job_details = response.text
        print("-> Step 1 successful. Job details extracted.")
        return job_details
    except Exception as e:
        print(f"ERROR in Step 1 (Fetching Job Details): {e}")
        return None


def rewrite_cover_letter(job_details, resume_text, existing_letter):
    """
    Step 2: Uses the extracted data to rewrite the cover letter based on complex instructions.
    """
    print("-> STEP 2: Rewriting the cover letter using extracted data.")

    # The detailed instructions are baked directly into the system prompt and user prompt
    # to guide the model's behavior and response format.
    
    system_instruction = (
        "You are an expert cover letter personalization AI. Your task is to revise an EXISTING COVER LETTER "
        "to perfectly match a NEW ROLE REQUIREMENTS and RESUME. "
        "Your final output MUST be ONLY the revised cover letter text, with no preamble, introduction, or conversation, "
        "and MUST adhere to the formatting rules below."
    )
    
    user_query = f"""
    Analyze the following four inputs:
    1. [NEW ROLE REQUIREMENTS & COMPANY DESCRIPTION]: {job_details}
    2. [EXISTING COVER LETTER]: {existing_letter}
    3. [RESUME TEXT]: {resume_text}

    Revise the EXISTING COVER LETTER based on the following instructions:

    I. Structural & Tone Mandates:
    1. Replace the previous company's name and role title with the NEW COMPANY NAME and NEW ROLE TITLE found in the [NEW ROLE REQUIREMENTS & COMPANY DESCRIPTION].
    2. Integrate the new company's core mission/value proposition (found in the description) into the opening paragraph as the primary motivation for applying.
    3. Ensure the final letter is concise, strong, and professional, limited to a maximum of 4 paragraphs.

    II. Content Focus & Prioritization (The Match):
    1. Technical Stack: Identify the 2-3 most critical or overlapping technologies listed in the NEW ROLE REQUIREMENTS and make those the leading technical statements in the second paragraph. Specifically match the experience from the RESUME TEXT to prove proficiency in those required areas.
    2. Product/Soft Skills: Identify the 2-3 highest-value soft skills or responsibilities in the NEW ROLE REQUIREMENTS (e.g., "End-to-end ownership," "Architecture," "Cross-functional collaboration"). Use specific achievements from the RESUME TEXT (e.g., "Served as a team lead for the full product lifecycle," or "Facilitated Scrum ceremonies") to directly validate these skills.
    3. Unique Value Proposition: Find any unique, high-leverage overlap between the RESUME TEXT and the industry or regulatory needs of the new company (e.g., if the new company is in health/finance/government, highlight the security/compliance experience).
    4. Tone & Flow (CRITICAL): Do not use any quotation marks to lift phrases from the resume. Paraphrase all experience. The letter must "flow naturally" and sound like a confident human wrote it, not like a report. It should synthesize skills into a smooth narrative.
    
    Start your response directly with the salutation ("Dear...") and provide ONLY the revised cover letter text.
    """
    
    try:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_query,
            config=config
        )
        revised_letter = response.text
        print("-> Step 2 successful. Cover letter rewritten.")
        return revised_letter
    except Exception as e:
        print(f"ERROR in Step 2 (Rewriting Cover Letter): {e}")
        return None