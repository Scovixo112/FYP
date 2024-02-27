from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, SubmitField, TextAreaField
from pymongo import MongoClient
from wtforms.validators import DataRequired
from bson import ObjectId
from flask_socketio import SocketIO
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'S\x92z\xe7\x1e\x8b\x87+\x95E\x10\x8d\xf2\xf3bM'
socketio = SocketIO(app)

# Connect to MongoDB
client = MongoClient('mongodb+srv://qianerlee:826455@cluster0.gg05xge.mongodb.net/')
db = client['users']
users_collection = db['Data']
posts_collection = db['posts']


#User information
class UserProfileForm(FlaskForm):
    name = StringField('Name')
    age = StringField('Age')
    gender = StringField('Gender')
    phone_number = StringField('Phone Number')
    todo_task = StringField('Todo Task')
    submit = SubmitField('Save Changes')


# Add a new form for editing user information
class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    gender = StringField('Gender', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Save Changes')


# Define a form for creating posts
class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()])
    submit = SubmitField('Create Post')

# Assuming you have a CreateCommentForm class defined for comment creation
class CreateCommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit_comment = SubmitField('Submit Comment')


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # Check if the email is in the users collection and the password matches
    user = users_collection.find_one({'email': email, 'password': password})

    if user:
        # Debugging statements
        print(f"Login successful for {email}")

        # Successful login, store user ID in session and redirect to home page
        session['user_id'] = str(user['_id'])  # Convert ObjectId to string for session storage
        print(f"User ID stored in session: {session['user_id']}")
        return redirect(url_for('home'))
    else:
        # Debugging statements
        print(f"Login failed for {email}")

        # Failed login, redirect back to the login page with an error message
        return render_template('login.html', error='Invalid email or password')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']

    # Check if the email is already taken
    existing_user = users_collection.find_one({'email': email})

    if existing_user:
        return render_template('signup.html', error='User already exists')

    # Add the new user to the users collection
    users_collection.insert_one({'email': email, 'password': password})

    # Debugging statements
    print(f"User registered: {email}")

    # Log in the new user and redirect to the home page
    session['email'] = email
    return redirect(url_for('home'))


@app.route('/home')
def home():
    # Check if the user is logged in
    if 'email' in session:
        email = session['email']

        # Fetch additional data from MongoDB
        user_data = users_collection.find_one({'email': email})

        # Ensure user_data and emergency_contact exist in the structure
        emergency_contact = user_data.get('emergency_contact', {})

        return render_template('home.html', email=email, data={'emergency_contact': emergency_contact})
    else:
        # Redirect to the login page if not logged in
        return redirect(url_for('index'))


@app.route('/activities')
def activities():
    return render_template('activities.html')


@app.route('/story')
def story():
    return render_template('story.html')


@app.route('/music')
def music():
    return render_template('music.html')


@app.route('/sport')
def sport():
    return render_template('sport.html')


@app.route('/meditation')
def meditation():
    return render_template('meditation.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Check if the user is logged in
    if 'email' in session:
        email = session['email']

        # Fetch user data from MongoDB
        user_data = users_collection.find_one({'email': email})

        # Populate the form with existing data
        form = UserProfileForm(**user_data)

        if request.method == 'POST':
            # Update user data in MongoDB
            users_collection.update_one({'email': email}, {'$set': {
                'name': form.name.data,
                'age': form.age.data,
                'gender': form.gender.data,
                'phone_number': form.phone_number.data,
                'todo_list': user_data.get('todo_list', []) + [form.todo_task.data],
            }})

            flash('Changes saved successfully', 'success')
            return redirect(url_for('profile'))

        return render_template('profile.html', form=form, user_data=user_data)
    else:
        # Redirect to the login page if not logged in
        return redirect(url_for('index'))


# New route for editing user information
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    # Check if the user is logged in
    if 'email' in session:
        email = session['email']

        # Fetch user data from MongoDB
        user_data = users_collection.find_one({'email': email})

        # Initialize the edit profile form with existing user data
        form = EditProfileForm(obj=user_data)

        if form.validate_on_submit():
            # Update user data in MongoDB
            users_collection.update_one({'email': email}, {'$set': {
                'name': form.name.data,
                'age': form.age.data,
                'gender': form.gender.data,
                'phone_number': form.phone_number.data,
            }})

            # Redirect to the profile page after saving changes
            return redirect(url_for('profile'))

        return render_template('edit_profile.html', form=form, user_data=user_data)

    # Redirect to the login page if not logged in
    return redirect(url_for('index'))


@app.route('/create_todo', methods=['POST'])
def create_todo():
    try:
        # Check if the user is logged in
        if 'email' in session:
            email = session['email']

            # Fetch user data from MongoDB
            user_data = users_collection.find_one({'email': email})

            # Get data from the request
            data = request.get_json()

            # Update user data in MongoDB with the new todo
            users_collection.update_one({'email': email}, {'$set': {
                'todo_list': user_data.get('todo_list', []) + [{'todo_task': data['todo_task']}],
            }})

            return jsonify({"message": "Todo created successfully"})
        else:
            return jsonify({"error": "User not logged in"})

    except Exception as e:
        return jsonify({"error": str(e)})


# New route for retrieving todos
@app.route('/retrieve_todos', methods=['GET'])
def retrieve_todos():
    try:
        # Check if the user is logged in
        if 'email' in session:
            email = session['email']

            # Fetch user data from MongoDB
            user_data = users_collection.find_one({'email': email})

            # Retrieve the todo list from user data
            todo_list = user_data.get('todo_list', [])

            return jsonify({"todos": todo_list})
        else:
            return jsonify({"error": "User not logged in"})

    except Exception as e:
        return jsonify({"error": str(e)})


# # New route for updating a todo
# @app.route('/update_todo', methods=['POST'])
# def update_todo():
#     try:
#         # Check if the user is logged in
#         print("Reached update_todo route")

#         if 'email' in session:
#             email = session['email']

#             # Get data from the request
#             data = request.get_json()
#             user_id = data.get('user_id')
#             todo_task = data.get('todo_task')

#             print(f"Received data - user_id: {user_id}, todo_task: {todo_task}")

#             # Fetch user data from MongoDB
#             user_data = users_collection.find_one({'_id': ObjectId(user_id)})

#             print("User data from MongoDB:", user_data)

#             if user_data:
#                 # Update the specified todo in the user's todo list
#                 todo_list = user_data.get('todo_list', [])
#                 updated = False

#                 # Iterate through the array using index
#                 for i, todo in enumerate(todo_list):
#                     if i == int(user_id):
#                         todo['todo_task'] = todo_task
#                         updated = True
#                         break

#                 # If the todo was updated, update user data in MongoDB
#                 if updated:
#                     users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'todo_list': todo_list}})
#                     return jsonify({"message": "Todo updated successfully"})
#                 else:
#                     return jsonify({"message": "Todo not found"})
#             else:
#                 return jsonify({"message": "User not found"})

#         else:
#             return jsonify({"error": "User not logged in"})

#     except Exception as e:
#         return jsonify({"error": str(e)})


# New route for updating a todo
# @app.route('/update_todo', methods=['POST'])
# def update_todo():
#     try:
#         # Check if the user is logged in
#         if 'email' in session:
#             email = session['email']

#             # Get data from the request
#             data = request.get_json()
#             user_id = data.get('user_id')
#             old_todo_task = data.get('old_todo_task')  # Add a field for the old todo_task
#             new_todo_task = data.get('new_todo_task')

#             # Fetch user data from MongoDB
#             user_data = users_collection.find_one({'_id': ObjectId(user_id)})

#             if user_data:
#                 # Update the specified todo in the user's todo list
#                 todo_list = user_data.get('todo_list', {})
#                 updated = False

#                 # Iterate through the dictionary using keys
#                 for key in todo_list:
#                     if str(key) == old_todo_task:  # Convert the key to string for comparison
#                         todo_list[key] = new_todo_task  # Update the todo_task
#                         updated = True
#                         break


#                 # If the todo was updated, update user data in MongoDB
#                 if updated:
#                     users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'todo_list': todo_list}})
#                     return jsonify({"message": "Todo updated successfully"})
#                 else:
#                     return jsonify({"message": "Todo not found"})
#             else:
#                 return jsonify({"message": "User not found"})

#         else:
#             return jsonify({"error": "User not logged in"})

#     except Exception as e:
#         return jsonify({"error": str(e)})




# New route for deleting a todo
@app.route('/delete_todo', methods=['POST'])
def delete_todo():
    try:
        # Check if the user is logged in
        if 'email' in session:
            email = session['email']

            # Get data from the request
            data = request.get_json()
            user_id = data.get('user_id')
            todo_task = data.get('todo_task')

            # Fetch user data from MongoDB
            user_data = users_collection.find_one({'_id': ObjectId(user_id)})

            # Delete the specified todo from the user's todo list
            todo_list = user_data.get('todo_list', [])

            new_todo_list = [todo for todo in todo_list if str(todo['todo_task']) != todo_task]

            # If the todo was deleted, update user data in MongoDB
            if len(new_todo_list) < len(todo_list):
                users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'todo_list': new_todo_list}})
                return jsonify({"message": "Todo deleted successfully"})
            else:
                return jsonify({"message": "Todo not found"})

        else:
            return jsonify({"error": "User not logged in"})

    except Exception as e:
        return jsonify({"error": str(e)})



# Route to retrieve mental health status history
@app.route('/get_mental_health_history', methods=['GET'])
def get_mental_health_history():
    # Assuming user_id is stored in the session or provided in some way
    user_id = session.get('user_id')

    # Retrieve the user's mental health status history from MongoDB
    user_data = users_collection.find_one({'_id': ObjectId(user_id)})

    if user_data:
        history = user_data.get('mental_health_history', [])

        # Display all available entries if less than 10, otherwise display the latest 10
        history_to_display = history if len(history) < 10 else history[-10:]

        # Format timestamps for display
        formatted_history = []

        for entry in history_to_display:
            timestamp = entry['timestamp']

            # Check if the timestamp is a float (assumed to be Unix timestamp)
            if isinstance(timestamp, float):
                formatted_time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            else:
                # If timestamp is a string, directly use it
                formatted_time = timestamp

            formatted_history.append({'status': entry['status'], 'time': formatted_time})

        return jsonify({'history': formatted_history})
    else:
        return jsonify({'history': []})


# Update the mental health status route
@app.route('/update_mental_health_status', methods=['POST'])
def update_mental_health_status():
    user_id = request.json.get('user_id')
    result = request.json.get('result')

    # Map the radio button values to the desired mental health status
    mental_health_status_mapping = {
        'yes': 'Yes, user has symptoms of depression.',
        'no': 'No, user does not have symptoms of depression.'
    }

    # Update the mental health status in MongoDB
    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'mental_health_status': mental_health_status_mapping.get(result, 'N/A')}}
    )

    # Add the current result to the user's mental health status history
    timestamp = datetime.now().strftime('%y-%m-%d-%H-%M-%S')  # Format timestamp as YY-MM-DD-HH-MM-SS
    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$push': {'mental_health_history': {'status': mental_health_status_mapping.get(result, 'N/A'), 'timestamp': timestamp}}}
    )

    return jsonify({'message': 'Mental health status updated successfully'})


# New route for updating emergency contact from home page
@app.route('/update_emergency_contact_home', methods=['POST'])
def update_emergency_contact_home():
    try:
        # Check if the user is logged in
        if 'email' in session:
            email = session['email']

            # Get data from the request
            data = request.form.to_dict()
            user_id = users_collection.find_one({'email': email})['_id']

            # Update emergency contact in MongoDB
            users_collection.update_one({'_id': user_id}, {'$set': {
                'emergency_contact': {
                    'name': data.get('name'),
                    'gender': data.get('gender'),
                    'emergency_phone': data.get('emergency_phone'),
                }
            }})

            # Fetch updated emergency contact data
            updated_emergency_contact = users_collection.find_one({'_id': user_id}, {'emergency_contact': 1})['emergency_contact']

            return jsonify({"message": "Emergency contact updated successfully", "emergency_contact": updated_emergency_contact})

        else:
            return jsonify({"error": "User not logged in"})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/get_user_info', methods=['GET'])
def get_user_info():
    # Check if the user is logged in
    if 'email' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    # Retrieve the name from the session
    email = session['email']

    # Query MongoDB to retrieve user information based on the name
    user_data = users_collection.find_one({'email': email})

    if user_data:
        # Return user information as JSON
        return jsonify({'name': user_data['name']})
    else:
        return jsonify({'error': 'User not found'}), 404


@socketio.on('send_help_message')
def handle_help_message(data):
    name = data['username']  # 'username' instead of 'name'
    emergency_phone = data['emergency_phone']
    message_content = f'I am @{name}, please help me.'

    # Simulate sending a message back to the user
    socketio.emit('receive_help_message', {'content': message_content}, room=emergency_phone)


# New route for the community area
@app.route('/community_area')
def community_area():
    # Fetch all posts from the posts collection
    posts = posts_collection.find()

    # Create an instance of CreatePostForm
    create_post_form = CreatePostForm()

    return render_template('community_area.html', posts=posts, create_post_form=create_post_form)

# New route for creating a post
@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    form = CreatePostForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        # Create a new post and store it in the posts collection
        post_data = {
            'title': title,
            'content': content,
            'comments': [],
            'created_at': datetime.now()
        }
        posts_collection.insert_one(post_data)

        flash('Post created successfully', 'success')
        return redirect(url_for('community_area'))

    return render_template('community_area.html', form=form, posts=posts_collection.find())


# New route for viewing a post and adding comments
@app.route('/view_post/<post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    post = posts_collection.find_one({'_id': ObjectId(post_id)})

    if not post:
        flash('Post not found', 'error')
        return redirect(url_for('community_area'))

    comment_form = CreateCommentForm()

    if comment_form.validate_on_submit():
        comment_content = comment_form.content.data

        # Add the comment to the post
        posts_collection.update_one({'_id': ObjectId(post_id)}, {'$push': {'comments': {'content': comment_content}}})

        flash('Comment added successfully', 'success')
        return redirect(url_for('view_post', post_id=post_id))

    return render_template('view_post.html', post=post, comment_form=comment_form)


# New route for adding a comment to a post
@app.route('/add_comment/<post_id>', methods=['POST'])
def add_comment(post_id):
    post = posts_collection.find_one({'_id': ObjectId(post_id)})

    if not post:
        return jsonify({"error": "Post not found"}), 404

    comment_form = CreateCommentForm()

    if comment_form.validate_on_submit():
        comment_content = comment_form.content.data

        # Add the comment to the post
        posts_collection.update_one({'_id': ObjectId(post_id)}, {'$push': {'comments': {'content': comment_content}}})

        # Return the updated comments
        updated_post = posts_collection.find_one({'_id': ObjectId(post_id)})
        updated_comments = [{'content': comment['content']} for comment in updated_post.get('comments', [])]

        return jsonify({"success": True, "message": "Comment added successfully", "comments": updated_comments})
    else:
        return jsonify({"error": "Invalid form data"}), 400


if __name__ == '__main__':
    app.run(debug=True)
