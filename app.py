from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.secret_key = 'kotharipratham'

def init_db():
    if not os.path.exists('database'):
        os.makedirs('database')

    con = sqlite3.connect('./database/movie_booking.db')
    cur = con.cursor()


    cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT NOT NULL,
                is_admin INTEGER,
                password_attempts INTEGER DEFAULT 0,
                last_failed_attempt TEXT
            )
        ''')


    cur.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            movie_id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT,
            movie_name TEXT,
            release_date TEXT,
            director TEXT,
            cast TEXT,
            budget TEXT,
            duration TEXT,
            rating TEXT,
            movie_price REAL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            movie_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
        )
    ''')

    cur.execute('''
           CREATE TABLE IF NOT EXISTS transactions (
               Transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
               booking_id INTEGER,
               amount REAL,
               transaction_date TEXT,
               FOREIGN KEY (booking_id) REFERENCES bookings(id)
           )
       ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS password_change_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

    # Create the log_password_change trigger
    cur.execute('''
        CREATE TRIGGER IF NOT EXISTS log_password_change
        AFTER UPDATE OF password ON users
        BEGIN
            INSERT INTO password_change_log (username)
            VALUES (OLD.username);
        END;
        ''')

    cur.execute('''
        CREATE TRIGGER IF NOT EXISTS delete_transaction_on_booking_cancel
        AFTER DELETE ON bookings
        FOR EACH ROW
        BEGIN
            DELETE FROM transactions WHERE booking_id = OLD.id;
        END;
        ''')
    # Insert sample movies
    movies = [
        ("001", "Dilwale Dulhania Le Jayenge", "1995", "Aditya Chopra", "Shah Rukh Khan, Kajol", "4 Crores", "3", "4.5",350),
        ("002", "Kabhi Khushi Kabhie Gham", "2001", "Karan Johar", "Shah Rukh Khan, Amitabh Bachchan", "60 Crores", "3.5", "4.0",400),
        ("003", "3 Idiots", "2009", "Rajkumar Hirani", "Aamir Khan, Kareena Kapoor", "50 Crores", "2.5", "4.5",325),
        ("004", "Zindagi Na Milegi Dobara", "2011", "Zoya Akhtar", "Hrithik Roshan, Farhan Akhtar", "75 Crores", "2.5", "4.0",500),
        ("005", "Bajrangi Bhaijaan", "2015", "Kabir Khan", "Salman Khan, Harshaali Malhotra", "100 Crores", "2.0", "4.5",350),
        ("006", "Queen", "2013", "Vikas Bahl", "Kangana Ranaut, Rajkummar Rao", "15 Crores", "2.5", "4.0",360),
        ("007", "Piku", "2015", "Shoojit Sircar", "Amitabh Bachchan, Deepika Padukone", "40 Crores", "2.0", "4.2",370),
        ("008", "Andhadhun", "2018", "Sriram Raghavan", "Ayushmann Khurrana, Tabu", "30 Crores", "2.5", "4.5",480),
        ("009", "Barfi!", "2012", "Anurag Basu", "Ranbir Kapoor, Priyanka Chopra", "40 Crores", "2.5", "4.3",490),
        ("010", "Tumbbad", "2018", "Rahi Anil Barve", "Sohum Shah, Jyoti Malshe", "10 Crores", "2.0", "4.6",300),
        ("011", "Dangal", "2016", "Nitesh Tiwari", "Aamir Khan, Sakshi Tanwar", "90 Crores", "2.5", "4.7",250),
        ("012", "Batla House", "2019", "Nikkhil Advani", "John Abraham, Mrunal Thakur", "30 Crores", "2.5", "4.0",370),
        ("013", "Kal Ho Naa Ho", "2003", "Nikhil Advani", "Shah Rukh Khan, Preity Zinta", "55 Crores", "2.5", "4.5",500),
        ("014", "Dhoom 2", "2006", "Sanjay Gadhvi", "Hrithik Roshan, Aishwarya Rai", "85 Crores", "2.5", "4.0",300),
        ("015", "Gully Boy", "2019", "Zoya Akhtar", "Ranveer Singh, Alia Bhatt", "40 Crores", "2.0", "4.4",340),
        ("016", "Aashiqui 2", "2013", "Mohit Suri", "Aditya Roy Kapur, Shraddha Kapoor", "20 Crores", "2.5", "4.3",240),
        ("017", "Sultan", "2016", "Ali Abbas Zafar", "Salman Khan, Anushka Sharma", "100 Crores", "2.5", "4.0",250),
        ("018", "Dil Chahta Hai", "2001", "Farhan Akhtar", "Aamir Khan, Saif Ali Khan", "60 Crores", "3.0", "4.5",260),
        ("019", "Chennai Express", "2013", "Rohit Shetty", "Shah Rukh Khan, Deepika Padukone", "100 Crores", "2.5", "4.1",290),
        ("020", "Wake Up Sid", "2009", "Ayan Mukerji", "Ranbir Kapoor, Konkona Sen Sharma", "15 Crores", "2.5", "4.0",490),
        ("021", "Jab We Met", "2007", "Imtiaz Ali", "Shahid Kapoor, Kareena Kapoor", "25 Crores", "2.5", "4.2",500),
        ("022", "Mera Naam Joker", "1970", "Raj Kapoor", "Raj Kapoor, Simi Garewal", "20 Crores", "3.0", "3.5",200),
        ("023", "Sholay", "1975", "Ramesh Sippy", "Amitabh Bachchan, Dharmendra", "15 Crores", "3.0", "4.7",300),
        ("024", "Kuch Kuch Hota Hai", "1998", "Karan Johar", "Shah Rukh Khan, Kajol", "40 Crores", "2.5", "4.5",400),
        ("025", "Taal", "1999", "Subhash Ghai", "Anil Kapoor, Aishwarya Rai", "30 Crores", "3.0", "4.1",500),
        ("026", "Rang De Basanti", "2006", "Rakeysh Omprakash Mehra", "Aamir Khan, Siddharth", "25 Crores", "2.5", "4.4",250),
        ("027", "Lagaan", "2001", "Ashutosh Gowariker", "Aamir Khan, Gracy Singh", "50 Crores", "2.5", "4.5",350),
        ("028", "Koi... Mil Gaya", "2003", "Rakesh Roshan", "Hrithik Roshan, Preity Zinta", "35 Crores", "2.5", "4.0",450),
        ("029", "Chakde! India", "2007", "Shimit Amin", "Shah Rukh Khan, Vidya Malvade", "30 Crores", "2.5", "4.5",550),
        ("030", "Mughal-e-Azam", "1960", "K. Asif", "Dilip Kumar, Madhubala", "10 Crores", "3.0", "4.6",370),
        ("031", "Pyaasa", "1957", "Guru Dutt", "Guru Dutt, Waheeda Rehman", "5 Crores", "3.0", "4.7",360),
        ("032", "Devdas", "2002", "Sanjay Leela Bhansali", "Shah Rukh Khan, Aishwarya Rai", "55 Crores", "3.0", "4.3",260),
        ("033", "Aashiqui", "1990", "Mahesh Bhatt", "Anu Aggarwal, Rahul Roy", "7 Crores", "3.0", "4.2",280),
        ("034", "Bobby", "1973", "Raj Kapoor", "Rishi Kapoor, Dimple Kapadia", "10 Crores", "3.0", "4.0",440),
        ("035", "Jab Tak Hai Jaan", "2012", "Yash Chopra", "Shah Rukh Khan, Katrina Kaif", "70 Crores", "2.5", "4.1",420)
    ]

    cur.executemany('''
        INSERT OR IGNORE INTO movies (movie_id, movie_name, release_date, director, cast, budget, duration, rating, movie_price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', movies)

    con.commit()
    con.close()

init_db()

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/logout', methods = ["POST"])
def logout():
    session.pop('username', None)
    session.pop('is_admin', None)
    return redirect(url_for('home'))


def get_db_connection():
    db_path = './database/movie_booking.db'
    print(f"Database path: {os.path.abspath(db_path)}")
    print(f"Database exists: {os.path.exists(db_path)}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = 1 if 'is_admin' in request.form else 0

        # Validate password length
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        # Validate password contains only alphanumeric characters
        if not password.isalnum():
            flash('Password must contain only alphanumeric characters.', 'danger')
            return render_template('register.html')

        conn = get_db_connection()

        # Check if the users table exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if not cursor.fetchone():
            print("Error: users table does not exist")
            return "Error: users table does not exist", 500

        try:
            conn.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                         (username, generate_password_hash(password), is_admin))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.', 'danger')
        finally:
            conn.close()

    return render_template('register.html')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#
#         conn = get_db_connection()
#         user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
#         conn.close()
#
#         if user and check_password_hash(user['password'], password):
#             session['user_id'] = user['id']
#             session['username'] = user['username']
#             session['is_admin'] = user['is_admin']
#             flash('Login successful!', 'success')
#             if user['is_admin']:
#                 return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard if admin
#             else:
#                 return redirect(url_for('booking_page'))  # Redirect to booking page if not admin
#         else:
#             flash('Invalid username or password.', 'danger')
#
#     return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user:
            user = dict(user)

            # Check if the user has failed too many login attempts
            if user['password_attempts'] >= 5:
                last_failed_attempt = datetime.datetime.strptime(user['last_failed_attempt'], '%Y-%m-%d %H:%M:%S')
                if (datetime.datetime.now() - last_failed_attempt).total_seconds() < 30:
                    flash('Too many failed login attempts. Please wait 30 seconds.', 'danger')
                    conn.close()
                    return render_template('login.html')

                # Reset password attempts if the time limit has passed
                conn.execute('UPDATE users SET password_attempts = 0 WHERE username = ?', (username,))
                conn.commit()

            if check_password_hash(user['password'], password):
                # Successful login
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['is_admin'] = user['is_admin']
                flash('Login successful!', 'success')
                conn.execute('UPDATE users SET password_attempts = 0 WHERE username = ?', (username,))
                conn.commit()
                conn.close()
                return redirect(url_for('admin_dashboard') if user['is_admin'] else url_for('booking_page'))
            else:
                # Failed login attempt
                remaining_attempts = 4 - user['password_attempts']
                flash(f'Invalid username or password. You have {remaining_attempts} attempts left.', 'danger')
                conn.execute('UPDATE users SET password_attempts = password_attempts + 1, last_failed_attempt = ? WHERE username = ?', (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), username))
                conn.commit()
        else:
            flash('Invalid username or password.', 'danger')

        conn.close()

    return render_template('login.html')


@app.route('/booking', methods=['GET'])
def booking_page():
    con = sqlite3.connect('database/movie_booking.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM movies')
    movies = cur.fetchall()
    con.close()
    return render_template('booking.html', movies=movies)


@app.route('/book/<string:movie_id>', methods=['POST'])
def book_movie(movie_id):
    if 'username' not in session:
        flash('You must be logged in to book a movie.')
        return redirect(url_for('login'))

    con = sqlite3.connect('./database/movie_booking.db')
    cur = con.cursor()
    cur.execute('SELECT id FROM users WHERE username = ?', (session['username'],))
    user_id = cur.fetchone()[0]

    try:
        cur.execute('INSERT INTO bookings (user_id, movie_id) VALUES (?, ?)', (user_id, movie_id))
        con.commit()

        # Get the movie details and calculate the transaction amount
        cur.execute('SELECT movie_price FROM movies WHERE movie_id = ?', (movie_id,))
        movie_price = cur.fetchone()[0]

        # Create a transaction record
        cur.execute('SELECT id FROM bookings WHERE user_id = ? AND movie_id = ?', (user_id, movie_id))
        booking_id = cur.fetchone()[0]
        transaction_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute('INSERT INTO transactions (booking_id, amount, transaction_date) VALUES (?, ?, ?)',
                    (booking_id, movie_price, transaction_date))
        con.commit()

    except sqlite3.IntegrityError:
        flash('You have already booked this movie.')

    cur.execute('SELECT * FROM movies WHERE movie_id = ?', (movie_id,))
    movie = cur.fetchone()
    con.close()

    return render_template('confirm.html', movie=movie)


@app.route('/transactions')
def transactions():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view your transactions.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT transactions.Transaction_id, movies.movie_name, movies.movie_id, transactions.transaction_date, transactions.amount
        FROM transactions
        JOIN bookings ON transactions.booking_id = bookings.id
        JOIN movies ON bookings.movie_id = movies.movie_id
        WHERE bookings.user_id = ?
    ''', (user_id,))

    transactions = cur.fetchall()
    conn.close()

    return render_template('transactions.html', transactions=transactions)


# @app.route('/my_bookings')
# def my_bookings():
#     if 'user_id' not in session:
#         flash('You need to log in first.', 'danger')
#         return redirect(url_for('home'))
#
#     user_id = session['user_id']
#     cursor = get_db_connection().cursor()
#     cursor.execute('SELECT * FROM bookings WHERE user_id = ?', (user_id,))
#     bookings = cursor.fetchall()
#     cursor.execute('SELECT * FROM movies WHERE movie_id IN (SELECT movie_id FROM bookings WHERE user_id = ?)', (user_id,))
#     movies = cursor.fetchall()
#     return render_template('my_bookings.html', bookings=bookings, movies=movies)
#
@app.route('/my_bookings')
def my_bookings():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('home'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all bookings for the user
    cursor.execute('SELECT * FROM bookings WHERE user_id = ?', (user_id,))
    bookings = cursor.fetchall()

    # Prepare a list to hold pairs of booking and movie
    booking_movie_pairs = []

    # For each booking, fetch the associated movie
    for booking in bookings:
        movie_id = booking['movie_id']
        cursor.execute('SELECT * FROM movies WHERE movie_id = ?', (movie_id,))
        movie = cursor.fetchone()
        booking_movie_pairs.append((booking, movie))

    conn.close()

    return render_template('my_bookings.html', booking_movie_pairs=booking_movie_pairs)


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        flash('You need to be logged in to change your password.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_password or not new_password or not confirm_password:
            flash('Please fill out all fields.', 'danger')
            return render_template('change_password.html')

        if new_password != confirm_password:
            flash('New password and confirm password do not match.', 'danger')
            return render_template('change_password.html')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (session['username'],)).fetchone()

        if not user or not check_password_hash(user['password'], current_password):
            flash('Current password is incorrect.', 'danger')
            conn.close()
            return render_template('change_password.html')

        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('change_password.html')

        if not new_password.isalnum():
            flash('Password must contain only alphanumeric characters.', 'danger')
            return render_template('change_password.html')

        conn.execute('UPDATE users SET password = ? WHERE username = ?',
                     (generate_password_hash(new_password), session['username']))
        conn.commit()
        conn.close()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('change_password.html')


@app.route('/cancel_booking', methods=['POST'])
def cancel_booking():
    booking_id = request.form['booking_id']
    db = get_db_connection()
    with db:
        db.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
    flash('Booking cancelled successfully.', 'success')
    return redirect(url_for('my_bookings'))


@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'username' not in session or not session.get('is_admin', False):
        flash('You do not have permission to access this page.')
        return redirect(url_for('home'))

    con = sqlite3.connect('database/movie_booking.db')
    cur = con.cursor()
    bookings = con.execute('SELECT * FROM bookings').fetchall()
    users = con.execute('SELECT * FROM users WHERE is_admin = 0').fetchall()
    if request.method == 'POST':
        if 'add_movie' in request.form:
            movie_id = request.form['movie_id']
            movie_name = request.form['movie_name']
            release_date = request.form['release_date']
            director = request.form['director']
            cast = request.form['cast']
            budget = request.form['budget']
            duration = request.form['duration']
            rating = request.form['rating']
            movie_price = request.form['movie_price']
            try:
                cur.execute('''
                    INSERT INTO movies (movie_id, movie_name, release_date, director, cast, budget, duration, rating, movie_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (movie_id, movie_name, release_date, director, cast, budget, duration, rating, movie_price))
                con.commit()
                flash('Movie added successfully.')
            except sqlite3.IntegrityError:
                flash('Movie ID already exists.')

        elif 'delete_movie' in request.form:
            movie_id = request.form['movie_id']
            cur.execute('DELETE FROM movies WHERE movie_id = ?', (movie_id,))
            con.commit()
            flash('Movie deleted successfully.')

        elif 'update_movie' in request.form:
            movie_id = request.form['movie_id']
            movie_name = request.form.get('movie_name')
            release_date = request.form.get('release_date')
            director = request.form.get('director')
            cast = request.form.get('cast')
            budget = request.form.get('budget')
            duration = request.form.get('duration')
            rating = request.form.get('rating')
            movie_price = request.form.get('movie_price')

            updates = []
            if movie_name:
                updates.append(f"movie_name = ?")
            if release_date:
                updates.append(f"release_date = ?")
            if director:
                updates.append(f"director = ?")
            if cast:
                updates.append(f"cast = ?")
            if budget:
                updates.append(f"budget = ?")
            if duration:
                updates.append(f"duration = ?")
            if rating:
                updates.append(f"rating = ?")
            if movie_price:
                updates.append(f"movie_price = ?")

            if updates:
                update_statement = ', '.join(updates)
                update_values = [val for val in [movie_name, release_date, director, cast, budget, duration, rating, movie_price] if val]
                update_values.append(movie_id)
                cur.execute(f'UPDATE movies SET {update_statement} WHERE movie_id = ?', tuple(update_values))
                con.commit()
                flash('Movie updated successfully.')

    cur.execute('SELECT * FROM bookings')
    bookings = cur.fetchall()
    con.close()
    return render_template('admin_dashboard.html', bookings=bookings, users = users)


@app.route('/add_movie', methods=['POST'])
def add_movie():
    if 'username' not in session or not session.get('is_admin', False):
        flash('You do not have permission to access this page.')
        return redirect(url_for('home'))

    movie_id = request.form['movie_id']
    movie_name = request.form['movie_name']
    release_date = request.form['release_date']
    director = request.form['director']
    cast = request.form['cast']
    budget = request.form['budget']
    duration = request.form['duration']
    rating = request.form['rating']

    con = sqlite3.connect('database/movie_booking.db')
    cur = con.cursor()
    try:
        cur.execute('''
            INSERT INTO movies (movie_id, movie_name, release_date, director, cast, budget, duration, rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (movie_id, movie_name, release_date, director, cast, budget, duration, rating))
        con.commit()
        flash('Movie added successfully.')
    except sqlite3.IntegrityError:
        flash('Movie ID already exists.')
    con.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/delete_movie/<string:movie_id>', methods=['POST'])
def delete_movie(movie_id):
    if 'username' not in session or not session.get('is_admin', False):
        flash('You do not have permission to access this page.')
        return redirect(url_for('home'))

    con = sqlite3.connect('database/movie_booking.db')
    cur = con.cursor()
    cur.execute('DELETE FROM movies WHERE movie_id = ?', (movie_id,))
    con.commit()
    con.close()
    flash('Movie deleted successfully.')
    return redirect(url_for('admin_dashboard'))

@app.route('/update_movie', methods=['POST'])
def update_movie():
    if 'username' not in session or not session.get('is_admin', False):
        flash('You do not have permission to access this page.')
        return redirect(url_for('home'))

    movie_id = request.form['movie_id']
    movie_name = request.form.get('movie_name')
    release_date = request.form.get('release_date')
    director = request.form.get('director')
    cast = request.form.get('cast')
    budget = request.form.get('budget')
    duration = request.form.get('duration')
    rating = request.form.get('rating')

    updates = []
    if movie_name:
        updates.append(f"movie_name = '{movie_name}'")
    if release_date:
        updates.append(f"release_date = '{release_date}'")
    if director:
        updates.append(f"director = '{director}'")
    if cast:
        updates.append(f"cast = '{cast}'")
    if budget:
        updates.append(f"budget = '{budget}'")
    if duration:
        updates.append(f"duration = '{duration}'")
    if rating:
        updates.append(f"rating = '{rating}'")

    if updates:
        update_statement = ', '.join(updates)
        con = sqlite3.connect('database/movie_booking.db')
        cur = con.cursor()
        cur.execute(f'UPDATE movies SET {update_statement} WHERE movie_id = ?', (movie_id,))
        con.commit()
        con.close()
        flash('Movie updated successfully.')

    return redirect(url_for('admin_dashboard'))
@app.route('/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    if 'is_admin' in session and session['is_admin']:
        conn = get_db_connection()
        conn.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
        conn.commit()
        conn.close()
        flash('Booking deleted successfully.')
    else:
        flash('Access denied: Admins only.', 'danger')
    return redirect(url_for('admin_dashboard'))


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'is_admin' in session and session['is_admin']:
        conn = get_db_connection()
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        flash('User deleted successfully.', 'success')
    else:
        flash('Access denied: Admins only.', 'danger')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

