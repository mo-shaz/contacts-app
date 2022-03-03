# Imports
import os
import sys
import re
from flask import Flask, request, redirect, render_template, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import uuid


#######################################
#               CONFIG                #
#######################################

# Flask App initialisation
app = Flask(__name__)


# Check for important environment variables
try:
    db_user = os.environ['DB_USER']
    db_pass = os.environ['DB_PASS']

except Exception as e:
    app.logger.error("Database configuration failed")
    app.logger.error(f"Key {e} not found")
    sys.exit(1)


# Initialise the database for the first time
try:
    # Create connection
    init_connection = psycopg2.connect(dbname="postgres", user=db_user, password=db_pass)
    init_cursor = init_connection.cursor()
    init_connection.autocommit = True

    # Check if the database already exists
    check_query = "SELECT 1 FROM pg_database WHERE datname = 'contacts'"
    init_cursor.execute(check_query)
    init_connection.commit()
    res = init_cursor.fetchone()

    if res == None:
        
        # Execute the database creation query
        creation_query = "CREATE DATABASE contacts"
        init_cursor.execute(creation_query)
        init_connection.commit()
        app.logger.info("Database created")

    # Close the connection
    init_cursor.close()
    init_connection.close()

    # Make a connection for the table creation
    create_connection = psycopg2.connect(dbname="contacts", user=db_user, password=db_pass)
    create_cursor = create_connection.cursor()

    # Now create the tables
    create_users_table = """CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email TEXT NOT NULL,
        salt TEXT NOT NULL,
        hashed_pass TEXT NOT NULL,
        session_id TEXT
        );"""

    create_cursor.execute(create_users_table)
    create_connection.commit()
    app.logger.info("Table 'users' ready")

    create_contacts_query = """CREATE TABLE IF NOT EXISTS contacts (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        number TEXT NOT NULL,
        email TEXT NOT NULL,
        owner INTEGER REFERENCES users(id)
    );"""
    
    create_cursor.execute(create_contacts_query)
    create_connection.commit()
    app.logger.info("Table 'contacts' ready")

    # Close the connection
    create_cursor.close()
    create_connection.close()



except Exception as e:
    app.logger.error("Error creating database")
    app.logger.error(e)
    sys.exit(1)

#########################################
#               UTILITIES               #
#########################################

# Function that checks the validity of emails
def is_valid_email(email):
    # The pattern
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

    if re.fullmatch(regex, email):
        return True

    else:
        return False


# Function that makes the database connection
def connect_to_db():

    try:
        # Make a connection using psycopg2 and return the connection
        connection = psycopg2.connect(dbname="contacts", user=db_user, password=db_pass)
        return connection

    except Exception as e:
        app.logger.error("Error making Database connection")
        app.logger.error(e)
        sys.exit(1)




#####################################
#               ROUTES              #
#####################################

# Index Route
@app.route('/')
def index():

    # Get the cookies
    cookie = request.cookies.get('sid')

    if cookie == "None":
        return render_template('login.html')

    # Make the database connection
    connection = connect_to_db()
    cursor = connection.cursor()

    # Get the user details
    get_user_query = "SELECT id FROM users WHERE session_id = %s;"
    cursor.execute(get_user_query, (cookie,))
    connection.commit()
    user_id = cursor.fetchone()

    # If no user, show error
    if user_id == []:
        cursor.close()
        connection.close()
        return render_template('login.html')

    # Fetch all their contacts
    get_contacts_query = "SELECT * FROM contacts WHERE owner = %s;"
    cursor.execute(get_contacts_query, (user_id[0],))
    connection.commit()
    contacts = cursor.fetchall()

    # Close the connection
    cursor.close()
    connection.close()

    return render_template('contacts.html', data = contacts, user = user_id[0])




# Login Route
@app.route('/login', methods=["POST"])
def login():

    # Get the data
    email = request.form.get('email') or ""
    password = request.form.get('password') or ""

    if is_valid_email(email) == False:
        return 'Invalid Email'

    if len(password) < 8:
        return 'Password too short'

    # Check if the email is registered
    connection = connect_to_db()
    cursor = connection.cursor()

    # Construct a query to check for the user
    check_user_query = "SELECT * FROM users WHERE email = %s;"
    cursor.execute(check_user_query, (email,))
    connection.commit()
    result = cursor.fetchall()

    # If no user, return
    if result == []:
        # Close the connection
        cursor.close()
        connection.close()
        return 'No such user exist'

    # Check the password
    salt = result[0][2]
    password_hash = result[0][3]

    is_user_legit = check_password_hash(password_hash, password + salt)
    
    if is_user_legit == False:
        # Close the connection
        cursor.close()
        connection.close()
        return 'Wrong credentials'

    # If user is legit, generate session_id and set the cookie
    session_id = str(uuid.uuid4())

    # Update Database
    add_session_query = "UPDATE users SET session_id = %s WHERE email = %s;"
    cursor.execute(add_session_query, (session_id, email))
    connection.commit()

    # Set the response cookie
    response = make_response(redirect('/'))
    response.set_cookie('sid', session_id)

    # Close the connection
    cursor.close()
    connection.close()
    
    return response



# Signup Route
@app.route('/signup', methods=["POST"])
def signup():

    # Get the user data
    email = request.form.get('email') or ""
    password = request.form.get('password') or ""
    salt = request.form.get('salt') or ""

    # Validate the data
    if is_valid_email(email) == False:
        return 'Invalid Email'

    if len(password) < 8:
        return 'Password too short'

    if salt == "":
        return 'Empty Secret'

    # Check if user with email already exist
    connection = connect_to_db()
    cursor = connection.cursor()

    check_user_query = "SELECT EXISTS (SELECT 1 FROM users WHERE email = %s);"
    cursor.execute(check_user_query, (email,))
    connection.commit()
    user_exists = cursor.fetchone()

    # If user already exists, return
    if user_exists[0] == True:
        return 'User already exists'

    # Hash the password
    hashed_password = generate_password_hash(password + salt)

    add_user_query = "INSERT INTO users(email, salt, hashed_pass) VALUES(%s, %s, %s);"

    # Execute and commit the query
    cursor.execute(add_user_query, (email, salt, hashed_password))
    connection.commit()

    # Close the connection
    cursor.close()
    connection.close()

    # Return to the login page
    return redirect('/')



# Logout route
@app.route('/logout')
def logout():

    # Set the cookie to None
    response = make_response(redirect('/'))
    response.set_cookie('sid', "None")

    return response


# Save contact route
@app.route('/save', methods=["POST"])
def save():

    # Get the cookie
    cookie = request.cookies.get('sid')

    # If no cookie, return to login
    if cookie == None or cookie == "None":
        return redirect('/')

    # Get the form data
    name = request.form.get('name') or "NIL"
    number = request.form.get('number') or "NIL"
    email = request.form.get('email') or "NIL"

    # Get a database connection
    connection = connect_to_db()
    cursor = connection.cursor()

    # Get the user_id from the database
    get_user_query = "SELECT id FROM users WHERE session_id = %s;"
    cursor.execute(get_user_query, (cookie,))
    connection.commit()
    user_id = cursor.fetchone()

    # Add the contact to the database
    add_contact_query = "INSERT INTO contacts(name, number, email, owner) VALUES(%s, %s, %s, %s);"
    cursor.execute(add_contact_query, (name, number, email, user_id[0]))
    connection.commit()
    
    # Close the connection
    cursor.close()
    connection.close()

    return redirect('/') 



# Delete contact route
@app.route('/delete/<int:id>')
def delete(id):

    # Check the cookie
    cookie = request.cookies.get('sid')

    if cookie == None or cookie == "None":
        return redirect('/')

    # Make database connection
    connection = connect_to_db()
    cursor = connection.cursor()

    # Get the user id of the cookie holder
    get_user_id = "SELECT id FROM users WHERE session_id = %s;"
    cursor.execute(get_user_id, (cookie,))
    connection.commit()
    user_id = cursor.fetchone()[0]

    # Get the owner of the contact
    get_owner_id = "SELECT owner FROM contacts WHERE id = %s;"
    cursor.execute(get_owner_id, (id,))
    connection.commit()
    owner_id = cursor.fetchone()

    # Check if the contact even exist
    if owner_id == None or owner_id == []:
        return redirect('/')

    owner_id = owner_id[0]

    # Check if the user requesting to delete the contact is the owner of the contact
    if user_id != owner_id:
        # Close the connection
        cursor.close()
        connection.close()
        return render_template('login.html')

    # Construct the delete query
    delete_query = "DELETE FROM contacts WHERE id = %s;"
    cursor.execute(delete_query, (id,))
    connection.commit()

    # Close the connection
    cursor.close()
    connection.close()
    
    return redirect('/')

