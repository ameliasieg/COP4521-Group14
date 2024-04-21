from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3

import pyjokes


app = Flask(__name__, static_folder='static')
app.secret_key = '12345'

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Global variable to store generated books
stored_books = {}
joke = ""

# User store
users = {'admin': {'password': 'password'}}

# Flask-Login setup
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Decorator provided by Flask-Login to load a user
@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

def get_random_books_by_genre(genre):
    try:
        conn = sqlite3.connect('socialReads.db')
        cur = conn.cursor()
        cur.execute("SELECT Title, ISBN, AuthorFirst, AuthorLast FROM Books WHERE Genre=? ORDER BY RANDOM() LIMIT 1", (genre,))
        books = cur.fetchall()
        conn.close()
        return [{'Title': book[0], 'ISBN': book[1], 'AuthorFirst': book[2], 'AuthorLast': book[3]} for book in books]
        # return book[0] if book is not None else None
    except Exception as e:
        print("Error fetching random book:", e)
        return None


@app.route('/')
def start():
    return render_template('start.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user['password'] == password:
            user_obj = User(username)
            login_user(user_obj)
            return redirect(url_for('admin_page'))
        return 'Invalid username or password'
    return render_template('login.html')

@app.route('/login')
def login_page():
    return render_template('login.html')


# Function to display the front page

@app.route('/role', methods=['POST'])
def role():
    selected_role = request.form.get('role')
    if selected_role == 'admin':
        return redirect(url_for('login_page'))
    if selected_role == 'user':
        return redirect(url_for('home', role='user'))  # Pass role to home.html
    if selected_role == 'moderator':
        return redirect(url_for('home', role='moderator'))



@app.route('/home')
def home():
    role = request.args.get('role', 'user')  # Get the role from the query parameters
    print(role)
    global stored_books
    global joke
    if not stored_books:  # If stored_books is empty, generate new books
        genres = ['Fantasy', 'Non-Fiction', 'Thriller-Mystery', 'Romance']  

        stored_books = {genre: get_random_books_by_genre(genre) for genre in genres}
        joke = pyjokes.get_joke()
    return render_template('home.html', books=stored_books, role=role, joke=joke)


@app.route('/admin')
@login_required
def admin_page():
    global stored_books
    if not stored_books:
        genres = ['Fantasy', 'Non-Fiction', 'Thriller/Mystery', 'Romance']
        stored_books = {genre: get_random_books_by_genre(genre) for genre in genres}
    return render_template('admin.html', books=stored_books)

@app.route('/regenerate', methods=['POST'])
@login_required
def regenerate_books():
    genres = ['Fantasy', 'Non-Fiction', 'Thriller/Mystery', 'Romance']
    global stored_books
    stored_books = {genre: get_random_books_by_genre(genre) for genre in genres}
    return render_template('home.html', books=stored_books, role='admin')

@app.route('/submit_review/<genre>', methods=['POST'])
@login_required
def submit_review(genre):
    review_text = request.form['review']
    review_rating = request.form['rating']
    conn = sqlite3.connect('socialReads.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO Reviews (genre, review, rating) VALUES (?, ?, ?)", (genre, review_text, int(review_rating)))
    conn.commit()
    conn.close()
    return redirect(url_for('reviews', genre=genre))

@app.route('/regenerate', methods=['POST'])
def regenerate_books():
    selected_role = request.form.get('role')
    genres = ['Fantasy', 'Non-Fiction', 'Thriller-Mystery', 'Romance']
    # Delete all reviews
    conn = sqlite3.connect('socialReads.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM Reviews")
    conn.commit()
    conn.close()
    # Generate new books
    global stored_books
    global joke
    stored_books = {genre: get_random_books_by_genre(genre) for genre in genres}
    print(stored_books)
    joke = pyjokes.get_joke()
    return render_template('admin.html', books=stored_books, role=selected_role, joke=joke)

# Function to display the form for submitting a review
@app.route('/submit_review/<genre>', methods=['POST', 'GET'])
def submit_review(genre):
    if request.method == 'POST':
        review_text = request.form['review']
        review_rating = request.form['rating']
        # Save the review to the database
        conn = sqlite3.connect('socialReads.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO Reviews (genre, review, rating) VALUES (?, ?, ?)", (genre, review_text, int(review_rating)))
        conn.commit()
        conn.close()
        role = request.args.get('role')
        return redirect(url_for('reviews', genre=genre, role=role))


@app.route('/reviews/<genre>')
def reviews(genre):
    role = request.args.get('role')  # Get the role from the query parameters
    conn = sqlite3.connect('socialReads.db')
    cur = conn.cursor()
    cur.execute("SELECT review, rating FROM Reviews WHERE genre=?", (genre,))
    reviews = cur.fetchall()
    #calculating average
    if reviews is not None:
        if len(reviews) == 0:
            average_rating = 0
        else:
            average_rating = sum (review[1] for review in reviews if not None) / len(reviews)
    else:
        average_rating = 0
    conn.close()
    return render_template('reviews.html', genre=genre, reviews=reviews, average_rating=average_rating, role=role)

@app.route('/admin')
def admin_page():
    global stored_books
    global joke
    if not stored_books:  # If stored_books is empty, generate new books
        genres = ['Fantasy', 'Non-Fiction', 'Thriller-Mystery', 'Romance']  
        stored_books = {genre: get_random_books_by_genre(genre) for genre in genres}
    joke = pyjokes.get_joke()
    return render_template('admin.html', joke=joke, books=stored_books)
    
# Function for admin to clear the reviews table
@app.route('/clear_reviews', methods=['POST', 'GET'])
def clear_reviews():
    if request.method == 'POST':
        conn = sqlite3.connect('socialReads.db')
        cur = conn.cursor()
        # Clear the reviews table
        cur.execute("DELETE FROM Reviews")
        conn.commit()
        conn.close()
        return redirect(url_for('admin_page'))
    
@app.route('/delete_review/<genre>', methods=['POST'])
def delete_review(genre):
    if request.method == 'POST':
        review_text = request.form['review_text']
        # Delete the review from the database
        conn = sqlite3.connect('socialReads.db')
        cur = conn.cursor()
        cur.execute("DELETE FROM Reviews WHERE genre=? AND review=?", (genre, review_text))
        conn.commit()
        conn.close()
        role = request.args.get('role')
        return redirect(url_for('reviews', genre=genre, role=role))


@app.route('/images/<filename>')
def send_image(filename):
    return send_from_directory("static/images", filename)


if __name__ == '__main__':
    app.run(debug=True)
