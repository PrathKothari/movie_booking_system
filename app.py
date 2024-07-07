from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

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
            password TEXT,
            is_admin INTEGER
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id TEXT UNIQUE,
            movie_name TEXT,
            release_date TEXT,
            director TEXT,
            cast TEXT,
            budget TEXT,
            duration TEXT,
            rating TEXT
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

    # Insert sample movies
    movies = [
        ("001", "Dilwale Dulhania Le Jayenge", "1995", "Aditya Chopra", "Shah Rukh Khan, Kajol", "4 Crores", "3", "4.5"),
        ("002", "Kabhi Khushi Kabhie Gham", "2001", "Karan Johar", "Shah Rukh Khan, Amitabh Bachchan", "60 Crores", "3.5", "4.0"),
        ("003", "3 Idiots", "2009", "Rajkumar Hirani", "Aamir Khan, Kareena Kapoor", "50 Crores", "2.5", "4.5"),
        ("004", "Zindagi Na Milegi Dobara", "2011", "Zoya Akhtar", "Hrithik Roshan, Farhan Akhtar", "75 Crores", "2.5", "4.0"),
        ("005", "Bajrangi Bhaijaan", "2015", "Kabir Khan", "Salman Khan, Harshaali Malhotra", "100 Crores", "2.0", "4.5"),
        ("006", "Queen", "2013", "Vikas Bahl", "Kangana Ranaut, Rajkummar Rao", "15 Crores", "2.5", "4.0"),
        ("007", "Piku", "2015", "Shoojit Sircar", "Amitabh Bachchan, Deepika Padukone", "40 Crores", "2.0", "4.2"),
        ("008", "Andhadhun", "2018", "Sriram Raghavan", "Ayushmann Khurrana, Tabu", "30 Crores", "2.5", "4.5"),
        ("009", "Barfi!", "2012", "Anurag Basu", "Ranbir Kapoor, Priyanka Chopra", "40 Crores", "2.5", "4.3"),
        ("010", "Tumbbad", "2018", "Rahi Anil Barve", "Sohum Shah, Jyoti Malshe", "10 Crores", "2.0", "4.6"),
        ("011", "Dangal", "2016", "Nitesh Tiwari", "Aamir Khan, Sakshi Tanwar", "90 Crores", "2.5", "4.7"),
        ("012", "Batla House", "2019", "Nikkhil Advani", "John Abraham, Mrunal Thakur", "30 Crores", "2.5", "4.0"),
        ("013", "Kal Ho Naa Ho", "2003", "Nikhil Advani", "Shah Rukh Khan, Preity Zinta", "55 Crores", "2.5", "4.5"),
        ("014", "Dhoom 2", "2006", "Sanjay Gadhvi", "Hrithik Roshan, Aishwarya Rai", "85 Crores", "2.5", "4.0"),
        ("015", "Gully Boy", "2019", "Zoya Akhtar", "Ranveer Singh, Alia Bhatt", "40 Crores", "2.0", "4.4"),
        ("016", "Aashiqui 2", "2013", "Mohit Suri", "Aditya Roy Kapur, Shraddha Kapoor", "20 Crores", "2.5", "4.3"),
        ("017", "Sultan", "2016", "Ali Abbas Zafar", "Salman Khan, Anushka Sharma", "100 Crores", "2.5", "4.0"),
        ("018", "Dil Chahta Hai", "2001", "Farhan Akhtar", "Aamir Khan, Saif Ali Khan", "60 Crores", "3.0", "4.5"),
        ("019", "Chennai Express", "2013", "Rohit Shetty", "Shah Rukh Khan, Deepika Padukone", "100 Crores", "2.5", "4.1"),
        ("020", "Wake Up Sid", "2009", "Ayan Mukerji", "Ranbir Kapoor, Konkona Sen Sharma", "15 Crores", "2.5", "4.0"),
        ("021", "Jab We Met", "2007", "Imtiaz Ali", "Shahid Kapoor, Kareena Kapoor", "25 Crores", "2.5", "4.2"),
        ("022", "Mera Naam Joker", "1970", "Raj Kapoor", "Raj Kapoor, Simi Garewal", "20 Crores", "3.0", "3.5"),
        ("023", "Sholay", "1975", "Ramesh Sippy", "Amitabh Bachchan, Dharmendra", "15 Crores", "3.0", "4.7"),
        ("024", "Kuch Kuch Hota Hai", "1998", "Karan Johar", "Shah Rukh Khan, Kajol", "40 Crores", "2.5", "4.5"),
        ("025", "Taal", "1999", "Subhash Ghai", "Anil Kapoor, Aishwarya Rai", "30 Crores", "3.0", "4.1"),
        ("026", "Rang De Basanti", "2006", "Rakeysh Omprakash Mehra", "Aamir Khan, Siddharth", "25 Crores", "2.5", "4.4"),
        ("027", "Lagaan", "2001", "Ashutosh Gowariker", "Aamir Khan, Gracy Singh", "50 Crores", "2.5", "4.5"),
        ("028", "Koi... Mil Gaya", "2003", "Rakesh Roshan", "Hrithik Roshan, Preity Zinta", "35 Crores", "2.5", "4.0"),
        ("029", "Chakde! India", "2007", "Shimit Amin", "Shah Rukh Khan, Vidya Malvade", "30 Crores", "2.5", "4.5"),
        ("030", "Mughal-e-Azam", "1960", "K. Asif", "Dilip Kumar, Madhubala", "10 Crores", "3.0", "4.6"),
        ("031", "Pyaasa", "1957", "Guru Dutt", "Guru Dutt, Waheeda Rehman", "5 Crores", "3.0", "4.7"),
        ("032", "Devdas", "2002", "Sanjay Leela Bhansali", "Shah Rukh Khan, Aishwarya Rai", "55 Crores", "3.0", "4.3"),
        ("033", "Aashiqui", "1990", "Mahesh Bhatt", "Anu Aggarwal, Rahul Roy", "7 Crores", "3.0", "4.2"),
        ("034", "Bobby", "1973", "Raj Kapoor", "Rishi Kapoor, Dimple Kapadia", "10 Crores", "3.0", "4.0"),
        ("035", "Jab Tak Hai Jaan", "2012", "Yash Chopra", "Shah Rukh Khan, Katrina Kaif", "70 Crores", "2.5", "4.1")
    ]

    cur.executemany('''
        INSERT OR IGNORE INTO movies (movie_id, movie_name, release_date, director, cast, budget, duration, rating)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
    db_path = 'C:/Users/PRATHAM/PycharmProjects/movie-booking/database/movie_booking.db'
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            flash('Login successful!', 'success')
            if user['is_admin']:
                return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard if admin
            else:
                return redirect(url_for('booking_page'))  # Redirect to booking page if not admin
        else:
            flash('Invalid username or password.', 'danger')

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

    con = sqlite3.connect('database/movie_booking.db')
    cur = con.cursor()
    cur.execute('SELECT id FROM users WHERE username = ?', (session['username'],))
    user_id = cur.fetchone()[0]

    try:
        cur.execute('INSERT INTO bookings (user_id, movie_id) VALUES (?, ?)', (user_id, movie_id))
        con.commit()
    except sqlite3.IntegrityError:
        flash('You have already booked this movie.')

    cur.execute('SELECT * FROM movies WHERE movie_id = ?', (movie_id,))
    movie = cur.fetchone()
    con.close()

    return render_template('confirm.html', movie=movie)

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
            try:
                cur.execute('''
                    INSERT INTO movies (movie_id, movie_name, release_date, director, cast, budget, duration, rating)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (movie_id, movie_name, release_date, director, cast, budget, duration, rating))
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

            if updates:
                update_statement = ', '.join(updates)
                update_values = [val for val in [movie_name, release_date, director, cast, budget, duration, rating] if val]
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
        flash('Booking deleted successfully.', 'success')
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

