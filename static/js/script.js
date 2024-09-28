// File upload handling
const fileUpload = document.getElementById('file-upload');
const fileNameDisplay = document.getElementById('file-name');
const submitButton = document.getElementById('submit-button');

fileUpload.addEventListener('change', function() {
    if (fileUpload.files.length > 0) {
        fileNameDisplay.textContent = 'Selected file: ' + fileUpload.files[0].name;
        submitButton.disabled = false;
    } else {
        fileNameDisplay.textContent = '';
        submitButton.disabled = true;
    }
});

// Day/Night cycle
function setDayNightTheme() {
    const hours = new Date().getHours();
    if (hours >= 6 && hours < 18) {
        document.body.classList.add('day');
    } else {
        document.body.classList.add('night');
    }
}

setDayNightTheme();

// Parallax scrolling effect
window.addEventListener('scroll', function() {
    const scrollPosition = window.pageYOffset;
    document.body.style.backgroundPositionY = (scrollPosition * 0.5) + 'px';
});
