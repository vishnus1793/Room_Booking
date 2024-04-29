from flask import Flask, render_template, request, g
import sqlite3

application = Flask(__name__)
application.config['DATABASE'] = 'site.db'

# Function to get the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(application.config['DATABASE'])
        db.row_factory = sqlite3.Row  # Access rows as dictionaries
    return db

# Function to close the database connection
def close_db(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Teardown function to close the database connection at the end of the request
@application.teardown_appcontext
def teardown_db(e=None):
    close_db()

# House information dictionary
house_info = {
    1: {
        'rooms': 3,
        'adults': 2,
        'children': 1,
        'description': "NATURAL VIEW",
        'url': "https://saliniyan.github.io/images/maxresdefault.jpg"
    },
    2: {
        'rooms': 4,
        'adults': 3,
        'children': 2,
        'description': "HOTEL NEAR",
        'url': "https://saliniyan.github.io/images/room2.jpeg"
    },
    3: {
        'rooms': 2,
        'adults': 1,
        'children': 0,
        'description': "PARKING LOT",
        'url': "https://articulate-heroes.s3.amazonaws.com/uploads/rte/blknfsca_tu09tpc-a-large-bed-in-a-room%20(1).jpeg"
    }
}

# Function to create necessary tables in the database
def create_tables():
    with application.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY,
                check_in DATE NOT NULL,
                check_out DATE NOT NULL,
                rooms INTEGER NOT NULL,
                adults INTEGER NOT NULL,
                children INTEGER NOT NULL,
                House_NO INTEGER NOT NULL,
                FOREIGN KEY (House_NO) REFERENCES houses(id)
            );
        ''')
        db.commit()

# Route for the index page
@application.route('/')
def index():
    return render_template('index1.html')

# Route for form submission
@application.route('/submit', methods=['POST'])
def submit():
    check_in = request.form['check_in']
    check_out = request.form['check_out']
    rooms_needed = int(request.form['rooms'])

    if not check_in or not check_out or rooms_needed <= 0:
        return "Invalid input. Please fill in all fields correctly."

    db = get_db()
    cursor = db.cursor()

    available_houses = []
    for house_id, info in house_info.items():
        if info['rooms'] >= rooms_needed:
            available_houses.append(house_id)

    available_results = []
    for house_id in available_houses:
        cursor.execute('''
            SELECT COUNT(*) FROM reservations
            WHERE House_NO = ? AND
            (check_in BETWEEN ? AND ? OR check_out BETWEEN ? AND ?);
        ''', (house_id, check_in, check_out, check_in, check_out))
        booking_count = cursor.fetchone()[0]
        if booking_count == 0:  # Indent this block properly
            house_description = house_info[house_id]['description']
            house_url = house_info[house_id]['url']
            available_results.append({
                'house_id': house_id,
                'rooms': house_info[house_id]['rooms'],
                'description': house_description,
                'url': house_url
            })

    if available_results:
        return render_template('available_houses.html', available_results=available_results)
    else:
        return "Sorry, no houses are available for your requested dates or rooms."
# Route for booking
@application.route('/book', methods=['POST'])
def book():
    house_id = request.form['house_id']
    check_in = request.form['check_in']
    check_out = request.form['check_out']

    if not house_id or not check_in or not check_out:
        return "Invalid input. Please fill in all fields correctly."

    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        INSERT INTO reservations (check_in, check_out, rooms, adults, children, House_NO)
        VALUES (?, ?, ?, ?, ?, ?);
    ''', (check_in, check_out, house_info[int(house_id)]['rooms'], house_info[int(house_id)]['adults'], house_info[int(house_id)]['children'], house_id))

    db.commit()

    success_message = "Booking successful! Thank you for choosing us."

    return render_template('success.html', success_message=success_message)

# Main block to run the application
if __name__ == '__main__':
    create_tables()  # Create tables within the application context
    application.run(debug=True)
