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


@app.route('/submit_review/<genre>', methods=['POST'])
def submit_review(genre):
    review_text = request.form['review']
    # Connect to your database
    conn = sqlite3.connect('socialReads.db')
    cur = conn.cursor()
    # Insert the new review into the database
    cur.execute("INSERT INTO Reviews (genre, review) VALUES (?, ?)", (genre, review_text))
    conn.commit()
    conn.close()
    # Redirect back to the reviews page for the current genre
    return redirect(url_for('reviews', genre=genre))




@app.route('/reviews/<genre>')
def reviews(genre):
    conn = sqlite3.connect('socialReads.db')
    cur = conn.cursor()
    cur.execute("SELECT review FROM Reviews WHERE genre=?", (genre,))
    reviews = cur.fetchall()
    conn.close()
    return render_template('reviews.html', genre=genre, reviews=reviews)




if __name__ == '__main__':
    app.run(debug=True)


