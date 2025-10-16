
from flask import Flask, render_template, request, redirect, url_for, flash
from config import get_db_connection
import os, csv, datetime
from flask import session  

app = Flask(__name__)
app.secret_key = "event_secret_key"

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username'].strip()
    password = request.form['password'].strip()  
    if username:
        session['username'] = username
        flash(f"Welcome, {username}!")
        return redirect(url_for('events'))  
    else:
        flash("Please enter a username.")
        return redirect(url_for('index'))  


@app.route('/events')
def events():

    if 'username' not in session:
        flash("Please login first.")
        return redirect(url_for('index'))
    

    q_title = request.args.get('title', '').strip()
    q_date  = request.args.get('date', '').strip()

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if q_title and q_date:
        cur.execute("SELECT * FROM events WHERE title LIKE %s AND date = %s ORDER BY date",
                    (f"%{q_title}%", q_date))
    elif q_title:
        cur.execute("SELECT * FROM events WHERE title LIKE %s ORDER BY date", (f"%{q_title}%",))
    elif q_date:
        cur.execute("SELECT * FROM events WHERE date = %s ORDER BY date", (q_date,))
    else:
        cur.execute("SELECT * FROM events ORDER BY date")

    events = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('events.html', events=events, q_title=q_title, q_date=q_date)


@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        date = request.form['date']
        location = request.form['location'].strip()
        capacity = int(request.form['capacity'] or 0)
        ticket_price = float(request.form.get('ticket_price') or 0)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO events (title, description, date, location, capacity, ticket_price) VALUES (%s,%s,%s,%s,%s,%s)",
            (title, description, date, location, capacity, ticket_price)
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("Event added successfully!")
        return redirect(url_for('events'))
    return render_template('add_event.html')


@app.route('/edit_event/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        date = request.form['date']
        location = request.form['location'].strip()
        capacity = int(request.form['capacity'] or 0)
        ticket_price = float(request.form.get('ticket_price') or 0)

        cur.execute("""
            UPDATE events SET title=%s, description=%s, date=%s, location=%s, capacity=%s, ticket_price=%s
            WHERE id=%s
        """, (title, description, date, location, capacity, ticket_price, id))
        conn.commit()
        cur.close()
        conn.close()
        flash("Event updated successfully!")
        return redirect(url_for('events'))

    cur.execute("SELECT * FROM events WHERE id=%s", (id,))
    event = cur.fetchone()
    cur.close()
    conn.close()
    if not event:
        flash("Event not found.")
        return redirect(url_for('events'))
    return render_template('edit_event.html', event=event)


@app.route('/delete_event/<int:id>')
def delete_event(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Event deleted.")
    return redirect(url_for('events'))


@app.route('/attendees')
def attendees():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT a.*, e.title as event_title, e.date as event_date
        FROM attendees a
        LEFT JOIN events e ON a.event_id = e.id
        ORDER BY e.date, a.name
    """)
    attendees = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('attendees.html', attendees=attendees)


@app.route('/add_attendee', methods=['GET', 'POST'])
def add_attendee():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, title, date, capacity FROM events ORDER BY date")
    events = cur.fetchall()

    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        event_id = int(request.form['event_id'])

        
        cur.execute("SELECT capacity, (SELECT COUNT(*) FROM attendees WHERE event_id=%s) AS sold FROM events WHERE id=%s",
                    (event_id, event_id))
        row = cur.fetchone()
        sold = row['sold'] if row else 0
        capacity = row['capacity'] if row else 0
        if sold >= capacity:
            flash("Cannot register — event capacity full.")
            cur.close()
            conn.close()
            return redirect(url_for('add_attendee'))

        cur.execute("INSERT INTO attendees (name, email, phone, event_id) VALUES (%s,%s,%s,%s)",
                    (name, email, phone, event_id))
        conn.commit()
        cur.close()
        conn.close()
        flash("Attendee registered successfully!")
        return redirect(url_for('attendees'))

    cur.close()
    conn.close()
    return render_template('add_attendee.html', events=events)

@app.route('/edit_attendee/<int:id>', methods=['GET', 'POST'])
def edit_attendee(id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM attendees WHERE id=%s", (id,))
    attendee = cur.fetchone()
    cur.execute("SELECT id, title FROM events ORDER BY date")
    events = cur.fetchall()

    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        event_id = int(request.form['event_id'])
        cur.execute("UPDATE attendees SET name=%s, email=%s, phone=%s, event_id=%s WHERE id=%s",
                    (name, email, phone, event_id, id))
        conn.commit()
        cur.close()
        conn.close()
        flash("Attendee updated.")
        return redirect(url_for('attendees'))

    cur.close()
    conn.close()
    if not attendee:
        flash("Attendee not found.")
        return redirect(url_for('attendees'))
    return render_template('edit_attendee.html', attendee=attendee, events=events)


@app.route('/delete_attendee/<int:id>')
def delete_attendee(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM attendees WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Attendee deleted.")
    return redirect(url_for('attendees'))


@app.route('/tickets')
def tickets():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT e.id, e.title, e.capacity,
               COUNT(a.id) AS sold,
               (e.capacity - COUNT(a.id)) AS available,
               e.ticket_price
        FROM events e
        LEFT JOIN attendees a ON e.id = a.event_id
        GROUP BY e.id
        ORDER BY e.date
    """)
    tickets = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('tickets.html', tickets=tickets)


@app.route('/report')
def report():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT e.id, e.title,
               COUNT(a.id) AS sold,
               COALESCE(e.ticket_price,0) AS price,
               (COUNT(a.id) * COALESCE(e.ticket_price,0)) AS revenue
        FROM events e
        LEFT JOIN attendees a ON e.id = a.event_id
        GROUP BY e.id
        ORDER BY revenue DESC
    """)
    report = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('report.html', report=report)


@app.route('/import_csv', methods=['GET', 'POST'])
def import_csv():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash("No file uploaded.")
            return redirect(request.url)
        if not file.filename.lower().endswith('.csv'):
            flash("Please upload a CSV file.")
            return redirect(request.url)

        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        
        with open(filepath, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            conn = get_db_connection()
            cur = conn.cursor()
            for row in reader:
                title = row.get('Event Title') or row.get('Title') or ''
                desc = row.get('Description') or ''
                date = row.get('Date') or None
                location = row.get('Location') or ''
                capacity = int(row.get('Capacity') or 0)
                ticket_price = float(row.get('Ticket Price') or row.get('ticket_price') or 0)
                
                try:
                    if date:
                    
                        datetime.datetime.strptime(date, "%Y-%m-%d")
                except Exception:
                    date = None
                cur.execute("""
                    INSERT INTO events (title, description, date, location, capacity, ticket_price)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, (title, desc, date, location, capacity, ticket_price))
            conn.commit()
            cur.close()
            conn.close()
        flash("CSV imported successfully.")
        return redirect(url_for('events'))
    return render_template('import_csv.html')


if __name__ == '__main__':
    app.run(debug=True)
