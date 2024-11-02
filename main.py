from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import MySQLdb
from flask_mysqldb import MySQL
import re
from datetime import timedelta, datetime
import secrets


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = '' 
app.config['MYSQL_DB'] = 'tutoring_center'

mysql = MySQL(app)

# Route to load the page with disciplines and subjects
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT DisciplineID, DisciplineName FROM DISCIPLINE')
    disciplines = cur.fetchall()
    cur.close()
    return render_template('index.html', disciplines=disciplines)

# Route to get subjects based on selected discipline
@app.route('/get_subjects', methods=['POST'])
def get_subjects():
    discipline_id = request.json.get('discipline_id')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('''
        SELECT sl.SubjectID, sl.SubjectName 
        FROM SUBJECT_LIST sl
        JOIN SUBJECT_GROUPS sg ON sg.SubjectID = sl.SubjectID
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

# Route to get schedule based on selected subject and approval status
@app.route('/get_schedule', methods=['POST'])
def get_schedule():
    data = request.json
    subject_id = data.get('subject_id')
    approved_filter = 'Yes'

    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT s.DayOfWeek, s.StartTime, s.Loc
        FROM SCHEDULE s
        JOIN SUBJECTS subj ON s.Email = subj.Email
        WHERE subj.SubjectID = %s AND s.Approved = %s
    ''', (subject_id, approved_filter))
    
    schedules = cur.fetchall()
    schedule_list = [
        {
            'DayOfWeek': row[0],
            'StartTime': timedelta_to_str(row[1]),
            'Loc': row[2]
        }
        for row in schedules
    ]
    cur.close()
    return jsonify(schedule_list)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
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
            return redirect(url_for('admin_dashboard') if account['Admin'] == 'Yes' else url_for('tutor_dashboard') if account['Tutor'] == 'Yes' else url_for('index'))
        else:
            msg = 'Incorrect email/password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and all(field in request.form for field in ('email', 'password', 'firstname', 'lastname')):
        email = request.form['email']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
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
            cursor.execute('INSERT INTO USERS (Email, FirstName, LastName, Tutor, Admin) VALUES (%s, %s, %s, %s, %s)', (email, firstname, lastname, 'No', 'No'))
            cursor.execute('INSERT INTO LOGIN (Email, Pword) VALUES (%s, %s)', (email, password))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('login'))
    return render_template('register.html', msg=msg)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'loggedin' in session and session.get('admin') == 'Yes':
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT DisciplineID, DisciplineName FROM DISCIPLINE")
        disciplines = cur.fetchall()
        cur.execute("SELECT Email, FirstName, LastName, Tutor, Admin FROM USERS")
        users = cur.fetchall()
        cur.execute('''
            SELECT s.Email, sl.SubjectName, s.DayOfWeek, s.StartTime, s.Loc, s.Approved
            FROM SCHEDULE s
            JOIN SUBJECTS subj ON s.Email = subj.Email
            JOIN SUBJECT_LIST sl ON subj.SubjectID = sl.SubjectID
            WHERE s.Approved = 'No'
            ORDER BY s.Email, s.DayOfWeek, s.StartTime
        ''')
        schedules = [{
            'Email': row['Email'],
            'SubjectName': row['SubjectName'],
            'DayOfWeek': row['DayOfWeek'],
            'StartTime': (datetime.min + row['StartTime']).time().strftime('%H:%M'),
            'Loc': row['Loc'],
            'Approved': row['Approved']
        } for row in cur.fetchall()]
        cur.close()
        return render_template('admin_dashboard.html', firstname=session['firstname'], disciplines=disciplines, users=users, schedules=schedules)
    return redirect(url_for('login'))

# Fetch tutors based on selected subject
@app.route('/get_tutors/<int:subject_id>')
def get_tutors(subject_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('''
        SELECT u.Email, u.FirstName, u.LastName
        FROM USERS u
        JOIN SUBJECTS s ON u.Email = s.Email
        WHERE s.SubjectID = %s AND u.Tutor = 'Yes'
    ''', (subject_id,))
    tutors = cur.fetchall()
    cur.close()
    return jsonify(tutors)

@app.route('/get_student_schedule/<string:tutor_email>')
def get_student_schedule(tutor_email):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Fetch unique schedule entries for the tutor
    cur.execute("""
        SELECT DISTINCT sch.Email, sch.DayOfWeek, sch.StartTime, sch.Loc, sch.Approved
        FROM SCHEDULE sch
        JOIN SUBJECTS subj ON sch.Email = subj.Email
        WHERE sch.Email = %s
    """, (tutor_email,))
    
    schedules = cur.fetchall()

    # Convert StartTime to HH:MM format for JSON compatibility
    for schedule in schedules:
        schedule['StartTime'] = (datetime.min + schedule['StartTime']).time().strftime('%H:%M')

    cur.close()
    return jsonify(schedules)

@app.route('/get_approved_schedule', methods=['GET'])
def get_approved_schedule():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('''
        SELECT DayOfWeek, StartTime, Loc
        FROM SCHEDULE
        WHERE Approved = 'Yes'
    ''')
    schedules = [
        {
            'DayOfWeek': row['DayOfWeek'],
            'StartTime': timedelta_to_str(row['StartTime']),
            'Loc': row['Loc']
        }
        for row in cur.fetchall()
    ]
    cur.close()
    return jsonify(schedules)

@app.route('/get_approved_hours', methods=['GET'])
def get_approved_hours():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('''
        SELECT u.FirstName, u.LastName, s.Email,
               SUM(TIMESTAMPDIFF(MINUTE, s.StartTime, ADDTIME(s.StartTime, '00:30:00')))/60 AS TotalHours
        FROM USERS u
        JOIN SCHEDULE s ON u.Email = s.Email
        WHERE s.Approved = 'Yes'
        GROUP BY s.Email
        HAVING TotalHours > 0
    ''')
    tutors = cur.fetchall()
    cur.close()
    return jsonify(tutors)

@app.route('/approve_schedules', methods=['POST'])
def approve_schedules():
    if 'loggedin' in session and session.get('admin') == 'Yes':
        tutor_email = request.form.get('tutor_email')
        if not tutor_email:
            flash("Tutor email is missing in the form submission.")
            return redirect(url_for('admin_dashboard'))

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch all schedule entries for the selected tutor
        cur.execute("SELECT Email, DayOfWeek, StartTime FROM SCHEDULE WHERE Email = %s", (tutor_email,))
        all_schedules = cur.fetchall()

        # Iterate over each schedule entry and determine its approved status
        for schedule in all_schedules:
            email = schedule['Email']
            day_of_week = schedule['DayOfWeek']
            start_time = timedelta_to_str(schedule['StartTime']).replace(":", "-")  # Format for matching form data
            checkbox_name = f"approve_{email}_{day_of_week}_{start_time}"
            
            # Set approval status based on presence in form data
            approved_status = "Yes" if checkbox_name in request.form else "No"

            # Update the schedule entry with the approval status
            cur.execute("""
                UPDATE SCHEDULE 
                SET Approved = %s 
                WHERE Email = %s AND DayOfWeek = %s AND StartTime = %s
            """, (approved_status, email, day_of_week, schedule['StartTime']))
        
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('admin_dashboard'))
    else:
        flash("Unauthorized access.")
        return redirect(url_for('login'))

@app.route('/update_user_roles', methods=['POST'])
def update_user_roles():
    if 'loggedin' in session and session.get('admin') == 'Yes':
        cur = mysql.connection.cursor()
        for field_name in request.form.keys():
            if field_name.startswith("tutor_") or field_name.startswith("admin_"):
                email = field_name.split('_')[1]
                tutor_role = 'Yes' if f'tutor_{email}' in request.form else 'No'
                admin_role = 'Yes' if f'admin_{email}' in request.form else 'No'
                cur.execute("UPDATE USERS SET Tutor = %s, Admin = %s WHERE Email = %s", (tutor_role, admin_role, email))

            # Check for delete checkbox and delete user if checked
            if field_name.startswith("delete_"):
                email_to_delete = field_name.split('_')[1]
                cur.execute("DELETE FROM USERS WHERE Email = %s", (email_to_delete,))

        mysql.connection.commit()
        cur.close()
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))

# Helper function to generate time slots in HH:MM format from 8:00 to 21:00
def generate_time_slots():
    slots = []
    for hour in range(8, 21):  # 8 AM to 9 PM
        for minute in (0, 30):
            slots.append(f"{hour:02}:{minute:02}:00")
    return slots

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
    app.run()