document.addEventListener('DOMContentLoaded', function() {
    var addCommentForm = document.getElementById('addCommentForm');

    if (addCommentForm) {
        addCommentForm.addEventListener('submit', function(event) {
            event.preventDefault();

            // Get form data
            var formData = new FormData(event.target);

            // Send POST request to add_comment endpoint
            fetch('/add_comment/{{ post["_id"] }}', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'  // Add this header to indicate an AJAX request
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Redirect to the view_post page with the updated comment
                    window.location.href = '/view_post/{{ post["_id"] }}';
                } else {
                    // Handle error scenario if needed
                    console.error('Error adding comment:', data.error);
                }
            })
            .catch(error => {
                console.error('Error adding comment:', error);
            });
        });
    }
});