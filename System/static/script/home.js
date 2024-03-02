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

// sendEmail function to dynamically fetch SMTP details
async function sendEmail(receiverEmail, subject, body) {
    try {
        const response = await fetch('/get_user_info', { method: 'GET' });
        const userData = await response.json();

        const smtpDetails = userData.smtp_details;

        if (!smtpDetails || !smtpDetails.smtp_server || !smtpDetails.smtp_port || !smtpDetails.email || !smtpDetails.email_password) {
            throw new Error('SMTP details are missing or incorrect.');
        }

        const { smtp_server, smtp_port, email, email_password } = smtpDetails;

        const message = new FormData();
        message.append('receiver_email', receiverEmail);
        message.append('subject', subject);
        message.append('body', body);

        const emailResponse = await fetch('/send_email', {
            method: 'POST',
            body: message,
            headers: {
                'Authorization': `Bearer ${email_password}`,  // Use a more secure method to send email password
            }
        });

        if (emailResponse.ok) {
            console.log(`Email sent successfully to ${receiverEmail}`);
        } else {
            throw new Error(`Error sending email to ${receiverEmail}`);
        }
    } catch (error) {
        console.error('Error sending email:', error);
    }
}


function sendHelpMessage() {
    fetch('/get_user_info', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            const emergencyEmail = data.emergency_contact.emergency_email;
            const userEmail = data.email;
            const subject = 'Emergency Help Needed';
            const message = `User ${userEmail} needs help!`;

            sendEmail(emergencyEmail, subject, message);
        })
        .catch(error => console.error('Error:', error));
}


