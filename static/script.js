// Toggle between text input and file upload
const toggleButtons = document.querySelectorAll('.toggle-btn');
const textInputSection = document.getElementById('textInputSection');
const fileInputSection = document.getElementById('fileInputSection');
const fileInput = document.getElementById('coverLetterFile');
const fileName = document.getElementById('fileName');

toggleButtons.forEach(button => {
    button.addEventListener('click', () => {
        const mode = button.dataset.mode;
        
        // Update active button
        toggleButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Show/hide appropriate section
        if (mode === 'text') {
            textInputSection.classList.add('active');
            fileInputSection.classList.remove('active');
        } else {
            textInputSection.classList.remove('active');
            fileInputSection.classList.add('active');
        }
    });
});

// Handle file selection
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    
    if (file) {
        // Validate file type
        const validTypes = ['.txt', '.pdf', '.docx'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!validTypes.includes(fileExtension)) {
            alert('Please upload a valid file type (.txt, .pdf, or .docx)');
            fileInput.value = '';
            fileName.classList.remove('show');
            return;
        }
        
        // Display file name
        fileName.textContent = `Selected: ${file.name}`;
        fileName.classList.add('show');
    } else {
        fileName.classList.remove('show');
    }
});

// Handle drag and drop
const fileUploadArea = document.querySelector('.file-upload-area');

fileUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileUploadArea.style.borderColor = 'var(--primary-color)';
    fileUploadArea.style.background = 'rgba(37, 99, 235, 0.05)';
});

fileUploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    fileUploadArea.style.borderColor = '';
    fileUploadArea.style.background = '';
});

fileUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    fileUploadArea.style.borderColor = '';
    fileUploadArea.style.background = '';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        // Trigger change event
        const event = new Event('change');
        fileInput.dispatchEvent(event);
    }
});

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
    const coverLetterFile = fileInput.files[0];
    
    // Validate that we have a cover letter (either text or file)
    const activeMode = document.querySelector('.toggle-btn.active').dataset.mode;
    
    if (activeMode === 'text' && !coverLetterText.trim()) {
        alert('Please enter your cover letter text');
        return;
    }
    
    if (activeMode === 'file' && !coverLetterFile) {
        alert('Please upload a cover letter file');
        return;
    }
    
    // Prepare form data
    const formData = new FormData();
    formData.append('companyDescription', companyDescription);
    formData.append('roleDescription', roleDescription);
    formData.append('resumeText', resumeText);
    
    if (activeMode === 'text') {
        formData.append('coverLetterText', coverLetterText);
    } else {
        formData.append('coverLetterFile', coverLetterFile);
    }
    
    try {
        // Show loading state
        const submitBtn = form.querySelector('.submit-btn');
        const originalText = submitBtn.innerHTML;
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
            resultContent.textContent = `Error: ${data.error}`;
        } else if (data.revised_letter) {
            resultContent.textContent = data.revised_letter;
        } else {
            resultContent.textContent = JSON.stringify(data, null, 2);
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
        
        // Reset button
        const submitBtn = form.querySelector('.submit-btn');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
});

