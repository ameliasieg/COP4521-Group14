import sqlite3

conn = sqlite3.connect('socialReads.db')
print ('Opened socialReads database successfully')

conn.execute('CREATE TABLE IF NOT EXISTS Books (Title TEXT, Genre TEXT, AuthorFirst TEXT, AuthorLast TEXT, ISBN INTEGER PRIMARY KEY)')
print('Created Books table')

conn.execute('DROP TABLE IF EXISTS Reviews')
conn.execute('CREATE TABLE Reviews (genre TEXT, review TEXT, rating INTEGER)')

print('Created Reviews table ')
conn.close()