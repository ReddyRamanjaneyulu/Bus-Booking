# Bus Ticket Booking System

A bus ticket booking system built using Flask, MySQL, and HTML templates. The system allows users to search for buses, select available seats, make bookings, and view their booking history. It also provides an admin panel for managing buses, users, and bookings.

## Features

- **User Authentication**: Users can log in and log out.
- **Search for Buses**: Users can search for buses based on departure and destination.
- **Seat Selection**: Users can select available seats for booking.
- **Booking Management**: Users can book a seat, and the system prevents double booking of seats.
- **Booking History**: Users can view their past bookings.
- **Admin Panel**: Admins can add, edit, and delete buses and routes, manage users, and view bookings.

## Installation

Follow the steps below to set up the project on your local machine.

### Prerequisites

- Python 3.x
- MySQL
- Flask
- Flask-WTF (for CSRF protection)
- pymysql

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/ReddyRamanjaneyulu/bus-booking.git
```

### 2. Install Dependencies
Navigate to the project folder and install the required Python packages:
```bash
cd bus-ticket-booking-system
pip install -r requirements.txt
```

### 3. Set Up MySQL Database
Create a MySQL database named bus_booking and run the following SQL commands to set up the necessary tables:
```bash
CREATE DATABASE bus_booking;

USE bus_booking;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user'
);

CREATE TABLE routes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(100),
    destination VARCHAR(100)
);

CREATE TABLE buses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    route_id INT,
    available_seats INT,
    FOREIGN KEY (route_id) REFERENCES routes(id)
);

CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    bus_id INT,
    seat_number INT,
    booking_date DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (bus_id) REFERENCES buses(id)
);
```

### 4. Update Database Credentials
In the app.py file, update the following MySQL connection configuration with your own credentials:
```bash
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='your-password',
        database='bus_booking',
        cursorclass=pymysql.cursors.DictCursor
    )
```

### 5. Run the Application
To start the Flask application, run the following command:

```bash
python app.py
```
By default, the application will run on http://127.0.0.1:5000.

### 6. Create an Admin Account
You can manually add an admin account in the database through MySQL or create a registration feature to register an admin user. Alternatively, you can log in with a user and use the admin panel once logged in.

### Usage
- Home Page: Displays a search form for users to search for buses.

- Login Page: Users and admins can log in using their credentials.

- Search Page: Allows users to search for buses by departure and destination.

- Select Seat Page: Displays available seats for the selected bus and allows users to book a seat.

- Admin Panel: Admins can manage users, buses, routes, and bookings from the admin panel.

Folder Structure
```bash
bus-booking/
│
├── app.py                  # Main application file
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── base.html           # Base layout template
│   ├── index.html          # Home page
│   ├── login.html          # Login page
│   ├── search.html         # Search for buses page
│   ├── search_results.html # Bus search results page
│   ├── select_seat.html    # Seat selection page
│   ├── booking_history.html # Booking history page
│   └── admin_panel.html    # Admin panel page
└── static/                 # Static files (CSS, images, JS)
```
### Technologies Used
- Flask: Web framework for building the web application.

- MySQL: Database for storing users, buses, routes, and bookings.

- HTML/CSS: Front-end design and layout.

- Flask-WTF: Form handling and CSRF protection.

- pymysql: Python library for interacting with MySQL.

### Contributing
If you want to contribute to the development of this project, feel free to fork the repository, make changes, and create a pull request. Make sure to follow best practices and write clean code.