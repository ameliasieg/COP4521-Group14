from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_random_book_by_genre(genre):
    conn = sqlite3.connect('socialReads.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM Books WHERE Genre=? ORDER BY RANDOM()", (genre,))
    book = cur.fetchone()
    conn.close()
    return book

@app.route('/')
def start():
    return render_template('start.html')

@app.route('/role', methods=['POST'])
def role():
    # Since all roles redirect to the same page, no need to check the role
    return redirect(url_for('home'))

@app.route('/home')
def home():
    genres = ['Fantasy', 'NonFiction', 'Mystery', 'Romance']  
    books = {genre: get_random_book_by_genre(genre) for genre in genres}
    return render_template('home.html', books=books)

@app.route('/reviews/<genre>')
def reviews(genre):
    return render_template('reviews.html', genre=genre)

if __name__ == '__main__':
    app.run(debug=True)
    