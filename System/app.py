from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'S\x92z\xe7\x1e\x8b\x87+\x95E\x10\x8d\xf2\xf3bM'

# Connect to MongoDB
client = MongoClient('mongodb+srv://qianerlee:826455@cluster0.gg05xge.mongodb.net/')
db = client['users']
users_collection = db['Data']

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

if __name__ == '__main__':
    app.run(debug=True)
