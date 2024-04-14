from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Connect to SQLite database
conn = sqlite3.connect('site.db')
cursor = conn.cursor()

# Create reservations table if it doesn't exist
create_table_query = '''
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    rooms INTEGER NOT NULL,
    adults INTEGER NOT NULL,
    children INTEGER NOT NULL
);
'''
cursor.execute(create_table_query)

# Commit changes and close connection
conn.commit()
conn.close()

# Routes
@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/submit', methods=['POST'])
def submit():
    check_in = request.form['check_in']
    check_out = request.form['check_out']
    rooms = request.form['rooms']
    adults = request.form['adults']
    children = request.form['children']

    # Connect to SQLite database
    conn = sqlite3.connect('site.db')
    cursor = conn.cursor()

    # Insert new reservation into the database
    insert_query = '''
    INSERT INTO reservations ( check_in, check_out, rooms, adults, children)
    VALUES (?, ?, ?, ?, ?)
    '''
    cursor.execute(insert_query, ( check_in, check_out, rooms, adults, children))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    return "Form submitted successfully!"

if __name__ == '__main__':
    app.run(debug=True)
