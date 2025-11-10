from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional

from config import Config
from helpers.gemini_helper import GeminiHelper
from helpers.form_validation_helper import FormValidationHelper

DEBUG = Config.DEBUG

app = FastAPI(title="Cover Letter Tweaker")

# Create directories if they don't exist
Path("static").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main page"""
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "max_text_length": Config.MAX_TEXT_LENGTH
        }
    )


@app.post("/process")
async def process_cover_letter(
    jobLink: Optional[str] = Form(None),
    companyDescription: Optional[str] = Form(None),
    roleDescription: Optional[str] = Form(None),
    resumeText: Optional[str] = Form(None),
    coverLetterText: Optional[str] = Form(None),
    resumeFile: Optional[UploadFile] = File(None),
    coverLetterFile: Optional[UploadFile] = File(None),
):
    """Process the cover letter using Gemini AI

    Combines company and role descriptions, then uses the rewrite_cover_letter
    function to generate a customized cover letter based on the resume.
    Accepts either text or file upload (TXT, PDF, DOCX) for both resume and cover letter.
    """
    try:
        form_validation_helper = FormValidationHelper(
            jobLink,
            companyDescription,
            roleDescription,
            resumeText,
            coverLetterText,
            resumeFile,
            coverLetterFile,
        )
        success, error = await form_validation_helper.validate_form()
        if not success:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": error,
                },
            )

        # TODO: Remove this once the form validation helper is implemented
        # Handle resume file upload if provided
        resume_file_data = form_validation_helper.resumeFileData
        resume_file_mime_type = form_validation_helper.resumeFileMimeType

        # Handle cover letter file upload if provided
        cover_letter_file_data = form_validation_helper.coverLetterFileData
        cover_letter_file_mime_type = form_validation_helper.coverLetterFileMimeType

        # Initialize Gemini helper
        gemini_helper = GeminiHelper()

        # Get job details either from URL or manual input
        if form_validation_helper.job_link_provided:
            # Use fetch_job_details to retrieve information from URL
            job_details = gemini_helper.fetch_job_details(jobLink.strip())
            
            if job_details is None:
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "error": (
                            "Failed to retrieve job details from the provided URL. "
                            "Please check the link and try again."
                        ),
                    },
                )
        else:
            # Combine company and role descriptions into job_details
            job_details = (
                f"Company Description:\n{companyDescription}\n\n"
                f"Role Description:\n{roleDescription}"
            )

        # Call the rewrite_cover_letter function
        revised_letter = gemini_helper.rewrite_cover_letter(
            job_details=job_details,
            resume_text=resumeText,
            existing_letter=coverLetterText,
            cover_letter_file_data=cover_letter_file_data,
            cover_letter_file_mime_type=cover_letter_file_mime_type,
            resume_file_data=resume_file_data,
            resume_file_mime_type=resume_file_mime_type,
        )

        if revised_letter == "SERVICE_UNAVAILABLE":
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "error": (
                        "The Gemini AI service is currently overloaded. "
                        "Please try again in a few moments."
                    ),
                },
            )
        elif revised_letter:
            return JSONResponse(
                content={"success": True, "revised_letter": revised_letter}
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": (
                        "Failed to generate revised cover letter. "
                        "Please check your API key and try again."
                    ),
                },
            )

    except Exception as e:

        if DEBUG:
            raise e
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"An error occurred: {str(e)}"},
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
