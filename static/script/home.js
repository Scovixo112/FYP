function scrollToTop() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}

function showWarningContent() {
    const warningContent = `
    Please fill in the correct emergency contact information.
    Emergency contact can help users quickly contact messages.

    Use the "Help" button with caution.
    This button will trigger the skill of sending distress messages.

    Remember to log in to WhatsApp in Website.
    To send help message via WhatsApp, click on the "Help" button.
`;

    alert(warningContent);
}

function toggleEditEmergencyForm() {
    const form = document.getElementById('editEmergencyForm');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';

    // If the form is displayed, populate it with current values
    if (form.style.display === 'block') {
        document.getElementById('edit-name').value = document.getElementById('emergency-name-value').innerText;
        document.getElementById('edit-gender').value = document.getElementById('emergency-gender-value').innerText;
        document.getElementById('edit-emergency-phone').value = document.getElementById('emergency-phone-value').innerText;
        document.getElementById('edit-emergency-email').value = document.getElementById('emergency-email-value').innerText;
    }
}

function saveEmergencyContact() {
    const formData = new FormData(document.getElementById('editEmergencyForm'));

    fetch('/update_emergency_contact_home', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        updateEmergencyContactUI(data.emergency_contact);
        toggleEditEmergencyForm();  // Hide the form after updating
    })
    .catch(error => console.error('Error:', error));
}

function updateEmergencyContactUI(emergencyContact) {
    // Update the displayed emergency contact information on the page
    document.getElementById('emergency-name-value').innerText = emergencyContact.name || 'N/A';
    document.getElementById('emergency-gender-value').innerText = emergencyContact.gender || 'N/A';
    document.getElementById('emergency-phone-value').innerText = emergencyContact.emergency_phone || 'N/A';
    document.getElementById('emergency-email-value').innerText = emergencyContact.emergency_email || 'N/A';
}


function sendWhatsAppHelp() {
    fetch('/send_whatsapp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.whatsapp_link) {
            window.open(data.whatsapp_link, '_blank'); // Open the WhatsApp link in a new tab
        } else if (data.error) {
            throw new Error(data.error); // Throw an error if an error message is received
        } else {
            throw new Error('Unknown error occurred'); // Throw an error for unknown response
        }
    })
    .catch(error => {
        console.error('Error:', error.message);
        alert('An error occurred while sending the WhatsApp message');
    });
}

// Add double-click event listener to the Help button
document.getElementById("help-button").addEventListener("dblclick", function(event) {
    // Prevent default behavior of the double-click event
    event.preventDefault();
    
    // Call the sendWhatsAppHelp() function to send the WhatsApp message
    sendWhatsAppHelp();
});

// document.addEventListener("DOMContentLoaded", function() {
//     // Opt-in message box elements
//     var optinBox = document.getElementById('optin-message');
//     var blurBackground = document.querySelector('.blur-background');
//     var agreeButton = document.getElementById('agree-button');
//     var cancelButton = document.getElementById('cancel-button');
//     var agreeCheckbox = document.getElementById('agree-checkbox');

//     // Function to show opt-in message box
//     function showOptinMessage() {
//         blurBackground.style.display = 'block';
//         optinBox.style.display = 'block';
//     }

//     // Function to hide opt-in message box
//     function hideOptinMessage() {
//         blurBackground.style.display = 'none';
//         optinBox.style.display = 'none';
//     }

//     // Functionality for 'Agree' button
//     agreeButton.addEventListener('click', function() {
//         // Check if the checkbox is checked
//         if (agreeCheckbox.checked) {
//             hideOptinMessage();
//             // Add your logic here for what happens when user agrees
//         } else {
//             alert('Please Agree to the Policy before proceeding.');
//         }
//     });

//     // Functionality for 'Cancel' button
//     cancelButton.addEventListener('click', function() {
//         window.location.href = "{{ url_for('index') }}"; // Redirect to login page
//     });

//     // Show opt-in message box after login (you can trigger this as needed)
//     showOptinMessage();

//     // Enable/disable 'Agree' button based on checkbox state
//     agreeCheckbox.addEventListener('change', function() {
//         agreeButton.disabled = !agreeCheckbox.checked;
//     });
// });

