# Cover Letter Tweaker

A FastAPI web application to help customize cover letters for different job postings using generative AI.

## Features

- Clean, modern single-page interface
- Input fields for company description and role details
- Flexible cover letter input (text or file upload)
- Support for multiple file formats (.txt, .pdf, .docx)
- Drag-and-drop file upload
- Responsive design

## Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager

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

1. Open your browser and navigate to `http://localhost:8000`
2. Fill in the **Company Description** field with information about the company
3. Paste the **Role Description** (job posting details)
4. Add your cover letter by either:
   - Pasting text directly into the text area, or
   - Uploading a file (.txt, .pdf, or .docx)
5. Click **Process Cover Letter**

## Project Structure

```
cover_letter_tweaker/
├── main.py              # FastAPI application
├── pyproject.toml       # Project dependencies and metadata
├── README.md            # This file
├── static/              # Static assets
│   ├── style.css        # Application styles
│   └── script.js        # Client-side JavaScript
└── templates/           # HTML templates
    └── index.html       # Main application page
```

## Development

This project uses:
- **FastAPI** - Modern web framework for building APIs
- **Uvicorn** - ASGI server for running the application
- **Jinja2** - Template engine for HTML rendering

## Future Enhancements

- Integration with AI providers (OpenAI, Anthropic, etc.)
- Paste in a URL and be able to scrape company info
- History of previous customizations
- Export functionality for processed cover letters
- Cover letter generation and customization logic
- User authentication and saved profiles

## License

This is a personal development project.

