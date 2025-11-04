from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from helpers.gemini_helper import rewrite_cover_letter

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
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process")
async def process_cover_letter(
    companyDescription: str = Form(...),
    roleDescription: str = Form(...),
    resumeText: str = Form(...),
    coverLetterText: str = Form(...)
):
    """Process the cover letter using Gemini AI
    
    Combines company and role descriptions, then uses the rewrite_cover_letter
    function to generate a customized cover letter based on the resume.
    """
    try:
        # Combine company and role descriptions into job_details
        job_details = f"Company Description:\n{companyDescription}\n\nRole Description:\n{roleDescription}"
        
        # Call the rewrite_cover_letter function
        revised_letter = rewrite_cover_letter(
            job_details=job_details,
            resume_text=resumeText,
            existing_letter=coverLetterText
        )
        
        if revised_letter:
            return JSONResponse(content={
                "success": True,
                "revised_letter": revised_letter
            })
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Failed to generate revised cover letter. Please check your API key and try again."
                }
            )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"An error occurred: {str(e)}"
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

