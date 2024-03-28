from flask import Flask, flash, redirect, render_template, request, session, jsonify
from cs50 import SQL
from flask_session import Session
from datetime import datetime, timedelta
import uuid

#Logs every SQL command.(For Debugging)
#import logging
#logging.getLogger("cs50").disabled = False

import helpers
#import google_calander


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///homework_2024.db")
database = "homework_2024.db"


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



#grades = ["9BT1", "9BT2", "9MOR", "10BT1", "10BT2", "10BT3", "11MWF", "12MWF", "11AM"]
grades_dict = {"9BT1": "Class 9 Batch-1",
               "9BT2": "Class 9 Batch-2",
               "10BT1": "Class 10 Batch-1",
               "10BT2": "Class 10 Batch-2",
               "10BT3": "Class 10 Batch-3",
               "11MWF": "Class 11",
               "12MWF": "Class 12",
               "11AM": "Class 11 AM",
               "diya": "Diya",
               "neel": "Neel",
               }
subjects = ["Mathematics", "Science", "Mathematics and Science"]
publications = {"oswaal": "Oswaal Books",
               "abd": "ABD Publications",
            }


def create_table():
    db.execute("CREATE TABLE IF NOT EXISTS homework (homework_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, date_given DATE, due_date DATE, grade TEXT,subject TEXT, description TEXT, event_id TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS exam (exam_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, exam_date DATE, grade TEXT, exam_time TEXT, marks INTEGER, portion TEXT, subject TEXT, event_id TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS outline (outline_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, class_date DATE, grade TEXT, description TEXT, subject TEXT, event_id TEXT, time TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS timetable (timetable_id INTEGER PRIMARY KEY AUTOINCREMENT, grade TEXT, subject TEXT, class_date DATE, start_time TEXT, end_time TEXT, event_id TEXT, description TEXT, status TEXT)")
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

        return render_template('add_homework.html', grades_dict=grades_dict, today=today, homework=[])

    if request.method == 'POST':
        title = request.form['title'].title()
        date_given = request.form['date_given']
        due_date = request.form['due_date']
        grade = request.form['grade']
        subject = request.form['subject']
        description = request.form['description']


        id = db.execute(" INSERT INTO homework (title, date_given, due_date, grade, subject, description) VALUES (?, ?, ?, ?, ?, ?)",
                    title, date_given, due_date, grade, subject, description)
        
        flash('Homework assignment added successfully!')
        if "add_new" in request.form:
            return redirect("/add_homework")
        
        if "add_message" in request.form:
            formatted_text = helpers.format_homework(id)
            return render_template("confirm_schedule_test.html", formatted_text=formatted_text)


@app.route("/delete_homework", methods=["POST"])
def delete_homework():
    homework_id = request.form["id"]
    session = request.form["session"]

    db.execute("DELETE FROM homework WHERE homework_id = ?", homework_id)
    flash("Deleted Successfully!")

    assignments = helpers.homework_from_session(session)

    return render_template('view_homework.html', assignments=assignments, session=session)



#Schedule Tests
@app.route('/schedule_test', methods=["GET", "POST"])
def schedule_test():
    if request.method == "GET":
        today = datetime.now().date().isoformat()

        return render_template("add_exam.html", grades_dict=grades_dict, today=today, exam=[])

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

        flash("Exam Scheduled!")
        if "add_new" in request.form:
            return redirect("/schedule_test")
        
        if "add_message" in request.form:
            formatted_text = helpers.format_exam(id)
            return render_template("confirm_schedule_test.html", formatted_text=formatted_text)



@app.route("/delete_exam", methods=["POST"])
def delete_exam():
    exam_id = request.form["id"]
    session = request.form["session"]

    db.execute("DELETE FROM exam WHERE exam_id = ?", exam_id)

    exams = helpers.exam_from_session(session)

    flash("Deleted Successfully!")
    return render_template('view_exam.html', exams=exams, session=session)



@app.route("/exam_status")
def exam_status():
    id = request.args.get('id')
    status = request.args.get('status')
    session = request.args.get('session')

    if status == "done":
        db.execute("UPDATE exam SET status = 1 WHERE exam_id = ?", id)
    elif status == "cancel":
        db.execute("UPDATE exam SET status = -1 WHERE exam_id = ?", id)

    exams = helpers.exam_from_session(session)

    return render_template('view_exam.html', exams=exams, session=session)


# CLASS OUTLINE
@app.route("/class_outline", methods=["GET", "POST"])
def class_outline():
    if request.method == "GET":
        today = datetime.now().date().isoformat()

        return render_template("add_outline.html", grades_dict=grades_dict, today=today, outline=[])

    if request.method == "POST":
        title = request.form['title'].title()
        class_date = request.form['class_date']
        grade = request.form['grade']
        description = request.form['description']
        subject = request.form['subject']
        time = request.form['time']

        id = db.execute("INSERT INTO outline (title, class_date, grade, description, subject, time) VALUES (?, ?, ?, ?, ?, ?)", title, class_date, grade, description, subject, time)
        
        flash("Added Successfully")
        if "add_new" in request.form:
            return redirect("/class_outline")
        
        if "add_message" in request.form:
            formatted_text = helpers.format_outline(id)
            return render_template("confirm_schedule_test.html", formatted_text=formatted_text)
        

@app.route("/generate_outline", methods=["POST"])
def generate_outline():
    timetable_id = request.form["id"]

    timetables = db.execute("SELECT * FROM timetable WHERE timetable_id = ?", timetable_id)
    timetable = timetables[0]
    
    return render_template("generate_outline.html", timetable=timetable, grades_dict=grades_dict)


@app.route("/delete_outline", methods=["POST"])
def delete_outline():
    outline_id = request.form["id"]
    session = request.form["session"]

    db.execute("DELETE FROM outline WHERE outline_id = ?", outline_id)

    outlines = helpers.outline_from_session(session)

    flash("Deleted Successfully!")
    return render_template('view_outline.html', outlines=outlines, session=session)


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
        return render_template("add_timetable.html", timetables=timetables, session=session, grades_dict=grades_dict, today=today, timetable=[])

    if request.method == "POST":
        grade = request.form["grade"]
        subject = request.form["subject"]
        class_date = request.form["class_date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        description = request.form['description']
        status = 0

        id = db.execute("INSERT INTO timetable (grade, subject, class_date, start_time, end_time, description, status) VALUES (?, ?, ?, ?, ?, ?, ?)", grade, subject, class_date, start_time, end_time, description, status)

        if "add_new" in request.form:
            flash("Class Added Successfully!")
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

    if session == "add":
        return redirect("/timetable")

    timetables = helpers.timetable_from_session(session)

    flash("Deleted Successfully!")
    return render_template('view_timetable.html', timetables=timetables, session=session)



@app.route("/class_status")
def class_status():
    id = request.args.get('id')
    status = request.args.get('status')
    session = request.args.get('session')

    if status == "done":
        db.execute("UPDATE timetable SET status = 1 WHERE timetable_id = ?", id)
    elif status == "cancel":
        db.execute("UPDATE timetable SET status = -1 WHERE timetable_id = ?", id)

    timetables = helpers.timetable_from_session(session)

    return render_template('view_timetable.html', timetables=timetables, session=session)


@app.route("/add_event", methods=["POST"])
def add_event():
    id = request.form["id"]
    session = request.form["session"]

    event_id = str(uuid.uuid4()).replace("-", "")

    if session[1] == "H":
        assignment = db.execute("SELECT * FROM homework WHERE homework_id = ? ", id)
        assignment = assignment[0]

        timetables = db.execute("SELECT * FROM timetable WHERE grade = ? AND subject = ? AND class_date = ?", assignment["grade"], assignment["subject"], assignment["due_date"])
        
        if timetables:
            timetable = timetables[0]
            start_time = str(timetable["start_time"]) + ":00"
            end_time = str(timetable["end_time"]) + ":00"
        else:
            start_time = "06:00:00"
            end_time = "22:00:00"

        if assignment["grade"] in ["diya", "neel", "ansh", "sakshi", "vedant", "dhiya"]:
            location = "Private Tution"
        else:
            location = "Shiv Apartment"

        event_status = google_calander.add_event(
            id=event_id,
            start_date=assignment["due_date"],
            start_time=start_time,
            end_date=assignment["due_date"],
            end_time=end_time,
            summary=(grades_dict[assignment["grade"]] + assignment["title"]),
            location=location,
            description=assignment["description"],
        )

        if event_status == 0:
            db.execute("UPDATE homework SET event_id = ? WHERE homework_id = ?", event_id, id)
            flash("Event Added Succeessfully!")
        else:
            flash(f"Event Not Added. Error: {event_status}")

        assignments = helpers.homework_from_session(session)

        return render_template('view_homework.html', assignments=assignments, session=session)

    if session[1] == "E":
        exam = db.execute("SELECT * FROM exam WHERE exam_id = ? ", id)
        exam = exam[0]

        start_time = str(exam["exam_time"]) + ":00"
        end_time = helpers.add_timedelta_to_time(exam["exam_time"], 120)

        if exam["grade"] in ["diya", "neel", "sakshi", "vedant", "dhiya"]:
            location = "Private Tution"
        else:
            location = "Shiv Apartment"

        event_status = google_calander.add_event(
            id=event_id,
            start_date=exam["exam_date"],
            start_time=start_time,
            end_date=exam["exam_date"],
            end_time=end_time,
            summary=f'{grades_dict[exam["grade"]]}: {exam["title"]} (Marks: {exam["marks"]})',
            location=location,
            description=exam["portion"],
        )

        if event_status == 0:
            db.execute("UPDATE exam SET event_id = ? WHERE exam_id = ?", event_id, id)
            flash("Event Added Succeessfully!")
        else:
            flash(f"Event Not Added. Error: {event_status}")

        exams = helpers.exam_from_session(session)

        return render_template('view_exam.html', exams=exams, session=session)


    if session[1] == "T":
        timetable = db.execute("SELECT * FROM timetable WHERE timetable_id = ? ", id)
        timetable = timetable[0]

        start_time = str(timetable["start_time"]) + ":00"
        end_time = str(timetable["end_time"]) + ":00"

        if timetable["grade"] in ["diya", "neel", "sakshi", "vedant", "dhiya"]:
            location = "Private Tution"
        else:
            location = "Shiv Apartment"

        event_status = google_calander.add_event(
            id=event_id,
            start_date=timetable["class_date"],
            start_time=start_time,
            end_date=timetable["class_date"],
            end_time=end_time,
            summary=timetable["grade"],
            location=location,
            description=timetable["description"],
        )

        if event_status == 0:
            db.execute("UPDATE timetable SET event_id = ? WHERE timetable_id = ?", event_id, id)
            flash("Event Added Succeessfully!")
        else:
            flash(f"Event Not Added. Error: {event_status}")

        timetables = helpers.timetable_from_session(session)

        return render_template('view_timetable.html', timetables=timetables, session=session)

    #Not Required
    #if session[1] == "W":  
        #worksheet = db.execute("SELECT * FROM worksheet WHERE worksheet_id = ? ", id)
        #worksheet = worksheet[0]
    
    if session[1] == "L":
        guest = db.execute("SELECT * FROM guest WHERE guest_id = ? ", id)
        guest = guest[0]

        start_time = "06:00:00"
        end_time = "22:00:00"

        location = "Shiv Apartment"

        event_status = google_calander.add_event(
            id=event_id,
            start_date=guest["date_given"],
            start_time=start_time,
            end_date=guest["date_given"],
            end_time=end_time,
            summary=f'{grades_dict[guest["grade"]]}: {guest["title"]})',
            location=location,
            description=guest["description"],
        )

        if event_status == 0:
            db.execute("UPDATE guest SET event_id = ? WHERE guest_id = ?", event_id, id)
            flash("Event Added Succeessfully!")
        else:
            flash(f"Event Not Added. Error: {event_status}")

        guests = helpers.guest_from_session(session)

        return render_template('view_guest.html', guests=guests, session=session)


    #Not Required
    """
    if session[1] == "O":
        outline = db.execute("SELECT * FROM outline WHERE outline_id = ? ", id)
        outline = outline[0]
        
        start_time = str(outline["time"]) + ":00"

        timetables = db.execute("SELECT * FROM timetable WHERE grade = ? AND subject = ? AND class_date = ?", assignment["grade"], assignment["subject"], assignment["due_date"])
        
        if timetables:
            timetable = timetables[0]
            end_time = str(timetable["end_time"]) + ":00"
        else:
            end_time = "22:00:00"

        if outline["grade"] in ["diya", "neel", "sakshi", "vedant", "dhiya"]:
            location = "Private Tution"
        else:
            location = "Shiv Apartment"

        event_status = google_calander.add_event(
            id=event_id,
            start_date=outline["class_date"],
            start_time=start_time,
            end_date=outline["class_date"],
            end_time=end_time,
            summary=f'{grades_dict[outline["grade"]]}: {outline["title"]})',
            location=location,
            description=outline["description"],
        )

        if event_status == 0:
            db.execute("UPDATE outline SET event_id = ? WHERE outline_id = ?", event_id, id)
            flash("Event Added Succeessfully!")
        else:
            flash(f"Event Not Added. Error: {event_status}")

        outlines = helpers.outline_from_session(session)

        return render_template('view_outline.html', outlines=outlines, session=session)
        """



@app.route("/delete_event", methods=["POST"])
def delete_event():
    id = request.form["id"]
    session = request.form["session"]

    if session[1] == "H":
        event_id = db.execute("SELECT event_id FROM homework WHERE homework_id = ?", id)
        event_id = event_id[0]

        event_status = google_calander.delete_event(event_id["event_id"])

        if event_status == 0:
            db.execute("UPDATE homework SET event_id = ? WHERE homework_id = ?", "", id)
            flash("Event Deleted Succeessfully!")
        else:
            flash(f"Event Not Deleted. Error: {event_status}")

        assignments = helpers.homework_from_session(session)

        return render_template('view_homework.html', assignments=assignments, session=session)

    if session[1] == "E":
        event_id = db.execute("SELECT event_id FROM exam WHERE exam_id = ? ", id)
        event_id = event_id[0]

        event_status = google_calander.delete_event(event_id["event_id"])

        if event_status == 0:
            db.execute("UPDATE exam SET event_id = ? WHERE exam_id = ?", "", id)
            flash("Event Deleted Succeessfully!")
        else:
            flash(f"Event Not Deleted. Error: {event_status}")

        exams = helpers.exam_from_session(session)

        return render_template('view_exam.html', exams=exams, session=session)

    if session[1] == "T":
        event_id = db.execute("SELECT * FROM timetable WHERE timetable_id = ?", id)
        event_id = event_id[0]

        event_status = google_calander.delete_event(event_id["event_id"])

        if event_status == 0:
            db.execute("UPDATE timetable SET event_id = ? WHERE timetable_id = ?", "", id)
            flash("Event Deleted Succeessfully!")
        else:
            flash(f"Event Not Deleted. Error: {event_status}")

        timetables = helpers.timetable_from_session(session)

        return render_template('view_timetable.html', timetables=timetables, session=session)

    if session[1] == "L":
        event_id = db.execute("SELECT * FROM guest WHERE guest_id = ? ", id)
        event_id = event_id[0]

        event_status = google_calander.delete_event(event_id["event_id"])

        if event_status == 0:
            db.execute("UPDATE guest SET event_id = ? WHERE guest_id = ?", "", id)
            flash("Event Deleted Succeessfully!")
        else:
            flash(f"Event Not Deleted. Error: {event_status}")

        guests = helpers.guest_from_session(session)

        return render_template('view_guest.html', guests=guests, session=session)

#Not Required
    """
    if session[1] == "O":
        event_id = db.execute("SELECT event_id FROM outline WHERE outline_id = ? ", id)
        event_id = event_id[0]

        event_status = google_calander.delete_event(event_id["event_id"])

        if event_status == 0:
            db.execute("UPDATE outline SET event_id = ? WHERE outline_id = ?", "", id)
            flash("Event Deleted Succeessfully!")
        else:
            flash(f"Event Not Deleted. Error: {event_status}")

        outlines = helpers.outline_from_session(session)

        return render_template('view_outline.html', outlines=outlines, session=session)
    """


    #Not Required
    """
    if session[1] == "W":
        event_id = db.execute("SELECT * FROM worksheet WHERE worksheet_id = ? ", id)
        event_id = event_id[0]

        event_status = google_calander.delete_event(event_id["event_id"])

        if event_status == 0:
            db.execute("UPDATE worksheet SET event_id = ? WHERE worksheet_id = ?", "", id)
            flash("Event Deleted Succeessfully!")
        else:
            flash(f"Event Not Deleted. Error: {event_status}")

        worksheets = helpers.worksheet_from_session(session)

        return render_template('view_worksheet.html', worksheets=worksheets, session=session)
    """


@app.route("/worksheet", methods=["GET", "POST"])
def add_worksheet():
    if request.method == "GET":
        today = datetime.now().date().isoformat()
        return render_template("add_worksheet.html", grades_dict=grades_dict, publications=publications, today=today, worksheet=[])

    if request.method == "POST":
        publication = request.form["publication"].title()
        title = request.form["title"].title()
        given_date = request.form["given_date"]
        grade = request.form["grade"]
        subject = request.form["subject"]
        copies = request.form["copies"]
        notes = request.form["notes"]

        id = db.execute("INSERT INTO worksheet (publication, title, given_date, grade, subject, copies, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", publication, title, given_date, grade, subject, copies, notes)

        flash("Worksheet Issued Successfully!")
        if "add_new" in request.form:
            return redirect("/worksheet")
        
        if "add_message" in request.form:
            formatted_text = helpers.format_worksheet(id)
            return render_template("confirm_schedule_test.html", formatted_text=formatted_text)
        

@app.route("/delete_worksheet", methods=["POST"])
def delete_worksheet():
    worksheet_id = request.form["id"]
    session = request.form["session"]

    db.execute("DELETE FROM worksheet WHERE worksheet_id = ?", worksheet_id)

    worksheets = helpers.worksheet_from_session(session)

    flash("Deleted Successfully!")
    return render_template('view_worksheet.html', worksheets=worksheets, session=session)


@app.route("/guest_lecture", methods=["GET", "POST"])
def guest_lecture():
    if request.method == "GET":
        today = datetime.now().date().isoformat()
        return render_template("add_guest_lecture.html", today=today, grades_dict=grades_dict, guest=[])

    if request.method == "POST":
        grade = request.form["grade"]
        date_given = request.form["date_given"]
        subject = request.form["subject"]
        duration = request.form["duration"]
        title = request.form["title"].title()
        description = request.form["description"]

        id = db.execute("INSERT INTO guest_lecture (grade, date_given, subject, duration, title, description) VALUES (?, ?, ?, ?, ?, ?)", grade, date_given, subject, duration, title, description)

        flash("Guest Lecture Added Successfully!")
        if "add_new" in request.form:
            return redirect("/guest_lecture")
        
        if "add_message" in request.form:
            formatted_text = helpers.format_guest(id)
            return render_template("confirm_schedule_test.html", formatted_text=formatted_text)



@app.route("/delete_guest", methods=["POST"])
def delete_guest():
    guest_id = request.form["id"]
    session = request.form["session"]

    db.execute("DELETE FROM guest WHERE guest_id = ?", guest_id)

    guests = helpers.guest_from_session(session)

    flash("Deleted Successfully!")
    return render_template('view_guest.html', guests=guests, session=session)



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
        status = 0

        grade = grade + "(EC)"

        db.execute("INSERT INTO timetable (grade, subject, class_date, start_time, end_time, description, status) VALUES (?, ?, ?, ?, ?, ?)", grade, subject, class_date, start_time, end_time, description, status)
        flash("Added Successfully!")

        return redirect("/extra_class")


#Complete Lists
@app.route("/full_homework")
def full_homework():
    assignments = db.execute("SELECT * FROM homework ORDER BY due_date DESC")
    assignments = helpers.process_homework(assignments)
    session = "AH"
    return render_template('view_homework.html', assignments=assignments, session=session)

@app.route("/full_exam")
def full_exam():
    exams  = db.execute("SELECT * FROM exam ORDER BY exam_date DESC")
    exams = helpers.process_exams(exams)
    session = "AE"
    return render_template('view_exam.html', exams=exams, session=session)

@app.route("/full_report")
def full_report():
    outlines = db.execute("SELECT * FROM outline ORDER BY class_date DESC")
    outlines = helpers.process_outline(outlines)
    session = "AO"
    return render_template('view_outline.html', outlines=outlines, session=session)

@app.route("/full_timetable")
def full_timetable():
    timetables = db.execute("SELECT * FROM timetable ORDER BY class_date DESC, start_time")
    timetables = helpers.process_timetable(timetables)
    session = "AT"
    return render_template('view_timetable.html', timetables=timetables, session=session)

@app.route("/full_worksheet")
def full_worksheet():
    worksheets = db.execute("SELECT * FROM worksheet ORDER BY given_date DESC")
    worksheets = helpers.process_worksheet(worksheets)
    session = "AW"
    return render_template('view_worksheet.html', worksheets=worksheets, session=session)

@app.route("/full_guest")
def full_guest():
    guests = db.execute("SELECT * FROM guest ORDER BY date_given DESC")
    guests = helpers.process_guest(guests)
    session = "AL"
    return render_template('view_guest.html', guests=guests, session=session)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/edit_data", methods=["POST"])
def edit_data():
    id = request.form['id']
    session = request.form['session']

    if session[1] == "H":
        homework = db.execute("SELECT * FROM homework WHERE homework_id = ?", id)
        homework = homework[0]

        return render_template('add_homework.html', grades_dict=grades_dict, today=homework["date_given"], homework=homework, session=session)

    if session[1] == "E":
        exam = db.execute("SELECT * FROM exam WHERE exam_id = ?", id)
        exam = exam[0]

        return render_template("add_exam.html", grades_dict=grades_dict, today=exam["exam_date"], exam=exam, session=session)

    if session[1] == "O":
        outline = db.execute("SELECT * FROM outline WHERE outline_id = ?", id)
        outline = outline[0]

        return render_template("add_outline.html", grades_dict=grades_dict, today=outline["class_date"], outline=outline, session=session)

    if session[1] == "T":
        timetable = db.execute("SELECT * FROM timetable WHERE timetable_id = ?", id)
        timetable = timetable[0]

        timetables = helpers.timetable_from_session(session)

        return render_template("add_timetable.html", timetables=timetables, session=session, grades_dict=grades_dict, today=timetable["class_date"], timetable=timetable)
    
    if session[1] == "W":
        worksheet = db.execute("SELECT * FROM worksheet WHERE worksheet_id = ?", id)
        worksheet = worksheet[0]

        return render_template("add_worksheet.html", grades_dict=grades_dict, publications=publications, today=worksheet["given_date"], worksheet=worksheet, session=session)

    if session[1] == "L":
        guest = db.execute("SELECT * FROM guest WHERE guest_id = ?", id)
        guest = guest[0]

        return render_template("add_guest_lecture.html", today=guest["date_given"], grades_dict=grades_dict, guest=guest, session=session)


@app.route("/change_data", methods=["POST"])
def change_data():
    id = request.form["id"]
    session = request.form["session"]
    
    if session[1] == "H":
        title = request.form['title'].title()
        date_given = request.form['date_given']
        due_date = request.form['due_date']
        grade = request.form['grade']
        subject = request.form['subject']
        description = request.form['description']

        db.execute("UPDATE homework SET title=?, date_given=?, due_date=?, grade=?, subject=?, description=? WHERE homework_id = ?", title, date_given, due_date, grade, subject, description, id)

        flash("Homework Updated Successfully!")
        if "add_new" in request.form:
            return redirect("/add_homework")
        
        if "add_message" in request.form:
            formatted_text = helpers.format_homework(id)
            return render_template("confirm_schedule_test.html", formatted_text=formatted_text)


    if session[1] == "E":
        title = request.form['title'].title()
        exam_date = request.form['exam_date']
        grade = request.form['grade']
        exam_time = request.form['exam_time']
        marks = request.form['marks']
        portion = request.form['portion'].capitalize()
        subject = request.form['subject']

        db.execute("UPDATE exam SET title=?, exam_date=?, grade=?, exam_time=?, marks=?, portion=?, subject=? WHERE exam_id = ?", title, exam_date, grade, exam_time, marks, portion, subject, id)

        flash("Exam Updated Successfully!")
        if "add_new" in request.form:
            return redirect("/schedule_test")
        
        if "add_message" in request.form:
            formatted_text = helpers.format_exam(id)
            return render_template("confirm_schedule_test.html", formatted_text=formatted_text)


    if session[1] == "O":
        title = request.form['title'].title()
        class_date = request.form['class_date']
        grade = request.form['grade']
        description = request.form['description']
        subject = request.form['subject']
        time = request.form['time']

        db.execute("UPDATE outline SET title=?, class_date=?, grade=?, description=?, subject=?, time=? WHERE outline_id = ?", title, class_date, grade, description, subject, time, id)

        flash("Report Updated Successfully!")
        if "add_new" in request.form:
            return redirect("/class_outline")
        
        if "add_message" in request.form:
            formatted_text = helpers.format_outline(id)
            return render_template("confirm_schedule_test.html", formatted_text=formatted_text)

    if session[1] == "T":
        grade = request.form["grade"]
        subject = request.form["subject"]
        class_date = request.form["class_date"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        description = request.form['description']
        status = 0

        db.execute("UPDATE timetable SET grade=?, subject=?, class_date=?, start_time=?, end_time=?, description=?, status=? WHERE timetable_id = ?", grade, subject, class_date, start_time, end_time, description, status, id)

        flash("Class Updated Successfully!")
        if "add_new" in request.form:
            return redirect("/timetable")
        
        if "add_message" in request.form:
            formatted_text = helpers.format_timetable(id)
            return render_template("confirm_schedule_test.html", formatted_text=formatted_text)
    
    if session[1] == "W":
        publication = request.form["publication"].title()
        title = request.form["title"].title()
        given_date = request.form["given_date"]
        grade = request.form["grade"]
        subject = request.form["subject"]
        copies = request.form["copies"]
        notes = request.form["notes"]

        db.execute("UPDATE worksheet SET publication=?, title=?, given_date=?, grade=?, subject=?, copies=?, notes=? WHERE worksheet_id = ?", publication, title, given_date, grade, subject, copies, notes, id)

        flash("Worksheet Updated Successfully!")
        if "add_new" in request.form:
            return redirect("/worksheet")
        
        if "add_message" in request.form:
            formatted_text = helpers.format_worksheet(id)
            return render_template("confirm_schedule_test.html", formatted_text=formatted_text)

    if session[1] == "L":
        grade = request.form["grade"]
        date_given = request.form["date_given"]
        subject = request.form["subject"]
        duration = request.form["duration"]
        title = request.form["title"].title()
        description = request.form["description"]

        db.execute("UPDATE guest SET grade=?, date_given=?, subject=?, duration=?, title=?, description=? WHERE guest_id = ?", grade, date_given, subject, duration, title, description, id)

        flash("Guest Lecture Updated Successfully!")
        if "add_new" in request.form:
            return redirect("/guest_lecture")
        
        if "add_message" in request.form:
            formatted_text = helpers.format_guest(id)
            return render_template("confirm_schedule_test.html", formatted_text=formatted_text)

