from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)
app.config['DATABASE'] = 'site.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row  # Access rows as dictionaries
    return db

def close_db(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.teardown_appcontext
def teardown_db(e=None):
    close_db()

house_info = {
    1: {
        'rooms': 3,
        'adults': 2,
        'children': 1
    },
    2: {
        'rooms': 4,
        'adults': 3,
        'children': 2
    },
    3: {
        'rooms': 2,
        'adults': 1,
        'children': 0
    }
}


@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/submit', methods=['POST'])
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
        if booking_count == 0:
            available_results.append(f"House {house_id} is available for your dates with {house_info[house_id]['rooms']} rooms.")

    if available_results:
        return render_template('available_houses.html', available_results=available_results)
    else:
        return "Sorry, no houses are available for your requested dates or rooms."

@app.route('/book', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True)
