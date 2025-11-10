import trafilatura
from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions

from config import Config


class GeminiHelper:
    def __init__(self):
        api_key = Config.GEMINI_API_KEY
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set. Please check your configuration"
            )

        self.client = genai.Client(api_key=api_key)

    def fetch_job_details(self, job_url):
        """
        Step 1: Fetches job posting content from URL and extracts relevant details using trafilatura and Gemini.
        
        This method:
        1. Fetches the HTML content from the job URL using trafilatura
        2. Extracts the main content (removes nav, footer, ads, etc.)
        3. Uses Gemini to analyze and summarize company and role information
        
        Returns:
            str: Structured job details containing company and role information, or None on failure
        """
        print(f"-> STEP 1: Fetching job details from URL: {job_url}")
        
        try:
            # Step 1a: Fetch and extract content using trafilatura
            # trafilatura.fetch_url() handles HTTP requests with proper headers and error handling
            print("-> Fetching and extracting webpage content...")
            downloaded = trafilatura.fetch_url(job_url)
            
            if not downloaded:
                print("ERROR: Could not fetch content from the URL")
                return None
            
            # Extract main content using trafilatura
            extracted_text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                no_fallback=False
            )
            
            if not extracted_text or len(extracted_text.strip()) < 100:
                print("ERROR: Could not extract sufficient content from the webpage")
                return None
            
            print(f"-> Extracted {len(extracted_text)} characters of content")
            
            # Step 1b: Use Gemini to analyze and summarize the content
            print("-> Analyzing content with Gemini...")
            
            system_instruction = (
                "You are an expert job posting analyzer. Your task is to extract and summarize "
                "key information from job posting text. Focus on identifying: "
                "1) Company name, mission, values, and culture "
                "2) Role title, key requirements, responsibilities, and technical skills. "
                "Provide a clear, concise summary that captures the essential information "
                "needed to tailor a cover letter."
            )
            
            user_query = f"""
            Analyze the following job posting content and extract the key information:

            {extracted_text}

            Please provide a structured summary with the following sections:
            1. COMPANY INFORMATION: Name, mission/values, industry, and any relevant company culture details
            2. ROLE INFORMATION: Job title, key responsibilities, required qualifications, technical skills/stack, and any unique requirements
            
            Keep the summary concise but comprehensive enough to understand what the company does and what the role requires.
            """
            
            config = types.GenerateContentConfig(system_instruction=system_instruction)
            
            response = self.client.models.generate_content(
                model=Config.GEMINI_MODEL, 
                contents=user_query, 
                config=config
            )
            
            job_details = response.text
            print("-> Step 1 successful. Job details extracted and analyzed.")
            return job_details
            
        except Exception as e:
            print(f"ERROR in Step 1 (Fetching Job Details): {e}")
            return None

    def rewrite_cover_letter(
        self,
        job_details,
        resume_text=None,
        existing_letter=None,
        cover_letter_file_data=None,
        cover_letter_file_mime_type=None,
        resume_file_data=None,
        resume_file_mime_type=None,
    ):
        """
        Step 2: Uses the extracted data to rewrite the cover letter based on complex instructions.

        Args:
            job_details: Company and role description text
            resume_text: User's resume text (optional if resume_file_data is provided)
            existing_letter: Cover letter text (optional if cover_letter_file_data is provided)
            cover_letter_file_data: Raw cover letter file bytes (optional if existing_letter is provided)
            cover_letter_file_mime_type: MIME type of cover letter file (required if cover_letter_file_data is provided)
            resume_file_data: Raw resume file bytes (optional if resume_text is provided)
            resume_file_mime_type: MIME type of resume file (required if resume_file_data is provided)
        """
        print("-> STEP 2: Rewriting the cover letter using extracted data.")

        # Validate that we have either existing_letter or cover_letter_file_data
        if not existing_letter and not cover_letter_file_data:
            print(
                "ERROR: Neither existing_letter text nor cover_letter_file_data was provided."
            )
            return None

        # Validate that we have either resume_text or resume_file_data
        if not resume_text and not resume_file_data:
            print("ERROR: Neither resume_text nor resume_file_data was provided.")
            return None

        # The detailed instructions are baked directly into the system prompt and user prompt
        # to guide the model's behavior and response format.

        system_instruction = (
            "You are an expert cover letter personalization AI. Your task is to revise an EXISTING COVER LETTER "
            "to perfectly match a NEW ROLE REQUIREMENTS and RESUME. "
            "Your final output MUST be ONLY the revised cover letter text, with no preamble, introduction, or conversation, "
            "and MUST adhere to the formatting rules below."
        )

        # Build prompt with placeholders for attached documents
        resume_ref = (
            "See the attached resume document" if resume_file_data else resume_text
        )
        cover_letter_ref = (
            "See the attached document or text below"
            if cover_letter_file_data
            else existing_letter
        )

        prompt_text = f"""
        Analyze the following inputs:
        1. [NEW ROLE REQUIREMENTS & COMPANY DESCRIPTION]: {job_details}
        2. [EXISTING COVER LETTER]: {cover_letter_ref}
        3. [RESUME]: {resume_ref}

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
            config = types.GenerateContentConfig(system_instruction=system_instruction)

            # Build content parts based on whether we have file data or text
            parts = []

            # Add cover letter (file or text)
            if cover_letter_file_data and cover_letter_file_mime_type:
                print(
                    f"-> Processing cover letter from file (MIME type: {cover_letter_file_mime_type})"
                )
                cover_letter_part = types.Part(
                    inline_data=types.Blob(
                        mime_type=cover_letter_file_mime_type, data=cover_letter_file_data
                    )
                )
                parts.append(cover_letter_part)

            # Add resume (file or text - will be embedded in prompt if text)
            if resume_file_data and resume_file_mime_type:
                print(
                    f"-> Processing resume from file (MIME type: {resume_file_mime_type})"
                )
                resume_part = types.Part(
                    inline_data=types.Blob(
                        mime_type=resume_file_mime_type, data=resume_file_data
                    )
                )
                parts.append(resume_part)

            # Add the text prompt
            text_part = types.Part(text=prompt_text)
            parts.append(text_part)

            # Generate content
            if len(parts) > 1:
                # Use multipart content (files + text)
                print("-> Using multipart content with file attachments")
                contents = [types.Content(role="user", parts=parts)]

                response = self.client.models.generate_content(
                    model=Config.GEMINI_MODEL, contents=contents, config=config
                )
            else:
                # Use text-only approach
                print("-> Processing from text input only")
                response = self.client.models.generate_content(
                    model=Config.GEMINI_MODEL, contents=prompt_text, config=config
                )

            revised_letter = response.text
            print("-> Step 2 successful. Cover letter rewritten.")
            return revised_letter

        except google_exceptions.ServiceUnavailable as e:
            print(f"ERROR in Step 2 (Rewriting Cover Letter): 503 Service Unavailable - {e}")
            return "SERVICE_UNAVAILABLE"
        except google_exceptions.ResourceExhausted as e:
            print(f"ERROR in Step 2 (Rewriting Cover Letter): Resource Exhausted - {e}")
            return "SERVICE_UNAVAILABLE"
        except Exception as e:
            print(f"ERROR in Step 2 (Rewriting Cover Letter): {e}")
            # Provide more detailed error message for file-related issues
            if cover_letter_file_data:
                print(
                    f"  Cover letter file processing failed. MIME type: {cover_letter_file_mime_type}, File size: {len(cover_letter_file_data)} bytes"
                )
            if resume_file_data:
                print(
                    f"  Resume file processing failed. MIME type: {resume_file_mime_type}, File size: {len(resume_file_data)} bytes"
                )
            return None
