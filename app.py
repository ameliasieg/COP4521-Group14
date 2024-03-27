from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random

app = Flask(__name__)

def get_random_book_by_genre(genre):
    conn = sqlite3.connect('socialReads.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM Books WHERE Genre=? ORDER BY RANDOM()", (genre,))
    book = cur.fetchone()
    conn.close()
    return book

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/role', methods=['POST'])
def role():
    role = request.form.get('role')
    if role == 'user':
        return redirect(url_for('genres'))
    if role == 'admin':
        return redirect(url_for('genres'))
    if role == 'moderator':
        return redirect(url_for('genres'))
    return redirect(url_for('home'))

@app.route('/genres')
def genres():
    genres = ['Fantasy', 'NonFiction', 'Mystery', 'Romance']  
    books = {genre: get_random_book_by_genre(genre) for genre in genres}
    return render_template('genres.html', books=books)

@app.route('/chat/<genre>')
def chat(genre):
    return render_template('chat.html', genre=genre)

if __name__ == '__main__':
    app.run(debug=True)
