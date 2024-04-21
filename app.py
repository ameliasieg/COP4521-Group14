from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3

app = Flask(__name__, static_folder='static')
app.secret_key = '12345'

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Global variable to store generated books
stored_books = {}

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
        cur.execute("SELECT Title FROM Books WHERE Genre=? ORDER BY RANDOM() LIMIT 1", (genre,))
        book = cur.fetchone()
        conn.close()
        return book[0] if book else None
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

@app.route('/role', methods=['POST'])
def role():
    selected_role = request.form.get('role')
    if selected_role == 'admin':
        return redirect(url_for('login_page'))
    if selected_role == 'user':
        return redirect(url_for('home', role='user'))  # Pass role to home.html
    if selected_role == 'moderator':
        return redirect(url_for('home', role='moderator'))
    return redirect(url_for('home', role=selected_role))

@app.route('/home')
def home():
    role = request.args.get('role', 'user')
    global stored_books
    if not stored_books:
        genres = ['Fantasy', 'Non-Fiction', 'Thriller/Mystery', 'Romance']
        stored_books = {genre: get_random_books_by_genre(genre) for genre in genres}
    return render_template('home.html', books=stored_books, role=role)

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

@app.route('/reviews/<genre>')
def reviews(genre):
    conn = sqlite3.connect('socialReads.db')
    cur = conn.cursor()
    cur.execute("SELECT review, rating FROM Reviews WHERE genre=?", (genre,))
    reviews = cur.fetchall()
    average_rating = sum(review[1] for review in reviews) / len(reviews) if reviews else 0
    conn.close()
    return render_template('reviews.html', genre=genre, reviews=reviews, average_rating=average_rating)

@app.route('/clear_reviews', methods=['POST'])
@login_required
def clear_reviews():
    conn = sqlite3.connect('socialReads.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM Reviews")
    conn.commit()
    conn.close()
    return redirect(url_for('admin_page'))

@app.route('/delete_review/<genre>', methods=['POST'])
@login_required
def delete_review(genre):
    review_text = request.form['review_text']
    conn = sqlite3.connect('socialReads.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM Reviews WHERE genre=? AND review=?", (genre, review_text))
    conn.commit()
    conn.close()
    return redirect(url_for('reviews', genre=genre))

@app.route('/images/<filename>')
def send_image(filename):
    return send_from_directory("static/images", filename)

if __name__ == '__main__':
    app.run(debug=True)
