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
               "vedant": "Vedant",
               "dhiya": "Dhiya",
               }
subjects = ["Mathematics", "Science", "Mathematics and Science"]
publications = {"oswaal": "Oswaal Books",
               "abd": "ABD Publications",
            }


def create_table():
    db.execute("CREATE TABLE IF NOT EXISTS homework (homework_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, date_given DATE, due_date DATE, grade TEXT,subject TEXT, description TEXT, event_id TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS exam (exam_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, exam_date DATE, grade TEXT, exam_time TEXT, marks INTEGER, portion TEXT, subject TEXT, event_id TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS outline (outline_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, class_date DATE, grade TEXT, description TEXT, subject TEXT, event_id TEXT, time TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS timetable (timetable_id INTEGER PRIMARY KEY AUTOINCREMENT, grade TEXT, subject TEXT, class_date DATE, start_time TEXT, end_time TEXT, event_id TEXT, description TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS worksheet (worksheet_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, given_date DATE, grade TEXT, subject TEXT, copies INTEGER, notes TEXT, publication TEXT)")
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
    timetables = helpers.process_timetable(db.execute("SELECT * FROM timetable WHERE class_date = ? ORDER BY start_time", today))

    return render_template('index.html', assignments=assignments, exams=exams, tomorrow_exams=tomorrow_exams, timetables=timetables)


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
        description = request.form['description']


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
    if session[0] == "A":
        assignments = db.execute("SELECT * FROM homework ORDER BY grade")

    assignments = helpers.process_homework(assignments)

    return render_template('view_homework.html', assignments=assignments, table="homework", session=session)



#Schedule Tests
@app.route('/schedule_test', methods=["GET", "POST"])
def schedule_test():
    if request.method == "GET":
        today = datetime.now().date().isoformat()

        return render_template("add_test.html", grades_dict=grades_dict, today=today)

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
        exams = db.execute("SELECT * FROM exam WHERE grade = ? ORDER BY exam_date", session.removeprefix("GE"))
    if session[0] == "D":
        exams = db.execute("SELECT * FROM exam WHERE exam_date = ? ORDER BY grade", session.removeprefix("DE"))
    if session[0] == "A":
        exams = db.execute("SELECT * FROM exam ORDER BY grade")

    exams = helpers.process_exams(exams)

    flash("Deleted Successfully!")
    return render_template('view_exam.html', exams=exams, table="exam", session=session)



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
        description = request.form['description']
        subject = request.form['subject']
        time = request.form['time']

        id = db.execute("INSERT INTO outline (title, class_date, grade, description, subject, time) VALUES (?, ?, ?, ?, ?)", title, class_date, grade, description, subject, time)
        
        formatted_text = helpers.format_outline(id)

        flash("Added Successfully")
        return render_template("confirm_schedule_test.html", formatted_text=formatted_text)


@app.route("/delete_outline", methods=["POST"])
def delete_outline():
    outline_id = request.form["id"]
    session = request.form["session"]

    db.execute("DELETE FROM outline WHERE outline_id = ?", outline_id)

    if session[0] == "G":
        outlines = db.execute("SELECT * FROM outline WHERE grade = ? ORDER BY class_date", session.removeprefix("GO"))
    if session[0] == "D":
        outlines = db.execute("SELECT * FROM outline WHERE class_date = ? ORDER BY grade", session.removeprefix("DO"))
    if session[0] == "A":
        outlines = db.execute("SELECT * FROM outline ORDER BY grade")

    outlines = helpers.process_outline(outlines)

    flash("Deleted Successfully!")
    return render_template('view_outline.html', outlines=outlines, table="outline", session=session)


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
    
    if session[1] == "W":
        formatted_text = helpers.format_worksheet(id)
    
    if session[1] == "L":
        formatted_text = helpers.format_guest(id)

    return render_template("confirm_schedule_test.html", formatted_text=formatted_text)



@app.route('/check_by_grade', methods=['GET', 'POST'])
def check_homework_grade():
    if request.method == "GET":
        today = datetime.now().date().isoformat()
        return render_template("check_database.html", grades_dict=grades_dict, today=today)

    if request.method == 'POST':
        grade = request.form["grade"]

        if "get_homework" in request.form:
            assignments = helpers.process_homework(db.execute("SELECT * FROM homework WHERE grade = ? ORDER BY due_date", grade))
            session = f"GH{grade}"
            return render_template('view_homework.html', assignments=assignments, session=session)
        
        if "get_tests" in request.form:
            exams = helpers.process_exams(db.execute("SELECT * FROM exam WHERE grade = ? ORDER BY exam_date", grade))
            session = f"GE{grade}"
            return render_template('view_exam.html', exams=exams, session=session)
        
        if "get_outline" in request.form:
            outlines = helpers.process_outline(db.execute("SELECT * FROM outline WHERE grade = ? ORDER BY class_date", grade))
            session = f"GO{grade}"
            return render_template('view_outline.html', outlines=outlines,session=session)
        
        if "get_timetable" in request.form:
            timetables = helpers.process_timetable(db.execute("SELECT * FROM timetable WHERE grade = ? ORDER BY class_date", grade))
            session = f"GT{grade}"
            return render_template('view_timetable.html', timetables=timetables, session=session)
        
        if "get_worksheet" in request.form:
            worksheets = helpers.process_worksheet(db.execute("SELECT * FROM worksheet WHERE grade = ? ORDER BY given_date", grade))
            session = f"GW{grade}"
            return render_template('view_worksheet.html', worksheets=worksheets, session=session)

        if "get_guest" in request.form:
            guests = helpers.process_guest(db.execute("SELECT * FROM guest WHERE grade = ? ORDER BY date_given", grade))
            session = f"GL{grade}"
            return render_template('view_guest.html', guests=guests, session=session)

        flash("Error, check VS Code for reason.")
        return redirect("/check_by_grade")


@app.route('/check_by_date', methods=['POST'])
def check_by_date():
    date = request.form["date"]

    if "get_homework" in request.form:
        assignments = helpers.process_homework(db.execute("SELECT * FROM homework WHERE due_date = ? ORDER BY grade", date))
        session = f"DH{date}"
        return render_template('view_homework.html', assignments=assignments, session=session)

    if "get_tests" in request.form:
        exams = helpers.process_exams(db.execute("SELECT * FROM exam WHERE exam_date = ? ORDER BY exam_time", date))
        session = f"DE{date}"
        return render_template('view_exam.html', exams=exams, session=session)

    if "get_outline" in request.form:
        outlines = helpers.process_outline(db.execute("SELECT * FROM outline WHERE class_date = ? ORDER BY grade", date))
        session = f"DO{date}"
        return render_template('view_outline.html', outlines=outlines,session=session)

    if "get_timetable" in request.form:
        timetables = helpers.process_timetable(db.execute("SELECT * FROM timetable WHERE class_date = ? ORDER BY start_time", date))
        session = f"DT{date}"
        return render_template('view_timetable.html', timetables=timetables, session=session)

    if "get_worksheet" in request.form:
        worksheets = helpers.process_worksheet(db.execute("SELECT * FROM worksheet WHERE given_date = ? ORDER BY title", date))
        session = f"GW{date}"
        return render_template('view_worksheet.html', worksheets=worksheets, session=session)

    if "get_guest" in request.form:
        guests = helpers.process_guest(db.execute("SELECT * FROM guest WHERE date_given = ? ORDER BY title", date))
        session = f"GL{date}"
        return render_template('view_guest.html', guests=guests, session=session)

    flash("Error, check VS Code for reason.")
    return redirect("/check_by_grade")



# TIMETABLE
@app.route("/timetable", methods=["GET", "POST"])
def timetable():
    if request.method == "GET":
        today = datetime.now().date().isoformat()
        timetables = helpers.process_timetable(db.execute("SELECT * FROM timetable WHERE class_date = ? ORDER BY start_time", today))
        session = f"DT{today}"

        return render_template("add_timetable.html", timetables=timetables, session=session, grades_dict=grades_dict, today=today)

    if request.method == "POST":
        grade = request.form["grade"]
        subject = request.form["subject"]
        class_date = request.form["class_date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        description = request.form['description']

        db.execute("INSERT INTO timetable (grade, subject, class_date, start_time, end_time, description) VALUES (?, ?, ?, ?, ?, ?)", grade, subject, class_date, start_time, end_time, description)
        flash("Added Successfully!")

        if "add_new" in request.form:
            return redirect("/timetable")
        
        if "add_message" in request.form:
            formatted_text = helpers.format_timetable(id)
            flash("Class Added Successfully!")
            return render_template("confirm_schedule_test.html", formatted_text=formatted_text)
        
        return redirect("/timetable")


@app.route("/delete_timetable", methods=["POST"])
def delete_timetable():
    timetable_id = request.form["id"]
    session = request.form["session"]

    db.execute("DELETE FROM timetable WHERE timetable_id = ?", timetable_id)

    if session[0] == "G":
        timetables = db.execute("SELECT * FROM timetable WHERE grade = ? ORDER BY start_time", session.removeprefix("GT"))
    if session[0] == "D":
        timetables = db.execute("SELECT * FROM timetable WHERE class_date = ? ORDER BY start_time", session.removeprefix("DT"))
    if session[0] == "A":
        timetables = db.execute("SELECT * FROM timetable ORDER BY start_time")

    timetables = helpers.process_timetable(timetables)

    flash("Deleted Successfully!")
    return render_template('view_timetable.html', timetables=timetables, session=session)


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

    if session[1] == "W":  
        worksheet = db.execute("SELECT * FROM worksheet WHERE worksheet_id = ? ", id)
        worksheet = helpers.process_worksheet(worksheet)
    
    if session[1] == "L":
        guest = db.execute("SELECT * FROM guest WHERE guest_id = ? ", id)
        guest = helpers.process_guest(guest)
        
    ##add backend for events



@app.route("/worksheet", methods=["GET", "POST"])
def add_worksheet():
    if request.method == "GET":
        today = datetime.now().date().isoformat()
        return render_template("add_worksheet.html", grades_dict=grades_dict, publications=publications, today=today)

    if request.method == "POST":
        publication = request.form["publication"].title()
        title = request.form["title"].title()
        given_date = request.form["given_date"]
        grade = request.form["grade"]
        subject = request.form["subject"]
        copies = request.form["copies"]
        notes = request.form["notes"]

        id = db.execute("INSERT INTO worksheet (publication, title, given_date, grade, subject, copies, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", publication, title, given_date, grade, subject, copies, notes)

        if "add_new" in request.form:
            return redirect("/worksheet")
        
        if "add_message" in request.form:
            formatted_text = helpers.format_worksheet(id)
            flash("Worksheet Issued Successfully!")
            return render_template("confirm_schedule_test.html", formatted_text=formatted_text)
        

@app.route("/delete_worksheet", methods=["POST"])
def delete_worksheet():
    worksheet_id = request.form["id"]
    session = request.form["session"]

    db.execute("DELETE FROM worksheet WHERE worksheet_id = ?", worksheet_id)

    if session[0] == "G":
        worksheets = db.execute("SELECT * FROM worksheet WHERE grade = ? ORDER BY start_time", session.removeprefix("GW"))
    if session[0] == "D":
        worksheets = db.execute("SELECT * FROM worksheet WHERE class_date = ? ORDER BY start_time", session.removeprefix("DW"))
    if session[0] == "A":
        worksheets = db.execute("SELECT * FROM worksheet ORDER BY start_time")

    worksheets = helpers.process_worksheet(worksheets)

    flash("Deleted Successfully!")
    return render_template('view_worksheet.html', worksheets=worksheets, table="worksheet", session=session)


@app.route("/guest_lecture", methods=["GET", "POST"])
def guest_lecture():
    if request.method == "GET":
        today = datetime.now().date().isoformat()
        return render_template("guest_lecture.html", today=today, grades_dict=grades_dict)

    if request.method == "POST":
        grade = request.form["grade"]
        date_given = request.form["date_given"]
        subject = request.form["subject"]
        duration = request.form["duration"]
        title = request.form["title"].title()
        description = request.form["description"]

        id = db.execute("INSERT INTO guest_lecture (grade, date_given, subject, duration, title, description) VALUES (?, ?, ?, ?, ?, ?)", grade, date_given, subject, duration, title, description)

        return redirect("/guest_lecture")


@app.route("/delete_guest", methods=["POST"])
def delete_guest():
    guest_id = request.form["id"]
    session = request.form["session"]

    db.execute("DELETE FROM guest WHERE guest_id = ?", guest_id)

    if session[0] == "G":
        guests = db.execute("SELECT * FROM guest WHERE grade = ? ORDER BY start_time", session.removeprefix("GL"))
    if session[0] == "D":
        guests = db.execute("SELECT * FROM guest WHERE class_date = ? ORDER BY start_time", session.removeprefix("DL"))
    if session[0] == "A":
        guests = db.execute("SELECT * FROM guest ORDER BY start_time")

    guests = helpers.process_guest(guests)

    flash("Deleted Successfully!")
    return render_template('view_guest.html', guests=guests, table="guest", session=session)



@app.route("/extra_class", methods=["GET", "POST"])
def extra_class():
    if request.method == "GET":
        today = datetime.now().date().isoformat()
        timetables = helpers.process_timetable(db.execute("SELECT * FROM timetable WHERE class_date = ? ORDER BY start_time", today))
        session = f"DT{today}"

        return render_template("add_extra_class.html", timetables=timetables, session=session, grades_dict=grades_dict, today=today)

    if request.method == "POST":
        grade = request.form["grade"]
        subject = request.form["subject"]
        class_date = request.form["class_date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        description = request.form['description']

        grade = grade + "(EC)"

        db.execute("INSERT INTO timetable (grade, subject, class_date, start_time, end_time, description) VALUES (?, ?, ?, ?, ?, ?)", grade, subject, class_date, start_time, end_time, description)
        flash("Added Successfully!")

        return redirect("/extra_class")


#Complete Lists
@app.route("/full_homework")
def full_homework():
    assignments = db.execute("SELECT * FROM homework ORDER BY due_date")
    assignments = helpers.process_homework(assignments)
    table = "homework"
    session = "AH"
    return render_template('view_homework.html', assignments=assignments, table=table, session=session)

@app.route("/full_exam")
def full_exam():
    exams  = db.execute("SELECT * FROM exam ORDER BY exam_date")
    exams = helpers.process_exams(exams)
    table = "exam"
    session = "AE"
    return render_template('view_exam.html', exams=exams, table=table, session=session)

@app.route("/full_report")
def full_report():
    outlines = db.execute("SELECT * FROM outline ORDER BY class_date")
    outlines = helpers.process_outline(outlines)
    table = "outline"
    session = "AO"
    return render_template('view_outline.html', outlines=outlines, table=table, session=session)


@app.route("/full_timetable")
def full_timetable():
    timetables = db.execute("SELECT * FROM timetable ORDER BY class_date DESC, start_time")
    timetables = helpers.process_timetable(timetables)
    table = "timetable"
    session = "AT"
    return render_template('view_timetable.html', timetables=timetables, table=table, session=session)

@app.route("/full_worksheet")
def full_worksheey():
    worksheets = db.execute("SELECT * FROM worksheet ORDER BY given_date")
    worksheets = helpers.process_worksheet(worksheets)
    table = "worksheet"
    session = "AW"
    return render_template('view_worksheet.html', worksheets=worksheets, table=table, session=session)

@app.route("/full_guest")
def full_guest():
    guests = db.execute("SELECT * FROM guest ORDER BY date_given")
    guests = helpers.process_guest(guests)
    table = "guest"
    session = "AL"
    return render_template('view_guest.html', guests=guests, table=table, session=session)


@app.route("/about")
def about():
    return render_template("about.html")


##button in test for done and cancelled
##edit button (homework, outline, test, timetable, worksheet, extra class)