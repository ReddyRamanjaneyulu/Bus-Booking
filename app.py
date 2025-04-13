from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect
import pymysql
from datetime import datetime, date

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-strong-secret-key-here'
csrf = CSRFProtect(app)

# MySQL connection configuration
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='password',
        database='bus_booking',
        cursorclass=pymysql.cursors.DictCursor
    )

# ---------------------------
# User Routes
# ---------------------------

@app.route('/')
def home():
    return render_template('index.html', min_date=date.today().isoformat())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                query = "SELECT * FROM users WHERE email = %s AND password = %s"
                cursor.execute(query, (email, password))
                user = cursor.fetchone()
                
                if user:
                    session['user_id'] = user['id']
                    session['user_name'] = user['name']
                    session['role'] = user['role']

                    flash('Login successful!', 'success')
                    
                    if user['role'] == 'admin':
                        return redirect(url_for('admin_panel'))
                    else:
                        return redirect(url_for('home'))
                else:
                    flash('Invalid credentials', 'error')
        finally:
            connection.close()
    return render_template('login.html')

@app.route('/search', methods=['GET'])
def search():
    return render_template('search.html')

@app.route('/search_buses', methods=['GET', 'POST'])
def search_buses():
    buses = []

    if request.method == 'POST':
        departure = request.form.get('departure')
        destination = request.form.get('destination')

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT buses.*, routes.source, routes.destination
                    FROM buses
                    JOIN routes ON buses.route_id = routes.id
                    WHERE LOWER(routes.source) = LOWER(%s) AND LOWER(routes.destination) = LOWER(%s)
                """, (departure, destination))
                buses = cursor.fetchall()
        finally:
            connection.close()

    return render_template('search_results.html', buses=buses)

@app.route('/admin_panel')
def admin_panel():
    if session.get('role') != 'admin':
        flash('Access denied: Admins only.', 'error')
        return redirect(url_for('home'))

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()

            cursor.execute("SELECT buses.*, routes.source, routes.destination FROM buses JOIN routes ON buses.route_id = routes.id")
            buses = cursor.fetchall()

            cursor.execute("SELECT * FROM routes")
            routes = cursor.fetchall()

            cursor.execute("""
                SELECT bookings.*, users.name AS user_name, buses.name AS bus_name 
                FROM bookings
                JOIN users ON bookings.user_id = users.id
                JOIN buses ON bookings.bus_id = buses.id
            """)
            bookings = cursor.fetchall()

        return render_template('admin_panel.html', users=users, buses=buses, bookings=bookings, routes=routes)
    finally:
        connection.close()

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/add_bus', methods=['POST'])
def add_bus():
    if session.get('role') != 'admin':
        flash('Access denied: Admins only.', 'error')
        return redirect(url_for('home'))

    bus_name = request.form['bus_name']
    route_id = int(request.form['route_id'])
    available_seats = int(request.form['available_seats'])

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM buses WHERE name = %s AND route_id = %s", (bus_name, route_id))
            existing_bus = cursor.fetchone()
            if existing_bus:
                flash('Bus with this name and route already exists.', 'warning')
            else:
                cursor.execute("""
                    INSERT INTO buses (name, route_id, available_seats)
                    VALUES (%s, %s, %s)
                """, (bus_name, route_id, available_seats))
                connection.commit()

                flash('Bus added successfully!', 'success')
    finally:
        connection.close()

    return redirect(url_for('admin_panel'))

@app.route('/edit_bus/<int:bus_id>', methods=['GET', 'POST'])
def edit_bus(bus_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Fetch bus details by ID
            cursor.execute("SELECT * FROM buses WHERE id = %s", (bus_id,))
            bus = cursor.fetchone()

            if request.method == 'POST':
                # Handle form submission for editing bus
                bus_name = request.form['bus_name']
                route = request.form['route']
                available_seats = request.form['available_seats']

                # Update bus details in the database
                cursor.execute("""
                    UPDATE buses
                    SET name = %s, route = %s, available_seats = %s
                    WHERE id = %s
                """, (bus_name, route, available_seats, bus_id))
                connection.commit()

                flash('Bus details updated successfully!', 'success')
                return redirect(url_for('admin_panel'))

            return render_template('edit_bus.html', bus=bus)

    finally:
        connection.close()

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        flash('User deleted successfully.', 'info')
    finally:
        connection.close()
    return redirect(url_for('admin_panel'))

@app.route('/delete_bus/<int:bus_id>')
def delete_bus(bus_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM buses WHERE id = %s", (bus_id,))
        connection.commit()
        flash('Bus deleted successfully.', 'info')
    finally:
        connection.close()
    return redirect(url_for('admin_panel'))

# ---------------------------
# Booking Routes
# ---------------------------

@app.route('/book_bus/<int:bus_id>', methods=['GET', 'POST'])
def book_bus(bus_id):
    if 'user_id' not in session:
        flash('You must be logged in to make a booking.', 'warning')
        return redirect(url_for('login'))

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT buses.*, routes.source, routes.destination
                FROM buses
                JOIN routes ON buses.route_id = routes.id
                WHERE buses.id = %s
            """, (bus_id,))
            bus = cursor.fetchone()

            cursor.execute("""
                SELECT seat_number FROM bookings WHERE bus_id = %s
            """, (bus_id,))
            booked_seats = [row['seat_number'] for row in cursor.fetchall()]

            if not bus:
                flash('Bus not found.', 'error')
                return redirect(url_for('home'))

            if request.method == 'POST':
                seat_number = request.form.get('seat_number')
                user_id = session['user_id']
                booking_date = datetime.now()

                # Prevent double booking of a seat
                if seat_number in booked_seats:
                    flash('This seat has already been booked. Please choose another one.', 'warning')
                    return render_template('select_seat.html', bus=bus, booked_seats=booked_seats)

                # Insert booking into the database
                cursor.execute("""
                    INSERT INTO bookings (user_id, bus_id, seat_number, booking_date)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, bus_id, seat_number, booking_date))

                # Decrease the available seats
                cursor.execute("""
                    UPDATE buses SET available_seats = available_seats - 1 WHERE id = %s
                """, (bus_id,))
                connection.commit()

                flash(f'Seat {seat_number} booked successfully!', 'success')
                return redirect(url_for('home'))

    finally:
        connection.close()

    return render_template('select_seat.html', bus=bus, booked_seats=booked_seats)

@app.route('/booking_history')
def booking_history():
    if 'user_id' not in session:
        flash('You must be logged in to view your booking history.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Get all bookings of the logged-in user
            cursor.execute("""
                SELECT bookings.*, buses.name AS bus_name, routes.source, routes.destination
                FROM bookings
                JOIN buses ON bookings.bus_id = buses.id
                JOIN routes ON buses.route_id = routes.id
                WHERE bookings.user_id = %s
                ORDER BY bookings.booking_date DESC
            """, (user_id,))
            bookings = cursor.fetchall()

        return render_template('booking_history.html', bookings=bookings)
    finally:
        connection.close()

@app.route('/add_route', methods=['POST'])
def add_route():
    if session.get('role') != 'admin':
        flash('Access denied: Admins only.', 'error')
        return redirect(url_for('home'))

    source = request.form['source']
    destination = request.form['destination']

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Check if the route already exists
            cursor.execute("SELECT * FROM routes WHERE source = %s AND destination = %s", (source, destination))
            existing_route = cursor.fetchone()
            if existing_route:
                flash('Route already exists.', 'warning')
            else:
                cursor.execute("INSERT INTO routes (source, destination) VALUES (%s, %s)", (source, destination))
                connection.commit()
                flash('Route added successfully!', 'success')
    finally:
        connection.close()

    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True)
