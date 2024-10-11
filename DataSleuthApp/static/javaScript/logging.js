// Show modal for password input
document.getElementById('delete-logs').addEventListener('click', function() {
    document.getElementById('password-modal').style.display = 'block'; // Show the modal
});

// Confirm password before showing logs
document.getElementById('confirm-password').addEventListener('click', function() {
    const password = document.getElementById('password-input').value;

    if (password) {
        // Assuming you send the password to the backend for verification
        fetch("{% url 'check_password' %}", {
            method: "POST",
            headers: {
                "X-CSRFToken": "{{ csrf_token }}",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ password: password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = "{% url 'logging' %}";  // Redirect to the logs page if password is correct
            } else {
                alert('Incorrect password');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    } else {
        alert('Please enter a password.');
    }
});

// Confirm password before deleting logs
document.getElementById('confirm-delete').addEventListener('click', function() {
    const password = document.getElementById('password-input').value;

    if (password) {
        fetch("/delete_logs/", {  // Use URL for 'delete_logs' view
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,  // Ensure CSRF token is passed
                "Content-Type": "application/json"
            },
            credentials: "include",  // Ensure cookies are included in the request
            body: JSON.stringify({ password: password })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();  // Assuming the response is in JSON format
        })
        .then(data => {
            if (data.success) {
                alert("Logs deleted successfully!");
                location.reload();  // Reload the page after successful deletion
            } else {
                alert(data.message || "Failed to delete logs. Incorrect password.");
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    } else {
        alert('Please enter a password.');
    }
});

// Close modal on cancel
document.getElementById('cancel').addEventListener('click', function() {
    document.getElementById('password-modal').style.display = 'none'; // Hide the modal
});

// Confirm logout action
document.getElementById('logout').addEventListener('click', function(event) {
    const confirmation = confirm("Are you sure you want to logout?");
    if (!confirmation) {
        event.preventDefault();  // Prevent logout if user cancels
    }
});
