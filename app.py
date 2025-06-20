from flask import Flask, render_template, request, redirect, session, url_for
from bson.objectid import ObjectId
from utils.mongo import users_col, admins_col, bookings_col
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ---- INDEX ----
@app.route('/')
def index():
    return render_template('index.html')

# ---- USER REGISTER ----
@app.route('/user_register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users_col.find_one({'username': username}):
            return "User already exists"
        users_col.insert_one({'username': username, 'password': password})
        return redirect('/user_login')
    return render_template('user_register.html')

# ---- USER LOGIN ----
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_col.find_one({'username': username, 'password': password})
        if user:
            session['user_id'] = str(user['_id'])
            session['username'] = username
            return redirect('/dashboard')
        return "Invalid credentials"
    return render_template('user_login.html')

# ---- USER DASHBOARD ----
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/user_login')
    bookings = list(bookings_col.find({'user_id': session['user_id']}))
    return render_template('dashboard.html', bookings=bookings)

# ---- BOOK SERVICE ----
@app.route('/book', methods=['GET', 'POST'])
def book():
    if 'user_id' not in session:
        return redirect('/user_login')
    if request.method == 'POST':
        service = request.form['service']
        date = request.form['date']
        time = request.form['time']
        bookings_col.insert_one({
            'user_id': session['user_id'],
            'username': session['username'],
            'service': service,
            'date': date,
            'time': time,
            'accepted': False
        })
        return redirect('/dashboard')
    return render_template('booking.html')

# ---- UPDATE BOOKING ----
@app.route('/update_booking/<id>', methods=['POST'])
def update_booking(id):
    if 'user_id' not in session:
        return redirect('/user_login')
    booking = bookings_col.find_one({'_id': ObjectId(id)})
    if booking and not booking['accepted']:
        new_date = request.form['date']
        new_time = request.form['time']
        bookings_col.update_one(
            {'_id': ObjectId(id)},
            {'$set': {'date': new_date, 'time': new_time}}
        )
    return redirect('/dashboard')

# ---- ADMIN LOGIN ----
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = admins_col.find_one({'username': username, 'password': password})
        if admin:
            session['admin'] = True
            return redirect('/admin_dashboard')
        return "Invalid admin credentials"
    return render_template('admin_login.html')

# ---- ADMIN DASHBOARD ----
@app.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/admin_login')
    bookings = list(bookings_col.find())
    return render_template('admin_dashboard.html', bookings=bookings)

# ---- ACCEPT BOOKING ----
@app.route('/accept/<id>', methods=['POST'])
def accept(id):
    if not session.get('admin'):
        return redirect('/admin_login')
    bookings_col.update_one(
        {'_id': ObjectId(id)},
        {'$set': {'accepted': True}}
    )
    return redirect('/admin_dashboard')

# ---- LOGOUT ----
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---- Run App ----
if __name__ == '__main__':
    app.run(debug=True)
