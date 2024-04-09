# app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

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

@app.route('/reviews/<genre>')
def reviews(genre):
    return render_template('reviews.html', genre=genre)

if __name__ == '__main__':
    app.run(debug=True)