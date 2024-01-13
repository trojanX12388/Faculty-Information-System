// Function to disable form fields and submit button
function disableForm(disable) {
    const formFields = ['email', 'password', 'month', 'day', 'year'];
    formFields.forEach(field => {
        document.getElementById(field).disabled = disable;
    });

    document.getElementById('submitBtn').disabled = disable;
}

// Function to start the countdown
function startCountdown() {
    let countdownTime = localStorage.getItem('countdownTime') || 30; // Retrieve countdown time from localStorage or set to 30 initially
    let countdownDisplay = document.getElementById('countdownDisplay'); // Reference to the countdown display span

    countdownDisplay.textContent = countdownTime; // Display initial countdown

    const countdownInterval = setInterval(() => {
        countdownTime -= 1; // Decrement countdown

        if (countdownTime <= 0) {
            clearInterval(countdownInterval); // Stop the countdown when it reaches 0
            resetEntrySession(); // Reset entry session on the server
            localStorage.setItem('entry', 3); // Reset attempts in localStorage
            localStorage.removeItem('countdownTime'); // Remove countdown time from localStorage
            countdownDisplay.textContent = ''; // Clear countdown display
            document.getElementById('manyAttempt').style.display = 'none'; // Hide the attempt message
            disableForm(false); // Enable form fields and submit button after countdown
        } else {
            countdownDisplay.textContent = countdownTime; // Update countdown text
            localStorage.setItem('countdownTime', countdownTime); // Update countdown time in localStorage
        }
    }, 1000); // Update every 1 second (1000 milliseconds)
}

// Check entry count on page load and initiate countdown if entry is zero
document.addEventListener("DOMContentLoaded", function(event) {
    let entry = localStorage.getItem('entry') || 3; // Get the stored entry count or set to 3 initially
    let countdownDisplay = document.getElementById('countdownDisplay'); // Reference to the countdown display span

    if (entry <= 0) {
        disableForm(true); // Disable form fields and submit button
        document.getElementById('manyAttempt').style.display = 'inline-block'; // Show the attempt message
        startCountdown(); // Start the countdown
    }
});

document.getElementById('loginForm').addEventListener('submit', function(event) {
    let entry = localStorage.getItem('entry') || 3; // Get the stored entry count or set to 3 initially
    let countdownDisplay = document.getElementById('countdownDisplay'); // Reference to the countdown display span

    if (entry <= 0) {
        event.preventDefault(); // Prevent form submission
        disableForm(true); // Disable form fields and submit button
        document.getElementById('manyAttempt').style.display = 'inline-block'; // Show the attempt message
        startCountdown(); // Start the countdown
    } else {
        entry -= 1; // Decrement attempts
        localStorage.setItem('entry', entry); // Update attempts in localStorage
    }
});

function resetEntrySession() {
    // Reset entry session logic
}