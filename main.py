from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import MySQLdb
from flask_mysqldb import MySQL
import re
from datetime import timedelta
import secrets



app = Flask(__name__)
app.secret_key =  secrets.token_hex(16)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'Tutoring_Center'

mysql = MySQL(app)

# Route to load the page with disciplines and subjects
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    
    # Fetch all disciplines for the first dropdown
    cur.execute('SELECT DisciplineID, DisciplineName FROM DISCIPLINE')
    disciplines = cur.fetchall()
    
    cur.close()

    return render_template('index.html', disciplines=disciplines)

# Route to get subjects based on selected discipline
@app.route('/get_subjects', methods=['POST'])
def get_subjects():
    discipline_id = request.form.get('discipline_id')
    
    cur = mysql.connection.cursor()
    
    # Query to get subjects based on discipline
    cur.execute('''
        SELECT s.SubjectID, s.SubjectName 
        FROM SUBJECT_LIST s
        JOIN SUBJECT_GROUPS sg ON sg.SubjectID = s.SubjectID
        WHERE sg.DisciplineID = %s
    ''', (discipline_id,))
    
    subjects = cur.fetchall()

    cur.close()

    return jsonify(subjects)

# Function to convert timedelta to string in HH:MM format
def timedelta_to_str(timedelta_obj):
    total_seconds = int(timedelta_obj.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}"

# Route to get schedule based on selected subject
# Route to get schedule based on selected subject and approval status
@app.route('/get_schedule', methods=['POST'])
def get_schedule():
    subject_id = request.form.get('subject_id')
    approved_filter = request.form.get('approved', 'Yes')  # Default to 'Yes'
    
    cur = mysql.connection.cursor()
    
    try:
        # If approved_filter is 'Yes', filter by approved sessions, else show all
        if approved_filter == 'Yes':
            cur.execute('''
                SELECT s.DayOfWeek, s.StartTime, s.Loc
                FROM SCHEDULE s
                JOIN SUBJECTS subj ON s.Email = subj.Email
                WHERE subj.SubjectID = %s AND s.Approved = 'Yes'
            ''', (subject_id,))
        else:
            cur.execute('''
                SELECT s.DayOfWeek, s.StartTime, s.Loc, s.Approved
                FROM SCHEDULE s
                JOIN SUBJECTS subj ON s.Email = subj.Email
                WHERE subj.SubjectID = %s
            ''', (subject_id,))
        
        schedules = cur.fetchall()

        # Convert the result into a list of dictionaries for easier access in JavaScript
        schedule_list = [{
            'DayOfWeek': row[0],
            'StartTime': timedelta_to_str(row[1]),  # Convert time to string
            'Loc': row[2],
            'Approved': row[3] if len(row) > 3 else 'Yes'  # Only include Approved if it's in the result
        } for row in schedules]

        return jsonify(schedule_list)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        
        # Query to validate login from LOGIN table and get user roles from USERS table
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Ensure MySQLdb is imported
        cursor.execute('''
            SELECT u.Email, u.FirstName, u.LastName, u.Tutor, u.Admin
            FROM LOGIN l
            JOIN USERS u ON l.Email = u.Email
            WHERE l.Email = %s AND l.Pword = %s
        ''', (email, password,))
        account = cursor.fetchone()
        
        if account:
            session['loggedin'] = True
            session['email'] = account['Email']
            session['firstname'] = account['FirstName']
            session['lastname'] = account['LastName']
            session['tutor'] = account['Tutor']
            session['admin'] = account['Admin']
            
            # Redirect based on role
            if account['Admin'] == 'Yes':
                return redirect(url_for('admin_dashboard'))
            elif account['Tutor'] == 'Yes':
                return redirect(url_for('tutor_dashboard'))
            else:
                return redirect(url_for('index'))  # General home page for non-admin/tutor users
        else:
            msg = 'Incorrect email/password!'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('email', None)
    session.pop('firstname', None)
    session.pop('lastname', None)
    session.pop('tutor', None)
    session.pop('admin', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form and 'firstname' in request.form and 'lastname' in request.form:
        email = request.form['email']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        tutor = 'No'  # Default to 'No'
        admin = 'No'  # Default to 'No'
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM USERS WHERE Email = %s', (email,))
        account = cursor.fetchone()
        
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', firstname):
            msg = 'First name must contain only letters!'
        elif not re.match(r'[A-Za-z0-9]+', lastname):
            msg = 'Last name must contain only letters!'
        else:
            # Insert new account into USERS and LOGIN tables
            cursor.execute('INSERT INTO USERS (Email, FirstName, LastName, Tutor, Admin) VALUES (%s, %s, %s, %s, %s)',
                           (email, firstname, lastname, tutor, admin))
            cursor.execute('INSERT INTO LOGIN (Email, Pword) VALUES (%s, %s)', (email, password))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('login'))
    return render_template('register.html', msg=msg)

# Existing route for admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'loggedin' in session and session.get('admin') == 'Yes':
        return render_template('admin_dashboard.html', firstname=session['firstname'])
    else:
        return redirect(url_for('login'))

def generate_time_slots():
    slots = []
    for hour in range(8, 21):  # 8 AM to 9 PM
        for minute in (0, 30):
            slots.append(f"{hour:02}:{minute:02}:00")
    return slots

# Helper function to convert timedelta to HH:MM format
def timedelta_to_str(timedelta_obj):
    total_seconds = int(timedelta_obj.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}"  # Returns HH:MM format

# New route for tutor dashboard
@app.route('/tutor_dashboard', methods=['GET', 'POST'])
def tutor_dashboard():
    if 'loggedin' in session and session.get('tutor') == 'Yes':
        email = session['email']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch all subjects and pre-checked subjects for the user
        cur.execute("SELECT SubjectID, SubjectName FROM SUBJECT_LIST")
        subjects = cur.fetchall()
        cur.execute("SELECT SubjectID FROM SUBJECTS WHERE Email = %s", (email,))
        tutor_subjects = {row['SubjectID'] for row in cur.fetchall()}

        # Fetch existing availability with time formatted as HH:MM
        cur.execute("SELECT DayOfWeek, StartTime FROM SCHEDULE WHERE Email = %s", (email,))
        existing_availability = {(row['DayOfWeek'], timedelta_to_str(row['StartTime'])) for row in cur.fetchall()}

        if request.method == 'POST':
            # 1. Handle subject update form
            if 'subject_ids' in request.form:
                selected_subject_ids = set(map(int, request.form.getlist('subject_ids')))
                # Remove unselected subjects
                for subject_id in tutor_subjects - selected_subject_ids:
                    cur.execute("DELETE FROM SUBJECTS WHERE Email = %s AND SubjectID = %s", (email, subject_id))
                # Add newly selected subjects
                for subject_id in selected_subject_ids - tutor_subjects:
                    cur.execute("INSERT INTO SUBJECTS (Email, SubjectID) VALUES (%s, %s)", (email, subject_id))
                mysql.connection.commit()
                tutor_subjects = selected_subject_ids  # Update local cache after database update

            # 2. Handle availability update form, day-specific
            if 'availability_day' in request.form:
                availability_day = request.form.get("availability_day")
                selected_availability = set()
                location_default = request.form.get("location_default", "Online")

                # Collect selected availability time slots for the specific day
                if availability_day:
                    for time in request.form.getlist("availability_times"):
                        location = request.form.get(f"location_{time}", location_default)
                        selected_availability.add((availability_day, time, location))

                # Delete unselected availability slots only for the specific day
                to_delete = {(day, time) for day, time in existing_availability if day == availability_day and (day, time) not in {(day, time) for day, time, _ in selected_availability}}
                for day, time in to_delete:
                    cur.execute("DELETE FROM SCHEDULE WHERE Email = %s AND DayOfWeek = %s AND StartTime = %s", (email, day, time))

                # Add or update new availability for the specific day
                for day, time, location in selected_availability:
                    if (day, time) not in {(d, t) for d, t in existing_availability}:
                        cur.execute("INSERT INTO SCHEDULE (Email, DayOfWeek, StartTime, Loc, Approved) VALUES (%s, %s, %s, %s, 'No')",
                                    (email, day, time, location))
                    else:
                        cur.execute("UPDATE SCHEDULE SET Loc = %s WHERE Email = %s AND DayOfWeek = %s AND StartTime = %s", 
                                    (location, email, day, time))

                mysql.connection.commit()

        # Fetch updated schedule for display
        cur.execute("""
            SELECT DayOfWeek, StartTime, Loc
            FROM SCHEDULE
            WHERE Email = %s AND Approved = 'Yes'
            ORDER BY DayOfWeek, StartTime
        """, (email,))
        approved_schedule = [
            {
                "DayOfWeek": row['DayOfWeek'],
                "StartTime": timedelta_to_str(row['StartTime']),
                "Loc": row['Loc']
            }
            for row in cur.fetchall()
        ]

        # Updated availability list for rendering
        cur.execute("SELECT DayOfWeek, StartTime, Loc FROM SCHEDULE WHERE Email = %s", (email,))
        fetched_schedule = cur.fetchall()
        tutor_schedule = [
            (row['DayOfWeek'], timedelta_to_str(row['StartTime']), row['Loc']) for row in fetched_schedule
        ]

        cur.close()
        
        return render_template('tutor_dashboard.html', firstname=session['firstname'],
                               subjects=subjects, tutor_subjects=tutor_subjects,
                               approved_schedule=approved_schedule,
                               tutor_schedule=tutor_schedule)
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)