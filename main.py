from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

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

# Route to get schedule based on selected subject
@app.route('/get_schedule', methods=['POST'])
def get_schedule():
    subject_id = request.form.get('subject_id')
    
    cur = mysql.connection.cursor()
    
    # Query to get the schedule related to the selected subject
    cur.execute('''
        SELECT s.DayOfWeek, s.StartTime, s.Loc
        FROM SCHEDULE s
        JOIN SUBJECTS subj ON s.Email = subj.Email
        WHERE subj.SubjectID = %s AND s.Approved = 'Yes'
    ''', (subject_id,))
    
    schedules = cur.fetchall()

    cur.close()

    return jsonify(schedules)

if __name__ == '__main__':
    app.run(debug=True)