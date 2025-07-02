from flask import Flask, render_template, request, redirect, session
from bson.objectid import ObjectId
from utils.mongo import users_col, admins_col, bookings_col, services_col  # added services_col
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ---- INDEX ----
@app.route('/')
def index():
    services = list(services_col.find())
    return render_template('index.html', services=services)

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
    error = None
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']

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

        admin = admins_col.find_one({
            'username': identifier,
            'password': password
        })

        if admin:
            session['admin'] = True
            session['admin_name'] = admin['username']
            return redirect('/admin_dashboard')

        error = "Invalid credentials"

    return render_template('user_login.html', error=error)

# DASBOARD------
from datetime import datetime, timedelta

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/user_login')

    page = int(request.args.get('page', 1))
    per_page = 5
    skip = (page - 1) * per_page

    total_bookings = bookings_col.count_documents({'user_id': str(session['user_id'])})
    total_pages = (total_bookings + per_page - 1) // per_page

    # Get paginated bookings
    bookings_cursor = bookings_col.find({'user_id': str(session['user_id'])}).sort('datetime', -1)
    bookings = list(bookings_cursor.skip(skip).limit(per_page))

    # Get *all* bookings (for total spent)
    all_bookings_cursor = bookings_col.find({'user_id': str(session['user_id'])})
    total_spent = 0
    for b in all_bookings_cursor:
        if b.get('service_details'):
            total_spent += sum(s.get('price', 0) for s in b['service_details'])

    all_services = list(services_col.find())

    return render_template(
        'dashboard.html',
        bookings=bookings,
        services=all_services,
        total_bookings=total_bookings,
        total_spent=total_spent,
        page=page,
        total_pages=total_pages
    )


@app.route('/quick_book', methods=['POST'])
def quick_book():
    if 'user_id' not in session:
        return redirect('/user_login')

    user = users_col.find_one({'_id': ObjectId(session['user_id'])})
    services = request.form.getlist('services')
    date = request.form['date']
    time = request.form['time']

    if not services:
        return "Please select at least one service.", 400
    if not date or not time:
        return "Please select date and time.", 400
    if not user.get('address'):
        return redirect('/edit_profile')

    try:
        selected_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    except ValueError:
        return "Invalid date or time format.", 400
    if selected_datetime < datetime.now():
        return "Cannot book for a past time.", 400

    service_details = []
    for name in services:
        s = services_col.find_one({'name': name})
        if s:
            service_details.append({
                'name': name,
                'price': s.get('price', 0),
                'duration': s.get('duration', 0)
            })

    bookings_col.insert_one({
        'user_id': str(user['_id']),
        'username': user['username'],
        'services': [s['name'] for s in service_details],
        'service_details': service_details,
        'date': date,
        'time': time,
        'datetime': selected_datetime,
        'address': user.get('address'),
        'phone': user.get('phone'),
        'accepted': False,
        'completed': False
    })

    return redirect('/dashboard')


@app.route('/update_booking/<id>', methods=['POST'])
def update_booking(id):
    date = request.form['date']
    time = request.form['time']

    try:
        selected_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    except ValueError:
        return render_dashboard_with_error("Invalid date or time format.")
    
    if selected_datetime < datetime.now():
        return render_dashboard_with_error("Cannot reschedule to a past time.")

    bookings_col.update_one(
        {'_id': ObjectId(id)},
        {'$set': {
            'date': date,
            'time': time,
            'datetime': selected_datetime,
            'accepted': False
        }}
    )
    return redirect('/dashboard')

def render_dashboard_with_error(error):
    page = 1
    per_page = 5
    skip = 0
    total_bookings = bookings_col.count_documents({'user_id': str(session['user_id'])})
    bookings_cursor = bookings_col.find(
        {'user_id': str(session['user_id'])}
    ).sort('datetime', -1).skip(skip).limit(per_page)
    bookings = list(bookings_cursor)
    all_services = list(services_col.find())
    return render_template(
        'dashboard.html',
        bookings=bookings,
        services=all_services,
        page=page,
        prev_page=False,
        next_page=per_page < total_bookings,
        total_pages=(total_bookings + per_page - 1) // per_page,
        error=error
    )

@app.route('/delete_booking/<id>', methods=['POST'])
def delete_booking(id):
    bookings_col.delete_one({'_id': ObjectId(id)})
    return redirect('/dashboard')

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
            'password': user['password']
        }
        users_col.update_one({'_id': ObjectId(session['user_id'])}, {'$set': updated_data})
        session['username'] = updated_data['username']
        return redirect('/dashboard')
    return render_template('edit_profile.html', user=user)

# ---- ADMIN DASHBOARD ----
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/user_login')

    page = int(request.args.get('page', 1))
    per_page = 5
    skip = (page - 1) * per_page

    total_orders = bookings_col.count_documents({})
    pending_orders = bookings_col.count_documents({'accepted': False})
    completed_orders = bookings_col.count_documents({'completed': True})

    cursor = bookings_col.find().sort([('_id', -1)])
    bookings = list(cursor.skip(skip).limit(per_page))

    # Enrich bookings with user info if needed
    enriched_bookings = []
    for b in bookings:
        user = users_col.find_one({'_id': ObjectId(b['user_id'])})
        enriched_bookings.append({
            **b,
            'username': user.get('username', 'Unknown') if user else 'Unknown',
            'phone': user.get('phone', 'N/A') if user else 'N/A',
            'email': user.get('email', 'N/A') if user else 'N/A',
            'address': user.get('address', 'Not Provided') if user else 'Not Provided'
        })

    total_pages = (total_orders + per_page - 1) // per_page

    return render_template(
        'admin_dashboard.html',
        bookings=enriched_bookings,
        total_orders=total_orders,
        pending_orders=pending_orders,
        completed_orders=completed_orders,
        page=page,
        total_pages=total_pages
    )



@app.route('/accept/<id>', methods=['POST'])
def accept(id):
    if not session.get('admin'):
        return redirect('/user_login')
    bookings_col.update_one(
        {'_id': ObjectId(id)},
        {'$set': {'accepted': True}}
    )
    return redirect('/admin_dashboard')
@app.template_filter('format_time')
def format_time(value):
    try:
        from datetime import datetime
        # parse the 24-hour time string
        t = datetime.strptime(value, '%H:%M')
        return t.strftime('%I:%M %p').lstrip('0')  # e.g., 3:00 PM
    except:
        return value  # fallback if format is unexpected

@app.route('/complete/<id>', methods=['POST'])
def complete(id):
    if not session.get('admin'):
        return redirect('/user_login')
    bookings_col.update_one(
        {'_id': ObjectId(id)},
        {'$set': {'completed': True}}
    )
    return redirect('/admin_dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    load_dotenv()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
