import sqlite3

conn = sqlite3.connect('socialReads.db')
print ('Opened socialReads database successfully')

conn.execute('CREATE TABLE Books (Title TEXT, Genre TEXT, AuthorFirst TEXT, AuthorLast TEXT, ISBN INTEGER PRIMARY KEY)')
print('Created Books table')

conn.execute('CREATE TABLE Reviews (title TEXT, genre TEXT, review TEXT)')
print('Created Reviews table ')
conn.close()