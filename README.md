
# CONTACTS APP

## Pre-requisites to running the app

- Postgres Database (v13.0^) must be installed on your system (<https://www.postgresql.org/download/>)
- Python (v3.0^) (<https://www.python.org/downloads/>)
- Pipenv installed (if not, just try "pip install pipenv")

## Instructions to run the app

- Clone the repository:

        git clone [repo-name]

- Open the folder in your preferred code editor/terminal.

- Change the contents of .env file to configure your database ("DB_USER" and "DB_PASS"):

        DB_USER="[YOUR_DB_USER]"
        DB_PASS="[YOUR_DB_PASS]"

- Run the command in your terminal to load the environment:

        pipenv shell

- Run the command in your terminal to install the necessary dependencies:

        pipenv install

- Run the command in your terminal to run the application:

        flask run

- Go to "http://localhost:5000" from your preferred browser to view the application.
