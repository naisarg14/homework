from flask import Flask, flash, redirect, render_template, request, session, jsonify
from cs50 import SQL
from flask_session import Session
from datetime import datetime, timedelta
import helpers
import google_calander


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///homework.db")
database = "homework.db"


"""
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Perform authentication logic here
    
    if username == 'admin' and password == 'password':
        return 'Login successful!'
    else:
        return 'Invalid credentials'
"""



grades = ["9MWF", "9TTS", "9MOR", "10TTS", "11MWF", "12MWF", "12AM"]
grades_dict = {"9MWF": "Class 9 MWF",
               "9TTS": "Class 9 TTS",
               "9MOR": "Isucceed Achievers 6 AM",
               "10TTS": "Class 10-Diligent Squad",
               "11MWF": "Class 11",
               "12MWF": "Class 12",
               "12AM": "Class 12 AM",
               "diya": "Diya",
               "neel": "Neel",
               "ansh": "Ansh",
               "sakshi": "Sakshi",
               }
subjects = ["Mathematics", "Science", "Mathematics and Science"]
publications = {"oswaal": "Oswaal Books",
               "abd": "ABD Publications",
            }


def create_table():
    db.execute("CREATE TABLE IF NOT EXISTS homework (homework_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, date_given DATE, due_date DATE, grade TEXT,subject TEXT, description TEXT, event_id TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS exam (exam_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, exam_date DATE, grade TEXT, exam_time TEXT, marks INTEGER, portion TEXT, subject TEXT, event_id TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS outline (outline_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, class_date DATE, grade TEXT, description TEXT, subject TEXT, event_id TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS timetable (timetable_id INTEGER PRIMARY KEY AUTOINCREMENT, grade TEXT, subject TEXT, class_date DATE, start_time TEXT, end_time TEXT, event_id TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS worksheet (worksheet_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, given_date DATE, grade TEXT, subject TEXT, copies INTEGER, notes TEXT, publication)")
    db.execute("CREATE TABLE IF NOT EXISTS guest (guest_id INTEGER PRIMARY KEY AUTOINCREMENT, grade TEXT, date_given DATE, subject TEXT, duration TEXT, title TEXT, description TEXT)")


#Starting Page
@app.route('/')
def index():
    create_table()
    today = datetime.now().date().isoformat()
    tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()

    assignments = helpers.process_homework(db.execute("SELECT * FROM homework WHERE due_date = ? ORDER BY grade", today))
    exams = helpers.process_exams(db.execute("SELECT * FROM exam WHERE exam_date = ? ORDER BY exam_time", today))
    tomorrow_exams = helpers.process_exams(db.execute("SELECT * FROM exam WHERE exam_date = ? ORDER BY exam_time", tomorrow))
    timetable = helpers.process_timetable(db.execute("SELECT * FROM timetable WHERE class_date = ? ORDER BY start_time", today))

    return render_template('index.html', assignments=assignments, exams=exams, tomorrow_exams=tomorrow_exams, timetable=timetable)


#Add Homework
@app.route('/add_homework', methods=['GET', 'POST'])
def add_homework():
    if request.method == 'GET':
        today = datetime.now().date().isoformat()

        return render_template('add_homework.html', grades_dict=grades_dict, today=today)

    if request.method == 'POST':
        title = request.form['title'].title()
        date_given = request.form['date_given']
        due_date = request.form['due_date']
        grade = request.form['grade']
        subject = request.form['subject']
        description = request.form['description'].capitalize()


        id = db.execute(" INSERT INTO homework (title, date_given, due_date, grade, subject, description) VALUES (?, ?, ?, ?, ?, ?)",
                    title, date_given, due_date, grade, subject, description)
        
        formatted_text = helpers.format_homework(id)

        flash('Homework assignment added successfully!', 'success')
        return render_template("confirm_schedule_test.html", formatted_text=formatted_text)


@app.route("/delete_homework", methods=["POST"])
def delete_homework():
    homework_id = request.form["id"]
    session = request.form["session"]

    db.execute("DELETE FROM homework WHERE homework_id = ?", homework_id)
    flash("Deleted Successfully!")

    if session[0] == "G":
        assignments = db.execute("SELECT * FROM homework WHERE grade = ? ORDER BY due_date", session.removeprefix("GH"))
    if session[0] == "D":
        assignments = db.execute("SELECT * FROM homework WHERE due_date = ? ORDER BY grade", session.removeprefix("DH"))

    assignments = helpers.process_homework(assignments)

    return render_template('view_homework.html', assignments=assignments, table="homework", session=session)



#Schedule Tests
@app.route('/schedule_test', methods=["GET", "POST"])
def schedule_test():
    if request.method == "GET":
        today = datetime.now().date().isoformat()

        return render_template("schedule_test.html", grades_dict=grades_dict, today=today)

    if request.method == "POST":
        title = request.form['title'].title()
        exam_date = request.form['exam_date']
        grade = request.form['grade']
        exam_time = request.form['exam_time']
        marks = request.form['marks']
        portion = request.form['portion'].capitalize()
        subject = request.form['subject']


        id = db.execute("INSERT INTO exam (title, exam_date, grade, exam_time, marks, portion, subject) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   title, exam_date, grade, exam_time, marks, portion, subject)

        formatted_text = helpers.format_exam(id)

        flash("Exam Scheduled!")
        return render_template("confirm_schedule_test.html", formatted_text=formatted_text)



@app.route("/delete_exam", methods=["POST"])
def delete_exam():
    exam_id = request.form["id"]
    session = request.form["session"]

    db.execute("DELETE FROM exam WHERE exam_id = ?", exam_id)

    if session[0] == "G":
        assignments = db.execute("SELECT * FROM exam WHERE grade = ? ORDER BY exam_date", session.removeprefix("GE"))
        table = "exam"
    if session[0] == "D":
        assignments = db.execute("SELECT * FROM exam WHERE exam_date = ? ORDER BY grade", session.removeprefix("DE"))
        table = "exam"

    assignments = helpers.process_exams(assignments)

    flash("Deleted Successfully!")
    return render_template('view_homework.html', assignments=assignments, table=table, session=session)



# CLASS OUTLINE
@app.route("/class_outline", methods=["GET", "POST"])
def class_report():
    if request.method == "GET":
        today = datetime.now().date().isoformat()

        return render_template("add_outline.html", grades_dict=grades_dict, today=today)

    if request.method == "POST":
        title = request.form['title'].title()
        class_date = request.form['class_date']
        grade = request.form['grade']
        description = request.form['description'].capitalize()
        subject = request.form['subject']

        id = db.execute("INSERT INTO outline (title, class_date, grade, description, subject) VALUES (?, ?, ?, ?, ?)", title, class_date, grade, description, subject)
        
        formatted_text = helpers.format_outline(id)

        flash("Added Successfully")
        return render_template("confirm_schedule_test.html", formatted_text=formatted_text)


@app.route("/delete_outline", methods=["POST"])
def delete_outline():
    outline_id = request.form["id"]
    session = request.form["session"]

    db.execute("DELETE FROM outline WHERE outline_id = ?", outline_id)

    if session[0] == "G":
        assignments = db.execute("SELECT * FROM outline WHERE grade = ? ORDER BY class_date", session.removeprefix("GO"))
        table = "exam"
    if session[0] == "D":
        assignments = db.execute("SELECT * FROM outline WHERE class_date = ? ORDER BY grade", session.removeprefix("DO"))
        table = "exam"

    assignments = helpers.process_outline(assignments)

    flash("Deleted Successfully!")
    return render_template('view_homework.html', assignments=assignments, table=table, session=session)


#Generate Message
@app.route("/generate_message", methods=["POST"])
def generate_message():
    id = request.form["id"]
    session = request.form["session"]

    if session[1] == "H":
        formatted_text =  helpers.format_homework(id)

    if session[1] == "E":
        formatted_text = helpers.format_exam(id)

    if session[1] == "O":
        formatted_text = helpers.format_outline(id)

    if session[1] == "T":
        formatted_text = helpers.format_timetable(id)

    return render_template("confirm_schedule_test.html", formatted_text=formatted_text)



@app.route('/check_by_grade', methods=['GET', 'POST'])
def check_homework_grade():
    if request.method == "GET":
        today = datetime.now().date().isoformat()
        return render_template("get_homework.html", grades_dict=grades_dict, today=today)

    if request.method == 'POST':
        grade = request.form["grade"]

        if "get_homework" in request.form:
            assignments = helpers.process_homework(db.execute("SELECT * FROM homework WHERE grade = ? ORDER BY due_date", grade))
            table = "homework"
            session = f"GH{grade}"
        
        if "get_tests" in request.form:
            assignments = helpers.process_exams(db.execute("SELECT * FROM exam WHERE grade = ? ORDER BY exam_date", grade))
            table = "exam"
            session = f"GE{grade}"
        
        if "get_outline" in request.form:
            assignments = helpers.process_outline(db.execute("SELECT * FROM outline WHERE grade = ? ORDER BY class_date", grade))
            table = "outline"
            session = f"GO{grade}"
        
        if "get_timetable" in request.form:
            assignments = helpers.process_timetable(db.execute("SELECT * FROM timetable WHERE grade = ? ORDER BY class_date", grade))
            table = "timetable"
            session = f"GT{grade}"

        return render_template('view_homework.html', assignments=assignments, table=table, session=session)


@app.route('/check_by_date', methods=['POST'])
def check_by_date():
    date = request.form["date"]

    if "get_homework" in request.form:
        assignments = helpers.process_homework(db.execute("SELECT * FROM homework WHERE due_date = ? ORDER BY grade", date))
        table = "homework"
        session = f"DH{date}"

    if "get_tests" in request.form:
        assignments = helpers.process_exams(db.execute("SELECT * FROM exam WHERE exam_date = ? ORDER BY exam_time", date))
        table = "exam"
        session = f"DE{date}"

    if "get_outline" in request.form:
        assignments = helpers.process_outline(db.execute("SELECT * FROM outline WHERE class_date = ? ORDER BY grade", date))
        table = "outline"
        session = f"DO{date}"

    if "get_timetable" in request.form:
        assignments = helpers.process_timetable(db.execute("SELECT * FROM timetable WHERE class_date = ? ORDER BY start_time", date))
        print(assignments)
        table = "timetable"
        session = f"DT{date}"

    return render_template('view_homework.html', assignments=assignments, table=table, session=session)



# TIMETABLE
@app.route("/timetable", methods=["GET", "POST"])
def timetable():
    if request.method == "POST":
        grade = request.form["grade"]
        subject = request.form["subject"]
        class_date = request.form["class_date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]

        db.execute("INSERT INTO timetable (grade, subject, class_date, start_time, end_time) VALUES (?, ?, ?, ?, ?)", grade, subject, class_date, start_time, end_time)
        flash("Added Successfully!")


    today = datetime.now().date().isoformat()
    timetable = helpers.process_timetable(db.execute("SELECT * FROM timetable WHERE class_date = ? ORDER BY start_time", today))
    session = f"DT{today}"

    return render_template("add_timetable.html", timetable=timetable, session=session, grades_dict=grades_dict, today=today)


@app.route("/delete_timetable", methods=["POST"])
def delete_timetable():
    timetable_id = request.form["id"]
    session = request.form["session"]

    db.execute("DELETE FROM timetable WHERE timetable_id = ?", timetable_id)

    if session[0] == "G":
        assignments = db.execute("SELECT * FROM timetable WHERE grade = ? ORDER BY start_time", session.removeprefix("GT"))
        table = "timetable"
    if session[0] == "D":
        assignments = db.execute("SELECT * FROM timetable WHERE class_date = ? ORDER BY start_time", session.removeprefix("DT"))
        table = "timetable"

    assignments = helpers.process_timetable(assignments)

    flash("Deleted Successfully!")
    return render_template('view_homework.html', assignments=assignments, table=table, session=session)


@app.route("/add_event", methods=["POST"])
def add_event():
    id = request.form["id"]
    session = request.form["session"]

    if session[1] == "H":
        assignment = db.execute("SELECT * FROM homework WHERE homework_id = ? ", id)
        assignment = helpers.process_homework(assignment)
        event_id = (str(assignment["due_date"])).replace("-", "") + assignment["homework_id"]

    if session[1] == "E":
        exam = db.execute("SELECT * FROM exam WHERE exam_id = ? ", id)
        exam = helpers.process_exams(exam)

    if session[1] == "O":
        outline = db.execute("SELECT * FROM outline WHERE outline_id = ? ", id)
        outline = helpers.process_outline(outline)

    if session[1] == "T":
        timetable = db.execute("SELECT * FROM timetable WHERE timetable_id = ? ", id)
        timetable = helpers.process_timetable(timetable)



@app.route("/worksheet", methods=["GET", "POST"])
def add_worksheet():
    if request.method == "GET":
        today = datetime.now().date().isoformat()
        return render_template("add_worksheet.html", grades_dict=grades_dict, publications=publications, today=today)

    if request.method == "POST":
        publication = request.form["publication"]
        title = request.form["title"]
        given_date = request.form["given_date"]
        grade = request.form["grade"]
        subject = request.form["subject"]
        copies = request.form["copies"]
        notes = request.form["notes"]

        id = db.execute("INSERT INTO worksheet (publication, title, given_date, grade, subject, copies, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", publication, title, given_date, grade, subject, copies, notes)

        if "add_new" in request.form:
            return render_template("add_worksheet.html", grades_dict=grades_dict, publications=publications, today=today)
        
        if "add_message" in request.form:
            formatted_text = helpers.format_worksheet(id)
            flash("Worksheet Issued Successfully!")
            return render_template("confirm_schedule_test.html", formatted_text=formatted_text)


@app.route("/guest_lecture", methods=["GET", "POST"])
def guest_lecture():
    if request.method == "GET":
        return render_template("guest_lecture.html")

    if request.method == "POST":
        grade = request.form["grade"]
        date_given = request.form["date_given"]
        subject = request.form["subject"]
        duration = request.form["duration"]
        title = request.form["title"]
        description = request.form["description"]



@app.route("/about")
def about():
    return render_template("about.html")
