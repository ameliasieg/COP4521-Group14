# app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Function to get a random book from the database by genre
def get_random_book_by_genre(genre):
    conn = sqlite3.connect('socialReads.db')
    cur = conn.cursor()
    cur.execute("SELECT Title FROM Books WHERE Genre=? ORDER BY RANDOM() LIMIT 1", (genre,))
    book = cur.fetchone()
    conn.close()
    return book[0] if book else None

@app.route('/')
def start():
    return render_template('start.html')

# Function to display the front page
@app.route('/role', methods=['POST'])
def role():
    selected_role = request.form.get('role')
    if selected_role == 'admin':
        genres = ['Fantasy', 'Non-Fiction', 'Thriller/Mystery', 'Romance']  
        books = {genre: get_random_books_by_genre(genre) for genre in genres}
        return render_template('home.html', books=books, role=selected_role)  # Pass role to home.html
    else:
        return redirect(url_for('home'))

@app.route('/home')
def home():
    role = request.args.get('role', 'user')  # Get the role from the query parameters
    genres = ['Fantasy', 'Non-Fiction', 'Thriller/Mystery', 'Romance']  
    books = {genre: get_random_books_by_genre(genre) for genre in genres}
    return render_template('home.html', books=books, role=role)

@app.route('/regenerate', methods=['POST'])
def regenerate_books():
    if request.method == 'POST':
        role = request.form.get('role')
        if role == 'admin':
            genres = ['Fantasy', 'Non-Fiction', 'Thriller/Mystery', 'Romance']  
            books = {genre: get_random_books_by_genre(genre) for genre in genres}
            return render_template('home.html', books=books, role=role)
    return redirect(url_for('home'))

# Function to display the form for submitting a review
@app.route('/submit_review/<genre>', methods=['POST'])
def submit_review(genre):
    review_text = request.form['review']
    # Save the review to the database
    conn = sqlite3.connect('socialReads.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO Reviews (genre, review) VALUES (?, ?)", (genre, review_text))
    conn.commit()
    conn.close()
    return redirect(url_for('reviews', genre=genre))



# Function to display reviews for a specific genre
@app.route('/reviews/<genre>')
def reviews(genre):
    conn = sqlite3.connect('socialReads.db')
    cur = conn.cursor()
    cur.execute("SELECT review FROM Reviews WHERE genre=?", (genre,))
    reviews = cur.fetchall()
    conn.close()
    return render_template('reviews.html', genre=genre, reviews=reviews)


@app.route('/admin')
def admin_page():
    return render_template('admin.html')

# Function for admin to clear the reviews table
@app.route('/clear_reviews', methods=['POST'])
def clear_reviews():
    conn = sqlite3.connect('socialReads.db')
    cur = conn.cursor()
    # Clear the reviews table
    cur.execute("DELETE FROM Reviews")
    conn.commit()
    conn.close()
    return redirect(url_for('admin_page'))


if __name__ == '__main__':
    app.run(debug=True)
