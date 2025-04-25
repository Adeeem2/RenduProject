// Main JavaScript file for Lab Report Generator

document.addEventListener('DOMContentLoaded', function() {
    // Add Tunisian deadline countdown animation
    addDeadlineAnimation();

    // File input validation
    const instructionFileInput = document.getElementById('instruction_file');
    const codeFilesInput = document.getElementById('code_files');

    if (instructionFileInput && codeFilesInput) {
        // Validate instruction file
        instructionFileInput.addEventListener('change', function() {
            validateFileInput(this, ['.pdf', '.png', '.jpg', '.jpeg']);
        });

        // Validate code files
        codeFilesInput.addEventListener('change', function() {
            validateFileInput(this, ['.py', '.java', '.c','.ipynb']);

            // Show/hide execute Python checkbox based on file selection
            const executeCheckbox = document.getElementById('execute_python');
            if (executeCheckbox) {
                const hasPythonFiles = Array.from(this.files).some(file => file.name.toLowerCase().endsWith('.py'));
                executeCheckbox.parentElement.style.display = hasPythonFiles ? 'block' : 'none';
                if (!hasPythonFiles) {
                    executeCheckbox.checked = false;
                }
            }
        });
    }

    // File drag and drop enhancement
    const dropZones = document.querySelectorAll('.form-control[type="file"]');
    dropZones.forEach(zone => {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            zone.addEventListener(eventName, preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            zone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            zone.addEventListener(eventName, unhighlight, false);
        });

        zone.addEventListener('drop', handleDrop, false);
    });

    // Form submission handling
    const form = document.getElementById('upload-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const instructionFile = instructionFileInput.files.length;
            const codeFiles = codeFilesInput.files.length;

            if (!instructionFile || !codeFiles) {
                e.preventDefault();
                alert('Veuillez sélectionner à la fois un fichier d\'instructions et au moins un fichier de code.');
                return false;
            }
        });
    }
});

// Helper functions
function validateFileInput(input, allowedExtensions) {
    const files = Array.from(input.files);
    const invalidFiles = files.filter(file => {
        const ext = '.' + file.name.split('.').pop().toLowerCase();
        return !allowedExtensions.includes(ext);
    });

    if (invalidFiles.length > 0) {
        alert(`Type(s) de fichier non valide(s): ${invalidFiles.map(f => f.name).join(', ')}\nExtensions autorisées: ${allowedExtensions.join(', ')}`);
        input.value = ''; // Clear the input
    }
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    this.classList.add('highlight');
}

function unhighlight(e) {
    this.classList.remove('highlight');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    this.files = files;

    // Trigger change event
    const event = new Event('change');
    this.dispatchEvent(event);
}

// Tunisian deadline animation
function addDeadlineAnimation() {
    // Create a deadline countdown element
    const cardHeader = document.querySelector('.card-header');
    if (cardHeader) {
        const deadlineCountdown = document.createElement('div');
        deadlineCountdown.className = 'deadline-countdown mt-2 animate__animated animate__fadeIn animate__delay-2s';
        deadlineCountdown.innerHTML = '<span class="deadline-icon">⏱️</span> <span class="deadline-text">Date limite approche !</span>';
        cardHeader.appendChild(deadlineCountdown);

        // Add blinking effect
        const deadlineText = deadlineCountdown.querySelector('.deadline-text');
        setInterval(() => {
            deadlineText.style.animation = 'blink 1s';
            setTimeout(() => {
                deadlineText.style.animation = '';
            }, 1000);
        }, 5000);

        // Add random Tunisian student phrases
        const phrases = [
            "Mazelt barcha wa9t! (Il reste encore beaucoup de temps !)",
            "Nkammel ghodwa inchallah! (Je finirai demain, si Dieu le veut !)",
            "Mafhemtech el sujet! (Je ne comprends pas le sujet !)",
            "Chkoun 3ando el correction? (Qui a la solution ?)",
            "Nsit el deadline! (J'ai oublié la date limite !)",
            "Mafhemt meno chy! (Je n'ai rien compris !)",

        ];

        // Change phrase every 10 seconds
        const quoteElement = document.querySelector('.tunisian-quote p em');
        if (quoteElement) {
            let index = 0;
            setInterval(() => {
                index = (index + 1) % phrases.length;
                quoteElement.textContent = `"${phrases[index]}"`;
            }, 10000);
        }
    }
}
