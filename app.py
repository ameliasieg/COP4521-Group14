from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random

app = Flask(__name__)

# Global variable to store generated books
stored_books = {}

# Function to get a random book from the database by genre
def get_random_books_by_genre(genre):
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
        return redirect(url_for('admin_page'))
    if selected_role == 'user':
        return redirect(url_for('home'))  # Pass role to home.html
    if selected_role == 'moderator':
        return redirect(url_for('home'))


@app.route('/home')
def home():
    role = request.args.get('role', 'user')  # Get the role from the query parameters
    global stored_books
    if not stored_books:  # If stored_books is empty, generate new books
        genres = ['Fantasy', 'Non-Fiction', 'Thriller/Mystery', 'Romance']  
        stored_books = {genre: get_random_books_by_genre(genre) for genre in genres}
    return render_template('home.html', books=stored_books, role=role)

@app.route('/regenerate', methods=['POST', 'GET'])
def regenerate_books():
    if request.method == 'POST':
        role = request.form.get('role')
        if role == 'admin':
            genres = ['Fantasy', 'Non-Fiction', 'Thriller/Mystery', 'Romance']  
            global stored_books
            stored_books = {genre: get_random_books_by_genre(genre) for genre in genres}
            return render_template('home.html', books=stored_books, role=role)
    return redirect(url_for('home'))

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
        return redirect(url_for('reviews', genre=genre))

# Function to display reviews for a specific genre
@app.route('/reviews/<genre>')
def reviews(genre):
    conn = sqlite3.connect('socialReads.db')
    cur = conn.cursor()
    cur.execute("SELECT review, rating FROM Reviews WHERE genre=?", (genre,))
    reviews = cur.fetchall()
    #calculating average
    if reviews is not None:
        average_rating = sum (review[1] for review in reviews if not None) / len(reviews)
    else:
        average_rating = 0
    conn.close()
    return render_template('reviews.html', genre=genre, reviews=reviews, average_rating=average_rating)

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

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

if __name__ == '__main__':
    app.run(debug=True)
