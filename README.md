Here is the README file for your Flask application:

---

# Movie Booking System

## Overview
This is a simple movie booking system built with Flask, SQLite, and HTML/CSS. It allows users to register, log in, book movies, and manage bookings. Admin users have additional privileges to manage movies and bookings.

## Features
- User registration and login with password hashing.
- Booking movies from a list of available movies.
- Viewing and managing bookings.
- Admin dashboard for managing movies and bookings.
- Transaction management and password change functionality.
- Security features including password attempts tracking and triggers for logging password changes.

## Prerequisites
- Python 3.x
- Flask
- SQLite

## Installation

1. Clone the repository:

```sh
git clone https://github.com/yourusername/movie-booking-system.git
cd movie-booking-system
```

2. Install the required packages:

```sh
pip install flask
pip install werkzeug
```

3. Initialize the database:

Run the following command to create the necessary database and tables:

```sh
python app.py
```

## Project Structure

```
movie-booking-system/
│
├── app.py
├── database/
│   └── movie_booking.db
├── templates/
│   ├── home.html
│   ├── register.html
│   ├── login.html
│   ├── booking.html
│   ├── confirm.html
│   ├── transactions.html
│   ├── my_bookings.html
│   └── change_password.html
├── static/
│   └── styles.css
└── README.md
```

## Running the Application

To start the Flask application, run:

```sh
python app.py
```

Open your web browser and navigate to `http://127.0.0.1:5000/` to access the application.

## Routes

- `/` - Home page
- `/register` - User registration page
- `/login` - User login page
- `/booking` - Movie booking page (requires login)
- `/book/<movie_id>` - Book a specific movie (requires login)
- `/transactions` - View transactions (requires login)
- `/my_bookings` - View personal bookings (requires login)
- `/change_password` - Change password (requires login)
- `/cancel_booking` - Cancel a booking (requires login)
- `/admin_dashboard` - Admin dashboard (requires admin login)

## Database Schema

### Users Table

| Column             | Type    | Description                     |
|--------------------|---------|---------------------------------|
| id                 | INTEGER | Primary key, auto-increment     |
| username           | TEXT    | Unique                          |
| password           | TEXT    | Hashed password                 |
| is_admin           | INTEGER | 1 for admin, 0 for regular user |
| password_attempts  | INTEGER | Number of failed login attempts |
| last_failed_attempt| TEXT    | Timestamp of the last failed attempt |

### Movies Table

| Column      | Type    | Description         |
|-------------|---------|---------------------|
| movie_id    | INTEGER | Primary key         |
| movie_name  | TEXT    | Name of the movie   |
| release_date| TEXT    | Release date        |
| director    | TEXT    | Director of the movie|
| cast        | TEXT    | Cast of the movie   |
| budget      | TEXT    | Budget of the movie |
| duration    | TEXT    | Duration of the movie|
| rating      | TEXT    | Rating of the movie |
| movie_price | REAL    | Price of the movie  |

### Bookings Table

| Column  | Type    | Description                     |
|---------|---------|---------------------------------|
| id      | INTEGER | Primary key, auto-increment     |
| user_id | INTEGER | Foreign key referencing users(id) |
| movie_id| TEXT    | Foreign key referencing movies(movie_id) |

### Transactions Table

| Column          | Type    | Description                     |
|-----------------|---------|---------------------------------|
| Transaction_id  | INTEGER | Primary key, auto-increment     |
| booking_id      | INTEGER | Foreign key referencing bookings(id) |
| amount          | REAL    | Amount of the transaction       |
| transaction_date| TEXT    | Date of the transaction         |

### Password Change Log Table

| Column     | Type      | Description                 |
|------------|-----------|-----------------------------|
| id         | INTEGER   | Primary key, auto-increment |
| username   | TEXT      | Username                    |
| changed_at | TIMESTAMP | Timestamp of change         |

## Triggers

### `log_password_change`

Logs password changes in the `password_change_log` table.

### `delete_transaction_on_booking_cancel`

Deletes related transactions when a booking is canceled.

## Sample Data

The application includes sample movie data for demonstration purposes. The sample movies are inserted into the `movies` table during the initialization.

## Security Features

- Passwords are hashed using `werkzeug.security.generate_password_hash`.
- Users are limited to 5 login attempts within 30 seconds.
- Admin users have additional management privileges.

## License

This project is licensed under the MIT License.

---

Enjoy using the Movie Booking System! If you encounter any issues, please feel free to open an issue on the repository.
