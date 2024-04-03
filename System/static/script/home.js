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
    To send help information, double-click the "Help" button.
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


