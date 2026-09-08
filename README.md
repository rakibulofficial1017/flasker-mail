# Flasker Mail Application

## Description

This project is a web-based email application built as my final project for CS50x.

The application allows users to create accounts, log in, send and receive emails, search their inbox, reply to messages, and manage their emails. It uses Flask as the web framework and SQLite as the relational database.

The project was designed to demonstrate how a complete web application can combine Python, SQL, HTML, CSS, and JavaScript.

## Features

* User registration
* User login and logout
* Password hashing
* Session-based authentication
* Inbox
* Sent folder
* Compose and send emails
* Reply to emails
* Read and unread email states
* Unread email count
* Email search
* Individual email viewer
* Email deletion
* Custom right-click context menu for deleting emails
* Protection against users accessing emails that do not belong to them

## Technologies

### Backend

* Python
* Flask
* Flask-Session
* SQLite
* SQL

### Frontend

* HTML
* CSS
* JavaScript
* Jinja templates

## Database

The application uses SQLite with two main tables: `users` and `emails`.

### Users

The `users` table stores account information.

| Column          | Type    | Description                       |
| --------------- | ------- | --------------------------------- |
| `user_id`       | INTEGER | Primary key identifying the user  |
| `username`      | TEXT    | Unique username                   |
| `display_name`  | TEXT    | Name displayed in the application |
| `password_hash` | TEXT    | Securely hashed password          |

### Emails

The `emails` table stores messages.

| Column         | Type    | Description                              |
| -------------- | ------- | ---------------------------------------- |
| `email_id`     | INTEGER | Primary key identifying the email        |
| `sender_id`    | INTEGER | ID of the user who sent the email        |
| `recipient_id` | INTEGER | ID of the user who received the email    |
| `time_sent`    | TEXT    | Time the email was sent                  |
| `title`        | TEXT    | Email subject                            |
| `description`  | TEXT    | Email body                               |
| `is_read`      | INTEGER | Whether the recipient has read the email |

The `sender_id` and `recipient_id` columns are foreign keys referencing the `users` table.

This allows the application to associate every email with both a sender and a recipient.

## How It Works

### Authentication

When a user registers, their password is passed through Werkzeug's password hashing system before being stored in the database.

The original password is therefore not stored directly.

When logging in, the application retrieves the user's stored password hash and uses `check_password_hash()` to verify the supplied password.

Flask sessions are used to keep track of the currently logged-in user.

### Sending an Email

When a user composes an email, they enter the recipient's username, a subject, and a message.

The application looks up the recipient's `user_id` and creates a new record in the `emails` table containing the sender and recipient IDs.

### Inbox

The inbox retrieves emails where the current user's ID matches `recipient_id`.

The application uses SQL joins to retrieve information about the sender from the `users` table.

Emails are ordered by their sending time, with the newest emails appearing first.

### Read and Unread Emails

Each email has an `is_read` value.

* `0` means unread
* `1` means read

When a recipient opens an unread email, the application updates its `is_read` value to `1`.

The inbox also counts unread emails so that the user can see how many unread messages they have.

### Search

The inbox includes a search function.

The search query is compared against:

* Sender username
* Email subject
* Email body

Parameterized SQL queries are used when performing the search.

### Reply

The reply function determines the other participant in the email conversation and automatically fills in the recipient.

The subject is also prefixed with `Re:`.

The reply is then sent as a new email.

### Deleting Emails

Users can delete emails from their inbox using a custom right-click context menu.

The deletion request uses an HTTP POST request rather than GET because deleting an email changes the database.

The SQL query also verifies that the email belongs to the currently logged-in recipient before deleting it.

## Security

Several measures are used to protect the application:

### Password Hashing

Passwords are hashed using Werkzeug before being stored in the database.

### Parameterized SQL Queries

User input is passed to SQLite using parameterized queries such as:

```python
db.execute("""
    SELECT user_id
    FROM users
    WHERE username = ?
""", (username,))
```

This prevents user input from being interpreted as part of the SQL statement.

### Session Authentication

Protected pages check whether a user is logged in before allowing access.

### Authorization

When viewing an email, the application verifies that the logged-in user is either the sender or recipient of that email.

Similarly, deleting an email requires the logged-in user to be its recipient.

## Project Structure

```text
mail/
│
├── main.py
├── emails.db
├── requirements.txt
├── schema.txt
├── flask_session/ <- this is generated by Flask-Session
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── inbox.html
│   ├── sent.html
│   ├── compose.html
│   └── email.html
│
└── static/
    └── css
        └── styles.css
```

## Running the Application

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Then start the Flask application:

```bash
flask run
```

Open the address provided by Flask in a web browser.

## Design Decisions

SQLite was chosen because the application is relatively small and does not require a separate database server.

The database uses separate `users` and `emails` tables instead of storing usernames directly inside email records. This allows the application to use primary keys, foreign keys, and SQL joins while avoiding unnecessary duplication of user information.

Flask sessions were chosen to maintain authentication state between requests.

Jinja templates are used to generate the HTML pages from data retrieved by Flask.

JavaScript is used for interactive functionality such as the custom email context menu.

## What I Learned

Through this project, I learned how the different components of a web application interact with each other.

In particular, the project gave me practical experience with:

* Flask routing
* HTTP GET and POST requests
* Sessions
* Authentication
* Password hashing
* SQLite
* Relational database design
* Primary and foreign keys
* SQL joins
* Parameterized SQL queries
* CRUD operations
* Jinja templating
* HTML and CSS
* JavaScript DOM manipulation
* Connecting a frontend to a Python backend

The project also helped me understand how a database-driven application can be structured rather than treating the frontend and backend as separate pieces.


## Video Demo

https://youtu.be/oJfj5zaftWs