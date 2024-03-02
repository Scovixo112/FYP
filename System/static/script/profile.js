function toggleEditForm() {
    // Toggle visibility of the edit form
    var editForm = document.getElementById('editForm');
    editForm.style.display = editForm.style.display === 'none' ? 'block' : 'none';
}

//create
function saveTodo() {
    // Get the new todo task from the form
    var newTodoTask = document.getElementById('newTodoTask').value;


    // Make an AJAX request to the create_todo route
    fetch('/create_todo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ "todo_task": newTodoTask })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        // Refresh the page after adding the new todo
        window.location.reload();
    })
    .catch(error => console.error('Error:', error));

    return false; // Prevent the form from submitting in the traditional way
}


// delete
function deleteTodo(userId, todoTask) {
    var confirmDelete = confirm("Are you sure you want to delete this todo?");

    console.log(userId)
    console.log(todoTask)

    if (confirmDelete) {
        // Make an AJAX request to the delete_todo route
        fetch('/delete_todo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "user_id": userId,
                "todo_task": todoTask })
        })
        .then(response => response.json())
        .then(data => {
        if (data.message) {
            alert(data.message);
            window.location.reload();
        } else {
            console.error('Error:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    }
}



// Fetch and display todos when the page loads
document.addEventListener('DOMContentLoaded', function() {
    fetch('/retrieve_todos')
        .then(response => response.json())
        .then(data => {
            const todoList = document.getElementById('todoList');
            const emptyTodo = document.getElementById('emptyTodo');

            if (data.todos.length > 0) {
                emptyTodo.style.display = 'none'; // Hide the empty message
                data.todos.forEach(todo => {
                    const listItem = document.createElement('li');
                    listItem.textContent = todo.todo_task;
                    // listItem.innerHTML += `<span class="edit-icon" onclick="editTodo('${todo.todo_task|string}')">✎</span>`;
                    listItem.innerHTML += `<span class="delete-icon" onclick="deleteTodo('${todo.todo_task|string}')">🗑</span>`;
                    todoList.appendChild(listItem);
                });
            } else {
                emptyTodo.style.display = 'block'; // Show the empty message
            }
        })
        .catch(error => console.error('Error:', error));
});


function showOptInMessage() {
    document.getElementById('optInMessage').style.display = 'flex';
}

function openAssessment() {
    if (document.getElementById('agreeYes').checked) {
        window.open('https://worldhealthorg.shinyapps.io/steps_depression_tool/', '_blank');
        document.getElementById('optInMessage').style.display = 'none';
        document.getElementById('resultPopup').style.display = 'flex';
    } else {
        alert('Please agree to proceed.');
    }
}


function saveResult() {
    var resultValue = document.querySelector('input[name="resultRadio"]:checked').value;

    // Make an AJAX request to update mental health status in MongoDB
    fetch('/update_mental_health_status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "user_id": "{{ user_data['_id'] }}",
            "result": resultValue
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            window.location.reload();

            // Update the mental health status displayed on the page
            var statusElement = document.getElementById('mentalHealthStatus');
            if (resultValue === 'yes') {
                statusElement.innerHTML = 'Yes, user have symptoms of depression.';
            } else if (resultValue === 'no') {
                statusElement.innerHTML = 'No, user does not have symptoms of depression.';
            } else {
                statusElement.innerHTML = 'N/A';
            }

        } else {
            console.error('Error:', data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}


function closePopup() {
    document.getElementById('optInMessage').style.display = 'none';
    document.getElementById('resultPopup').style.display = 'none';
}


function showHistory() {
    // Fetch and display mental health status history when the user clicks on the report icon
    fetch('/get_mental_health_history')
        .then(response => response.json())
        .then(data => {
            const historyList = document.getElementById('historyList');
            historyList.innerHTML = ''; // Clear previous history

            if (data.history.length > 0) {
                data.history.forEach(entry => {
                    const listItem = document.createElement('li');
                    listItem.textContent = `${entry.status} - ${entry.time}`;
                    historyList.appendChild(listItem);
                });
            } else {
                const listItem = document.createElement('li');
                listItem.textContent = 'No history available.';
                historyList.appendChild(listItem);
            }

            document.getElementById('historyPopup').style.display = 'flex';
        })
        .catch(error => console.error('Error:', error));
}


function closeHistoryPopup() {
    document.getElementById('historyPopup').style.display = 'none';
}