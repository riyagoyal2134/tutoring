from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'  # Change if necessary
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'Tutoring_Center'

# Initialize MySQL
mysql = MySQL(app)

# Route to display the initial page with disciplines
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    
    # Fetch all disciplines
    cur.execute('SELECT DisciplineID, DisciplineName FROM DISCIPLINE')
    disciplines = cur.fetchall()
    
    cur.close()

    return render_template('index.html', disciplines=disciplines)

# Route to get subjects based on selected discipline
@app.route('/get_subjects', methods=['POST'])
def get_subjects():
    discipline_id = request.form.get('discipline_id')
    
    cur = mysql.connection.cursor()
    
    # Query subjects related to the selected discipline
    cur.execute('''
        SELECT s.SubjectID, s.SubjectName 
        FROM SUBJECT_LIST s
        JOIN SUBJECT_GROUPS sg ON s.SubjectID = sg.SubjectID
        WHERE sg.DisciplineID = %s
    ''', (discipline_id,))
    
    subjects = cur.fetchall()

    cur.close()

    return jsonify(subjects)

if __name__ == '__main__':
    app.run(debug=True)