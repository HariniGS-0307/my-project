// Forms JavaScript for AI Elderly Medicare System

// DOM Ready Function
document.addEventListener('DOMContentLoaded', function() {
  // Initialize form components
  initializeFormValidation();
  initializeDynamicForms();
  initializeFileUploads();
  initializeDatePickers();
  
  console.log('Forms JavaScript loaded');
});

// Initialize Form Validation
function initializeFormValidation() {
  const forms = document.querySelectorAll('.needs-validation');
  
  Array.from(forms).forEach(form => {
    form.addEventListener('submit', function(event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      
      form.classList.add('was-validated');
    }, false);
  });
}

// Initialize Dynamic Forms
function initializeDynamicForms() {
  // Handle conditional fields
  const conditionalTriggers = document.querySelectorAll('[data-conditional]');
  
  conditionalTriggers.forEach(trigger => {
    trigger.addEventListener('change', function() {
      const targetId = this.getAttribute('data-conditional');
      const target = document.getElementById(targetId);
      
      if (target) {
        if (this.type === 'checkbox') {
          target.style.display = this.checked ? 'block' : 'none';
        } else if (this.type === 'select-one') {
          target.style.display = this.value ? 'block' : 'none';
        }
      }
    });
  });
  
  // Handle dynamic field addition
  const addFieldButtons = document.querySelectorAll('[data-add-field]');
  
  addFieldButtons.forEach(button => {
    button.addEventListener('click', function() {
      const targetContainer = document.getElementById(this.getAttribute('data-add-field'));
      const fieldTemplate = this.getAttribute('data-field-template');
      
      if (targetContainer && fieldTemplate) {
        addDynamicField(targetContainer, fieldTemplate);
      }
    });
  });
}

// Add Dynamic Field
function addDynamicField(container, template) {
  const fieldCount = container.querySelectorAll('.dynamic-field').length;
  const newField = document.createElement('div');
  newField.className = 'dynamic-field mb-3';
  newField.innerHTML = template.replace(/{index}/g, fieldCount);
  
  container.appendChild(newField);
  
  // Add remove button
  const removeButton = document.createElement('button');
  removeButton.type = 'button';
  removeButton.className = 'btn btn-sm btn-outline-danger mt-2';
  removeButton.innerHTML = '<i class="fas fa-trash"></i> Remove';
  removeButton.addEventListener('click', function() {
    container.removeChild(newField);
  });
  
  newField.appendChild(removeButton);
}

// Initialize File Uploads
function initializeFileUploads() {
  const fileInputs = document.querySelectorAll('.file-input');
  
  fileInputs.forEach(input => {
    const wrapper = input.closest('.file-input-wrapper');
    if (!wrapper) return;
    
    const fileName = wrapper.querySelector('.file-name');
    const browseButton = wrapper.querySelector('.browse-button');
    
    if (browseButton) {
      browseButton.addEventListener('click', function() {
        input.click();
      });
    }
    
    input.addEventListener('change', function() {
      if (fileName && this.files.length > 0) {
        fileName.textContent = this.files[0].name;
      }
    });
  });
}

// Initialize Date Pickers
function initializeDatePickers() {
  // This would typically initialize a date picker library
  // For now, we'll just ensure date inputs have proper attributes
  const dateInputs = document.querySelectorAll('input[type="date"]');
  
  dateInputs.forEach(input => {
    // Add min/max dates if not already set
    if (!input.hasAttribute('min')) {
      const today = new Date();
      input.min = today.toISOString().split('T')[0];
    }
  });
}

// Validate Form Field
function validateFormField(field) {
  const value = field.value.trim();
  const fieldType = field.getAttribute('data-validate');
  
  if (!value) {
    showFieldError(field, 'This field is required');
    return false;
  }
  
  switch (fieldType) {
    case 'email':
      if (!validateEmail(value)) {
        showFieldError(field, 'Please enter a valid email address');
        return false;
      }
      break;
    case 'phone':
      if (!validatePhone(value)) {
        showFieldError(field, 'Please enter a valid phone number');
        return false;
      }
      break;
    case 'date':
      if (!validateDate(value)) {
        showFieldError(field, 'Please enter a valid date');
        return false;
      }
      break;
    default:
      // No additional validation needed
  }
  
  clearFieldError(field);
  return true;
}

// Show Field Error
function showFieldError(field, message) {
  field.classList.add('is-invalid');
  let feedback = field.parentNode.querySelector('.invalid-feedback');
  
  if (!feedback) {
    feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    field.parentNode.appendChild(feedback);
  }
  
  feedback.textContent = message;
  feedback.style.display = 'block';
}

// Clear Field Error
function clearFieldError(field) {
  field.classList.remove('is-invalid');
  const feedback = field.parentNode.querySelector('.invalid-feedback');
  if (feedback) {
    feedback.style.display = 'none';
  }
}

// Validate Email
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

// Validate Phone
function validatePhone(phone) {
  const re = /^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/;
  return re.test(phone);
}

// Validate Date
function validateDate(date) {
  return !isNaN(Date.parse(date));
}

// Format Phone Number
function formatPhoneNumber(input) {
  const phoneNumber = input.value.replace(/\D/g, '');
  const formatted = phoneNumber.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
  input.value = formatted;
}

// Calculate Age from Date of Birth
function calculateAge(dob) {
  const birthDate = new Date(dob);
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  
  return age;
}

// Auto-save Form Data
function autoSaveFormData(formId, interval = 30000) {
  const form = document.getElementById(formId);
  if (!form) return;
  
  setInterval(() => {
    const formData = new FormData(form);
    const data = {};
    
    for (const [key, value] of formData.entries()) {
      data[key] = value;
    }
    
    // Save to localStorage
    localStorage.setItem(`autosave_${formId}`, JSON.stringify(data));
    
    // Show save indicator
    const saveIndicator = document.getElementById('save-indicator');
    if (saveIndicator) {
      saveIndicator.textContent = 'Draft saved';
      saveIndicator.className = 'text-success';
      
      setTimeout(() => {
        saveIndicator.textContent = '';
      }, 2000);
    }
  }, interval);
}

// Load Auto-saved Data
function loadAutoSavedData(formId) {
  const savedData = localStorage.getItem(`autosave_${formId}`);
  if (!savedData) return;
  
  const data = JSON.parse(savedData);
  const form = document.getElementById(formId);
  
  if (form) {
    Object.keys(data).forEach(key => {
      const field = form.querySelector(`[name="${key}"]`);
      if (field) {
        field.value = data[key];
      }
    });
    
    // Show restore indicator
    const restoreIndicator = document.getElementById('restore-indicator');
    if (restoreIndicator) {
      restoreIndicator.innerHTML = 'Draft restored <button class="btn btn-sm btn-outline-primary" onclick="clearAutoSavedData(\'' + formId + '\')">Clear</button>';
    }
  }
}

// Clear Auto-saved Data
function clearAutoSavedData(formId) {
  localStorage.removeItem(`autosave_${formId}`);
  
  const restoreIndicator = document.getElementById('restore-indicator');
  if (restoreIndicator) {
    restoreIndicator.textContent = '';
  }
}

// Export functions for global use
window.validateFormField = validateFormField;
window.formatPhoneNumber = formatPhoneNumber;
window.calculateAge = calculateAge;
window.autoSaveFormData = autoSaveFormData;
window.loadAutoSavedData = loadAutoSavedData;
window.clearAutoSavedData = clearAutoSavedData;