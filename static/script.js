// LocalStorage key for form data persistence
const STORAGE_KEY = 'coverLetterFormData';

// Debounce function to limit save frequency
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Helper function to convert File to base64
async function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
        reader.readAsDataURL(file);
    });
}

// Helper function to convert base64 back to File object
function base64ToFile(base64, filename, mimeType) {
    // Extract the base64 data (remove data URL prefix)
    const base64Data = base64.split(',')[1];
    const byteCharacters = atob(base64Data);
    const byteNumbers = new Array(byteCharacters.length);
    
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: mimeType });
    
    return new File([blob], filename, { type: mimeType });
}

// Save form data to localStorage
async function saveFormData() {
    const resumeToggle = document.querySelector('.toggle-btn.active[data-target="resume"]');
    const coverLetterToggle = document.querySelector('.toggle-btn.active[data-target="coverLetter"]');
    
    const formData = {
        companyDescription: document.getElementById('companyDescription').value,
        roleDescription: document.getElementById('roleDescription').value,
        resumeText: document.getElementById('resumeText').value,
        coverLetterText: document.getElementById('coverLetterText').value,
        resumeInputMode: resumeToggle ? resumeToggle.dataset.mode : 'file',
        coverLetterInputMode: coverLetterToggle ? coverLetterToggle.dataset.mode : 'file'
    };
    
    // Handle resume file if present
    const resumeFileInput = document.getElementById('resumeFile');
    if (resumeFileInput && resumeFileInput.files && resumeFileInput.files[0]) {
        const file = resumeFileInput.files[0];
        const maxSize = 2 * 1024 * 1024; // 2MB limit
        
        if (file.size <= maxSize) {
            try {
                const base64 = await fileToBase64(file);
                formData.resumeFile = {
                    name: file.name,
                    type: file.type,
                    data: base64
                };
            } catch (error) {
                console.warn('Failed to save resume file:', error);
            }
        } else {
            console.warn('Resume file too large to save (exceeds 2MB)');
        }
    }
    
    // Handle cover letter file if present
    const coverLetterFileInput = document.getElementById('coverLetterFile');
    if (coverLetterFileInput && coverLetterFileInput.files && coverLetterFileInput.files[0]) {
        const file = coverLetterFileInput.files[0];
        const maxSize = 2 * 1024 * 1024; // 2MB limit
        
        if (file.size <= maxSize) {
            try {
                const base64 = await fileToBase64(file);
                formData.coverLetterFile = {
                    name: file.name,
                    type: file.type,
                    data: base64
                };
            } catch (error) {
                console.warn('Failed to save cover letter file:', error);
            }
        } else {
            console.warn('Cover letter file too large to save (exceeds 2MB)');
        }
    }
    
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(formData));
        console.log('Form data saved to localStorage');
    } catch (error) {
        console.error('Error saving to localStorage:', error);
        // If quota exceeded, try to save without files
        if (error.name === 'QuotaExceededError') {
            console.warn('Storage quota exceeded, saving without files');
            delete formData.resumeFile;
            delete formData.coverLetterFile;
            try {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(formData));
                console.log('Form data saved without files due to storage limit');
            } catch (e) {
                console.error('Failed to save even without files:', e);
            }
        }
    }
}

// Load form data from localStorage
function loadFormData() {
    try {
        const savedData = localStorage.getItem(STORAGE_KEY);
        if (savedData) {
            const formData = JSON.parse(savedData);
            
            // Populate form fields
            document.getElementById('companyDescription').value = formData.companyDescription || '';
            document.getElementById('roleDescription').value = formData.roleDescription || '';
            document.getElementById('resumeText').value = formData.resumeText || '';
            document.getElementById('coverLetterText').value = formData.coverLetterText || '';
            
            // Restore resume input mode
            if (formData.resumeInputMode) {
                const resumeTargetButton = document.querySelector(`.toggle-btn[data-target="resume"][data-mode="${formData.resumeInputMode}"]`);
                if (resumeTargetButton) {
                    resumeTargetButton.click();
                }
            }
            
            // Restore cover letter input mode (for backward compatibility, check old 'inputMode' field)
            const coverLetterMode = formData.coverLetterInputMode || formData.inputMode;
            if (coverLetterMode) {
                const coverLetterTargetButton = document.querySelector(`.toggle-btn[data-target="coverLetter"][data-mode="${coverLetterMode}"]`);
                if (coverLetterTargetButton) {
                    coverLetterTargetButton.click();
                }
            }
            
            // Restore resume file if present
            if (formData.resumeFile && formData.resumeFile.data) {
                try {
                    const file = base64ToFile(
                        formData.resumeFile.data,
                        formData.resumeFile.name,
                        formData.resumeFile.type
                    );
                    
                    // Create a DataTransfer to set files
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    
                    const resumeFileInput = document.getElementById('resumeFile');
                    resumeFileInput.files = dataTransfer.files;
                    
                    // Update file name display
                    const resumeFileName = document.getElementById('resumeFileName');
                    resumeFileName.textContent = `Selected: ${file.name}`;
                    resumeFileName.classList.add('show');
                    
                    console.log('Resume file restored from localStorage');
                } catch (error) {
                    console.warn('Failed to restore resume file:', error);
                }
            }
            
            // Restore cover letter file if present
            if (formData.coverLetterFile && formData.coverLetterFile.data) {
                try {
                    const file = base64ToFile(
                        formData.coverLetterFile.data,
                        formData.coverLetterFile.name,
                        formData.coverLetterFile.type
                    );
                    
                    // Create a DataTransfer to set files
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    
                    const coverLetterFileInput = document.getElementById('coverLetterFile');
                    coverLetterFileInput.files = dataTransfer.files;
                    
                    // Update file name display
                    const coverLetterFileName = document.getElementById('fileName');
                    coverLetterFileName.textContent = `Selected: ${file.name}`;
                    coverLetterFileName.classList.add('show');
                    
                    console.log('Cover letter file restored from localStorage');
                } catch (error) {
                    console.warn('Failed to restore cover letter file:', error);
                }
            }
            
            console.log('Form data loaded from localStorage');
        }
    } catch (error) {
        console.error('Error loading from localStorage:', error);
    }
}

// Clear saved form data
function clearSavedData() {
    try {
        localStorage.removeItem(STORAGE_KEY);
        console.log('Saved form data cleared');
        
        // Clear form fields
        document.getElementById('companyDescription').value = '';
        document.getElementById('roleDescription').value = '';
        document.getElementById('resumeText').value = '';
        document.getElementById('coverLetterText').value = '';
        
        // Clear file inputs
        const resumeFileInput = document.getElementById('resumeFile');
        const coverLetterFileInput = document.getElementById('coverLetterFile');
        
        if (resumeFileInput) {
            resumeFileInput.value = '';
        }
        
        if (coverLetterFileInput) {
            coverLetterFileInput.value = '';
        }
        
        // Hide file name displays
        const resumeFileName = document.getElementById('resumeFileName');
        const coverLetterFileName = document.getElementById('fileName');
        
        if (resumeFileName) {
            resumeFileName.classList.remove('show');
        }
        
        if (coverLetterFileName) {
            coverLetterFileName.classList.remove('show');
        }
        
        // Show feedback
        alert('Saved form data has been cleared!');
    } catch (error) {
        console.error('Error clearing localStorage:', error);
    }
}

// Create debounced save function
const debouncedSave = debounce(saveFormData, 500);

// Toggle between text input and file upload
const toggleButtons = document.querySelectorAll('.toggle-btn');

toggleButtons.forEach(button => {
    button.addEventListener('click', () => {
        const mode = button.dataset.mode;
        const target = button.dataset.target;
        
        // Get the siblings (other toggle buttons in the same group)
        const parentToggle = button.parentElement;
        const siblingButtons = parentToggle.querySelectorAll('.toggle-btn');
        
        // Update active button within this group only
        siblingButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Show/hide appropriate section based on target
        if (target === 'resume') {
            const resumeTextSection = document.getElementById('resumeTextInputSection');
            const resumeFileSection = document.getElementById('resumeFileInputSection');
            
            if (mode === 'text') {
                resumeTextSection.classList.add('active');
                resumeFileSection.classList.remove('active');
            } else {
                resumeTextSection.classList.remove('active');
                resumeFileSection.classList.add('active');
            }
        } else if (target === 'coverLetter') {
            const textInputSection = document.getElementById('textInputSection');
            const fileInputSection = document.getElementById('fileInputSection');
            
            if (mode === 'text') {
                textInputSection.classList.add('active');
                fileInputSection.classList.remove('active');
            } else {
                textInputSection.classList.remove('active');
                fileInputSection.classList.add('active');
            }
        }
        
        // Save the input mode change
        debouncedSave();
    });
});

// Handle file selection for cover letter
const coverLetterFileInput = document.getElementById('coverLetterFile');
const coverLetterFileName = document.getElementById('fileName');

coverLetterFileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    
    if (file) {
        // Validate file type
        const validTypes = ['.txt', '.pdf', '.docx'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!validTypes.includes(fileExtension)) {
            alert('Please upload a valid file type (.txt, .pdf, or .docx)');
            coverLetterFileInput.value = '';
            coverLetterFileName.classList.remove('show');
            return;
        }
        
        // Display file name
        coverLetterFileName.textContent = `Selected: ${file.name}`;
        coverLetterFileName.classList.add('show');
        
        // Save file to localStorage
        debouncedSave();
    } else {
        coverLetterFileName.classList.remove('show');
    }
});

// Handle file selection for resume
const resumeFileInput = document.getElementById('resumeFile');
const resumeFileName = document.getElementById('resumeFileName');

resumeFileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    
    if (file) {
        // Validate file type
        const validTypes = ['.txt', '.pdf', '.docx'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!validTypes.includes(fileExtension)) {
            alert('Please upload a valid file type (.txt, .pdf, or .docx)');
            resumeFileInput.value = '';
            resumeFileName.classList.remove('show');
            return;
        }
        
        // Display file name
        resumeFileName.textContent = `Selected: ${file.name}`;
        resumeFileName.classList.add('show');
        
        // Save file to localStorage
        debouncedSave();
    } else {
        resumeFileName.classList.remove('show');
    }
});

// Handle drag and drop for cover letter
const coverLetterFileUploadArea = document.querySelector('.file-upload-area');

coverLetterFileUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    coverLetterFileUploadArea.style.borderColor = 'var(--primary-color)';
    coverLetterFileUploadArea.style.background = 'rgba(37, 99, 235, 0.05)';
});

coverLetterFileUploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    coverLetterFileUploadArea.style.borderColor = '';
    coverLetterFileUploadArea.style.background = '';
});

coverLetterFileUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    coverLetterFileUploadArea.style.borderColor = '';
    coverLetterFileUploadArea.style.background = '';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        coverLetterFileInput.files = files;
        // Trigger change event
        const event = new Event('change');
        coverLetterFileInput.dispatchEvent(event);
    }
});

// Handle drag and drop for resume
const resumeFileUploadArea = document.getElementById('resumeFileUploadArea');

resumeFileUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    resumeFileUploadArea.style.borderColor = 'var(--primary-color)';
    resumeFileUploadArea.style.background = 'rgba(37, 99, 235, 0.05)';
});

resumeFileUploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    resumeFileUploadArea.style.borderColor = '';
    resumeFileUploadArea.style.background = '';
});

resumeFileUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    resumeFileUploadArea.style.borderColor = '';
    resumeFileUploadArea.style.background = '';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        resumeFileInput.files = files;
        // Trigger change event
        const event = new Event('change');
        resumeFileInput.dispatchEvent(event);
    }
});

// Add auto-save listeners to form fields
document.getElementById('companyDescription').addEventListener('input', debouncedSave);
document.getElementById('roleDescription').addEventListener('input', debouncedSave);
document.getElementById('resumeText').addEventListener('input', debouncedSave);
document.getElementById('coverLetterText').addEventListener('input', debouncedSave);

// Load saved data when page loads
window.addEventListener('DOMContentLoaded', loadFormData);

// Add event listener for clear button
document.getElementById('clearSavedData').addEventListener('click', clearSavedData);

// Handle form submission
const form = document.getElementById('coverLetterForm');
const resultSection = document.getElementById('result');
const resultContent = document.getElementById('resultContent');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form values
    const companyDescription = document.getElementById('companyDescription').value;
    const roleDescription = document.getElementById('roleDescription').value;
    const resumeText = document.getElementById('resumeText').value;
    const coverLetterText = document.getElementById('coverLetterText').value;
    const coverLetterFile = coverLetterFileInput.files[0];
    const resumeFile = resumeFileInput.files[0];
    
    // Get active modes
    const resumeActiveButton = document.querySelector('.toggle-btn.active[data-target="resume"]');
    const coverLetterActiveButton = document.querySelector('.toggle-btn.active[data-target="coverLetter"]');
    
    const resumeActiveMode = resumeActiveButton ? resumeActiveButton.dataset.mode : 'file';
    const coverLetterActiveMode = coverLetterActiveButton ? coverLetterActiveButton.dataset.mode : 'file';
    
    // Validate that we have a resume (either text or file)
    if (resumeActiveMode === 'text' && !resumeText.trim()) {
        alert('Please enter your resume text');
        return;
    }
    
    if (resumeActiveMode === 'file' && !resumeFile) {
        alert('Please upload a resume file');
        return;
    }
    
    // Validate that we have a cover letter (either text or file)
    if (coverLetterActiveMode === 'text' && !coverLetterText.trim()) {
        alert('Please enter your cover letter text');
        return;
    }
    
    if (coverLetterActiveMode === 'file' && !coverLetterFile) {
        alert('Please upload a cover letter file');
        return;
    }
    
    // Prepare form data
    const formData = new FormData();
    formData.append('companyDescription', companyDescription);
    formData.append('roleDescription', roleDescription);
    
    // Add resume (text or file)
    if (resumeActiveMode === 'text') {
        formData.append('resumeText', resumeText);
    } else {
        formData.append('resumeFile', resumeFile);
    }
    
    // Add cover letter (text or file)
    if (coverLetterActiveMode === 'text') {
        formData.append('coverLetterText', coverLetterText);
    } else {
        formData.append('coverLetterFile', coverLetterFile);
    }
    
    const submitBtn = form.querySelector('.submit-btn');
    const originalText = submitBtn.innerHTML;
    try {
        // Show loading state
        submitBtn.innerHTML = '<span>Processing...</span>';
        submitBtn.disabled = true;
        
        // Send request to backend
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        // Display result
        if (data.error) {
            resultContent.innerText = `Error: ${data.error}`;
        } else if (data.revised_letter) {
            resultContent.innerText = data.revised_letter;
        } else {
            resultContent.innerText = JSON.stringify(data, null, 2);
        }
        resultSection.classList.remove('hidden');
        
        // Scroll to result
        resultSection.scrollIntoView({ behavior: 'smooth' });
        
        // Reset button
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while processing your request. Please try again.');
        
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
});
