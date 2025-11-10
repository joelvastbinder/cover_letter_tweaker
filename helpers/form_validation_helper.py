from urllib.parse import urlparse
from ipaddress import ip_address
from typing import Optional
from fastapi import Form, File, UploadFile
from config import Config

from io import BytesIO
from docx import Document
import magic

class FormValidationHelper:
    def __init__(self,
    jobLink: Optional[str] = Form(None),
    companyDescription: Optional[str] = Form(None),
    roleDescription: Optional[str] = Form(None),
    resumeText: Optional[str] = Form(None),
    coverLetterText: Optional[str] = Form(None),
    resumeFile: Optional[UploadFile] = File(None),
    coverLetterFile: Optional[UploadFile] = File(None),
    ):
        self.jobLink = jobLink
        self.companyDescription = companyDescription
        self.roleDescription = roleDescription
        self.resumeText = resumeText
        self.coverLetterText = coverLetterText
        self.resumeFile = resumeFile
        self.coverLetterFile = coverLetterFile
        self.resumeFileData = None
        self.resumeFileMimeType = None
        self.coverLetterFileData = None
        self.coverLetterFileMimeType = None
        self.job_link_provided = False

    async def validate_form(self):
        # Validate that we have either a job link OR both company and role descriptions
        job_link_provided = self.jobLink and self.jobLink.strip()
        manual_descriptions_provided = (
            self.companyDescription
            and self.companyDescription.strip()
            and self.roleDescription
            and self.roleDescription.strip()
        )
        self.job_link_provided = bool(job_link_provided)
        
        if not job_link_provided and not manual_descriptions_provided:
            return False, "Please provide either a job link OR both company and role descriptions."
        if not self.resumeText and not self.resumeFile:
            return False, "Please provide either resume text or upload a resume file."
        if not self.coverLetterText and not self.coverLetterFile:
            return False, "Please provide either cover letter text or upload a cover letter file."
        if self.jobLink:
            success, error = self.validate_url_safety(self.jobLink)
            if not success:
                print(f"-> something screwy with the job link: {error}")
                return False, "Invalid job link. Please provide a valid URL."
        if self.companyDescription:
            success, error = self.validate_text_length(self.companyDescription)
            if not success:
                return False, f"Company description exceeds maximum length of {Config.MAX_TEXT_LENGTH:,} characters."
        if self.roleDescription:
            success, error = self.validate_text_length(self.roleDescription)
            if not success:
                return False, f"Role description exceeds maximum length of {Config.MAX_TEXT_LENGTH:,} characters."
        if self.resumeText:
            success, error = self.validate_text_length(self.resumeText)
            if not success:
                return False, f"Resume text exceeds maximum length of {Config.MAX_TEXT_LENGTH:,} characters."
        if self.coverLetterText:
            success, error = self.validate_text_length(self.coverLetterText)
            if not success:
                return False, f"Cover letter text exceeds maximum length of {Config.MAX_TEXT_LENGTH:,} characters."
        if self.resumeFile:
            resume_file_validation_helper = FileValidationHelper(self.resumeFile)
            success, error = await resume_file_validation_helper.validate_file()
            if not success:
                return False, error
            self.resumeFileData = resume_file_validation_helper.content
            self.resumeFileMimeType = resume_file_validation_helper.mime_type
        if self.coverLetterFile:
            cover_letter_file_validation_helper = FileValidationHelper(self.coverLetterFile)
            success, error = await cover_letter_file_validation_helper.validate_file()
            if not success:
                return False, error
            self.coverLetterFileData = cover_letter_file_validation_helper.content
            self.coverLetterFileMimeType = cover_letter_file_validation_helper.mime_type
        return True, "Form is valid."

    @staticmethod
    def validate_url_safety(url):
        """Validate that URL is safe to fetch"""
        try:
            parsed = urlparse(url)
            
            # Only allow HTTP/HTTPS
            if parsed.scheme not in ['http', 'https']:
                return False, "Only HTTP/HTTPS URLs are allowed"
            
            # Block localhost and private IP ranges
            hostname = parsed.hostname
            if not hostname:
                return False, "Invalid URL"
                
            # Block localhost variations
            if hostname in ['localhost', '127.0.0.1', '0.0.0.0', '::1']:
                return False, "Cannot fetch from localhost"
            
            # Block private IP ranges (RFC 1918)
            try:
                ip = ip_address(hostname)
                if ip.is_private or ip.is_loopback or ip.is_link_local:
                    return False, "Cannot fetch from private IP addresses"
            except ValueError:
                # Not an IP address, that's fine (it's a domain name)
                pass
            
            # Only allow specific domains (whitelist approach - most secure)
            # Or block known bad patterns (blacklist approach)
            
            return True, "URL is valid"
        except Exception:
            return False, "Invalid URL format"
    @staticmethod
    def validate_text_length(text: str):
        """Validate that extracted text doesn't exceed maximum length"""
        try:
            if len(text) > Config.MAX_TEXT_LENGTH:
                return False, f"Text exceeds maximum length of {Config.MAX_TEXT_LENGTH:,} characters."
        except Exception:
            return False, "Failed to validate text length."
        return True, "Text length is valid."


class FileValidationHelper:
    def __init__(self, file):
        self.file = file
        self.content = None
        self.mime_type = None

    async def validate_file(self):
        self.content = await self.file.read()
        if not self.validate_file_size():
            return False, "File size exceeds 10MB limit. Please use a smaller file."
        success, error = self.validate_file_type()
        return success, error

    def validate_file_size(self):
        if len(self.content) > Config.MAX_FILE_SIZE_BYTES:
            return False
        return True

    def validate_file_type(self):
        # Use python-magic to detect MIME type from file content
        mime = magic.Magic(mime=True)
        detected_mime_type = mime.from_buffer(self.content)

        # Map of supported MIME types
        supported_types = {
            "text/plain": "txt",
            "application/pdf": "pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        }

        if detected_mime_type not in supported_types:
            return False, "Unsupported file type. Please upload a .txt, .pdf, or .docx file."

        self.mime_type = detected_mime_type

        if supported_types[detected_mime_type] == "txt":
            success, error = FormValidationHelper.validate_text_length(
                self.content.decode("utf-8")
            )
            return success, error

        elif supported_types[detected_mime_type] == "docx":
            # DOCX: extract text on backend (Gemini doesn't support DOCX inline data)
            try:
                doc = Document(BytesIO(self.content))
                extracted_text = "\n".join(
                    [paragraph.text for paragraph in doc.paragraphs]
                )
                success, error = FormValidationHelper.validate_text_length(extracted_text)
                if not success:
                    return success, error
                self.content = extracted_text.encode("utf-8")
                self.mime_type = "text/plain"
                    
            except Exception as e:
                print(f"Failed to extract text from resume DOCX file: {e}")
                return False, "Failed to extract text from resume DOCX file."
        return True, "Successfully validated file."