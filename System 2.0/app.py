from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, SubmitField
from pymongo import MongoClient
from wtforms.validators import DataRequired
from bson import ObjectId

app = Flask(__name__)
app.secret_key = 'S\x92z\xe7\x1e\x8b\x87+\x95E\x10\x8d\xf2\xf3bM'

# Connect to MongoDB
client = MongoClient('mongodb+srv://qianerlee:826455@cluster0.gg05xge.mongodb.net/')
db = client['users']
users_collection = db['Data']


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


#Mental Health Information
class TakeTestForm(FlaskForm):
    # Define the fields for the mental health test form, if needed
    # Example: question1 = StringField('Question 1')
    question1 = RadioField('1. Have you ever been told by a doctor or other health worker that you have depression?',
                           choices=[('yes', 'Yes'), ('no', 'No')])

    question2 = RadioField('2. During the last 12 months, have you had a period lasting several days when you felt sad, empty, or depressed?',
                           choices=[('yes', 'Yes'), ('no', 'No')])

    submit = SubmitField('Submit Test')


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

        # Successful login, store user in session and redirect to home page
        # use session to store the user's login status
        session['email'] = email
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
        return render_template('home.html', email=email)
    else:
        # Redirect to the login page if not logged in
        return redirect(url_for('index'))

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

# New route for updating a todo
@app.route('/update_todo/<string:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    try:
        # Check if the user is logged in
        if 'email' in session:
            email = session['email']

            # Fetch user data from MongoDB
            user_data = users_collection.find_one({'email': email})

            # Get data from the request
            data = request.get_json()

            # Update the specified todo in the user's todo list
            todo_list = user_data.get('todo_list', [])
            for todo in todo_list:
                if str(todo['_id']) == todo_id:
                    todo.update({'todo_task': data.get('todo_task', todo.get('todo_task'))})

            # Update user data in MongoDB
            users_collection.update_one({'email': email}, {'$set': {'todo_list': todo_list}})
            return jsonify({"message": "Todo updated successfully"})

        else:
            return jsonify({"error": "User not logged in"})

    except Exception as e:
        return jsonify({"error": str(e)})

# New route for deleting a todo
@app.route('/delete_todo', methods=['POST'])
def delete_todo():
    print("sucessfully deleted")
    try:
        # Check if the user is logged in
        if 'email' in session:
            email = session['email']

            # Fetch user data from MongoDB
            user_data = users_collection.find_one({'email': email})

            # Delete the specified todo from the user's todo list
            todo_list = user_data.get('todo_list', [])
            new_todo_list = [todo for todo in todo_list if str(todo['_id']) != 123]

            # If the todo was deleted, update user data in MongoDB
            if len(new_todo_list) < len(todo_list):
                users_collection.update_one({'email': email}, {'$set': {'todo_list': new_todo_list}})
                return jsonify({"message": "Todo deleted successfully"})
            else:
                return jsonify({"message": "Todo not found"})

        else:
            return jsonify({"error": "User not logged in"})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/take_test', methods=['GET', 'POST'])
def take_test():
    form = TakeTestForm()

    if form.validate_on_submit():
        # Process the form data, store it in the database, etc.
        # You can access the user's response using form.question1.data and form.question2.data
        # For example, print the responses:
        print(f"Response to Question 1: {form.question1.data}")
        print(f"Response to Question 2: {form.question2.data}")

        # Redirect to another page or render a confirmation message
        return redirect(url_for('confirmation'))

    return render_template('take_test.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
