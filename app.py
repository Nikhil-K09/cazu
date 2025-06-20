from flask import Flask, render_template, request, redirect, session
from bson.objectid import ObjectId
from utils.mongo import users_col, admins_col, bookings_col

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
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        password = request.form['password']
        if users_col.find_one({'username': username}):
            return "User already exists"
        users_col.insert_one({
            'username': username,
            'email': email,
            'phone': phone,
            'address': address,
            'password': password
        })
        return redirect('/user_login')
    return render_template('user_register.html')

# ---- USER LOGIN ----
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']

        # Check for email OR phone
        user = users_col.find_one({
            '$and': [
                {'$or': [{'email': identifier}, {'phone': identifier}]},
                {'password': password}
            ]
        })

        if user:
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            return redirect('/dashboard')
        return "Invalid credentials"

    return render_template('user_login.html')


# ---- USER DASHBOARD ----
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/user_login')
    user = users_col.find_one({'_id': ObjectId(session['user_id'])})
    bookings = list(bookings_col.find({'user_id': session['user_id']}))
    return render_template('dashboard.html', user=user, bookings=bookings)

# ---- EDIT PROFILE ----
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect('/user_login')
    user = users_col.find_one({'_id': ObjectId(session['user_id'])})
    if request.method == 'POST':
        updated_data = {
            'username': request.form['username'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'address': request.form['address'],
            'password': user['password']  # keep existing password
        }
        users_col.update_one({'_id': ObjectId(session['user_id'])}, {'$set': updated_data})
        session['username'] = updated_data['username']
        return redirect('/dashboard')
    return render_template('edit_profile.html', user=user)

# ---- BOOK SERVICE ----
@app.route('/book', methods=['GET', 'POST'])
def book():
    if 'user_id' not in session:
        return redirect('/user_login')
    
    user = users_col.find_one({'_id': ObjectId(session['user_id'])})

    if request.method == 'POST':
        service = request.form['service']
        date = request.form['date']
        time = request.form['time']

        # Use user's stored address or form input
        address = user.get('address')
        if not address:
            address = request.form.get('address', '').strip()
            if address:  # Save to user's profile
                users_col.update_one({'_id': user['_id']}, {'$set': {'address': address}})
        if not address:
            return "Address is required."

        bookings_col.insert_one({
            'user_id': session['user_id'],
            'username': user['username'],
            'email': user['email'],
            'phone': user['phone'],
            'service': service,
            'date': date,
            'time': time,
            'address': address,
            'accepted': False
        })

        return redirect('/dashboard')
    
    return render_template('booking.html', user=user)


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
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/admin_login')

    # Get all bookings with user details
    bookings = []
    for b in bookings_col.find():
        user = users_col.find_one({'_id': ObjectId(b['user_id'])})
        booking = {
            '_id': str(b['_id']),
            'service': b.get('service'),
            'date': b.get('date'),
            'time': b.get('time'),
            'accepted': b.get('accepted', False),
            'completed': b.get('completed', False),
            'username': user.get('username', 'Unknown') if user else 'Unknown',
            'phone': user.get('phone', 'N/A') if user else 'N/A',
            'email': user.get('email', 'N/A') if user else 'N/A',
            'address': user.get('address', 'Not Provided') if user else 'Not Provided'
        }
        bookings.append(booking)

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
@app.route('/complete/<id>', methods=['POST'])
def complete(id):
    if not session.get('admin'):
        return redirect('/admin_login')
    
    bookings_col.update_one(
        {'_id': ObjectId(id)},
        {'$set': {'completed': True}}
    )
    return redirect('/admin_dashboard')

# ---- LOGOUT ----
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---- RUN APP ----
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
