# Cover Letter Tweaker

A FastAPI web application to help customize cover letters for different job postings using generative AI.

## Features

- **AI-Powered Cover Letter Rewriting** - Uses Google Gemini 2.5 Flash to intelligently customize your cover letter based on job requirements and your resume
- **Dual Input Support** - Both resume and cover letter fields support either text input or file upload
- **Flexible Input Modes** - Toggle between text input and file upload for both resume and cover letter (defaults to file upload)
- **Multiple File Formats** - Supports `.txt`, `.pdf`, and `.docx` files with automatic text extraction for DOCX
- **Drag-and-Drop Upload** - Intuitive drag-and-drop interface for both resume and cover letter files
- **Auto-Save Functionality** - Form data automatically saves to browser localStorage every 500ms, including uploaded files (up to 2MB)
- **Persistent Storage** - Your form data and files are restored when you return to the page
- **Clear Saved Data** - One-click button to reset all form fields and clear localStorage
- **Modern, Responsive UI** - Clean, single-page interface with a professional design

## Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Google Gemini API key (get one at [Google AI Studio](https://aistudio.google.com/app/apikey))

## Installation

1. Clone or navigate to the project directory:
```bash
cd cover_letter_tweaker
```

2. Install dependencies using `uv`:
```bash
uv pip install -e .
```

Alternatively, you can sync the project:
```bash
uv sync
```

## Configuration

Before running the application, you need to set up your Google Gemini API key:

1. Create a `.env` file in the project root directory:
```bash
touch .env
```

2. Add your Gemini API key to the `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

3. Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey) if you don't have one already.

**Important:** The `.env` file is already in `.gitignore` to keep your API key secure.

## Running the Application

### Using Python directly

```bash
python main.py
```

### Using uvicorn

```bash
uvicorn main:app --reload
```

The application will be available at: `http://localhost:8000`

## Usage

1. **Open the application** - Navigate to `http://localhost:8000` in your browser

2. **Fill in job details:**
   - **Company Description** - Provide information about the company (culture, values, mission, etc.)
   - **Role Description** - Paste the full job posting with requirements and responsibilities

3. **Add your resume:**
   - Toggle between **File Upload** (default) or **Text Input**
   - For file upload: Click or drag-and-drop a `.txt`, `.pdf`, or `.docx` file
   - For text input: Paste your resume text directly

4. **Add your cover letter:**
   - Toggle between **File Upload** (default) or **Text Input**
   - For file upload: Click or drag-and-drop a `.txt`, `.pdf`, or `.docx` file
   - For text input: Paste your existing cover letter

5. **Process** - Click **Process Cover Letter** to generate your customized version

6. **Auto-Save** - Your form data automatically saves every 500ms to your browser's localStorage (including files up to 2MB)

7. **Clear Data** - Use the **Clear Saved Data** button in the header to reset all fields and localStorage

**What to expect:** The AI will rewrite your cover letter by:
- Replacing company name and role title with the new ones
- Integrating the new company's mission into the opening
- Matching your resume's technical skills with the job requirements
- Highlighting relevant soft skills and achievements
- Keeping it concise (maximum 4 paragraphs) and professional

## Project Structure

```
cover_letter_tweaker/
├── main.py              # FastAPI application and API endpoints
├── pyproject.toml       # Project dependencies and metadata
├── README.md            # This file
├── .env                 # Environment variables (create this - not in repo)
├── helpers/             # Helper modules
│   └── gemini_helper.py # Google Gemini AI integration
│                        # - rewrite_cover_letter(): Main AI function
│                        # - fetch_job_details(): Job scraping (not exposed in UI)
├── static/              # Static assets
│   ├── style.css        # Application styles
│   └── script.js        # Client-side JavaScript with localStorage handling
└── templates/           # HTML templates
    └── index.html       # Main application page
```

## Dependencies

This project uses the following key libraries:

- **FastAPI** (`>=0.104.1`) - Modern, fast web framework for building APIs with Python
- **Uvicorn** (`>=0.24.0`) - Lightning-fast ASGI server for running the application
- **Jinja2** (`>=3.1.2`) - Template engine for HTML rendering
- **Google Gemini AI** (`google-genai>=0.1.0`) - Google's Gemini 2.5 Flash model for AI-powered text generation
- **python-dotenv** (`>=1.0.0`) - Environment variable management for secure API key storage
- **python-multipart** (`>=0.0.20`) - Multipart form data parsing for file uploads
- **python-docx** (`>=1.2.0`) - DOCX file parsing and text extraction

See `pyproject.toml` for the complete list of dependencies.

## Future Enhancements

### Completed Features ✅
- ~~Integration with AI provider~~ - **Done:** Google Gemini 2.5 Flash integrated
- ~~Cover letter generation and customization logic~~ - **Done:** Sophisticated AI prompting for natural rewrites
- ~~File upload support~~ - **Done:** Both resume and cover letter support multiple file formats

### Planned Features
- **URL-based job scraping** - Functionality exists in `gemini_helper.py` but not yet exposed in the UI
- **Customization history** - Save and view previous cover letter versions
- **Export functionality** - Download processed cover letters in various formats (PDF, DOCX, TXT)
- **User authentication** - Save profiles and preferences across devices
- **Template library** - Pre-built cover letter templates for different industries
- **Batch processing** - Process multiple job applications at once

## License

This is a personal development project.

