// Script to handle form submission using fetch API
document.getElementById('createPostForm').addEventListener('submit', function(event) {
    event.preventDefault();

    // Get form data
    var formData = new FormData(event.target);

    // Send POST request to create_post endpoint
    fetch('/create_post' , {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reload the page after successful post creation
            location.reload();
        } else {
            // Handle error scenario if needed
            console.error('Error creating post:', data.error);
        }
    })
    .catch(error => {
        console.error('Error creating post:', error);
    });
});


