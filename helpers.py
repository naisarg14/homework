from datetime import datetime, timedelta
from cs50 import SQL

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
               "bhawna": "Bhawna Teacher",
               }
database = "homework_2024.db"
name = "Bhawna Teacher"


def process_time(time_str):
    try:
        time_obj = datetime.strptime(time_str, "%H:%M")
        formatted_time = time_obj.strftime("%I:%M %p")
        return formatted_time
    except:
        pass
    return "None"


def process_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d %B %Y")
        return formatted_date
    except:
        pass
    return "None"


def process_text(text):
    text = str(text)
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace("&", "&lamp;")
    text = text.replace("\"", "&quot;")
    text = text.replace("\'", "&apos;")
    
    return text


def process_homework(assignments):
    for assignment in assignments:
        assignment["grade"] = grades_dict[assignment["grade"]]
        assignment["date_given"] = process_date(assignment["date_given"])
        assignment["due_date"] = process_date(assignment["due_date"])

        assignment["title"] = process_text(assignment["title"])
        assignment["description"] = process_text(assignment["description"])
    return assignments


def process_exams(exams):
    for exam in exams:
        exam["grade"] = grades_dict[exam["grade"]]
        exam["exam_time"] = process_time(exam["exam_time"])
        exam["exam_date"] = process_date(exam["exam_date"])

        exam["title"] = process_text(exam["title"])
        exam["portion"] = process_text(exam["portion"])
    return exams


def process_outline(outlines):
    for outline in outlines:
        outline["grade"] = grades_dict[outline["grade"]]
        outline["class_date"] = process_date(outline["class_date"])
        outline["time"] = process_time(outline["time"])

        outline["title"] = process_text(outline["title"])
        outline["description"] = process_text(outline["description"])
    return outlines


def process_timetable(timetables):
    for timetable in timetables:
        try:
            timetable["grade"] = grades_dict[timetable["grade"]]
        except Exception:
            pass
        timetable["class_date"] = process_date(timetable["class_date"])
        timetable["start_time"] = process_time(timetable["start_time"])
        timetable["end_time"] = process_time(timetable["end_time"])

        timetable["grade"] = process_text(timetable["grade"])
        timetable["description"] = process_text(timetable["description"])
    return timetables


def process_worksheet(worksheets):
    for worksheet in worksheets:
        worksheet["grade"] = grades_dict[worksheet["grade"]]
        worksheet["given_date"] = process_date(worksheet["given_date"])

        worksheet["title"] = process_text(worksheet["title"])
        worksheet["publication"] = process_text(worksheet["publication"])
        worksheet["notes"] = process_text(worksheet["notes"])
    return worksheets


def process_guest(guest_lecture):
    for guest in guest_lecture:
        guest["grade"] = grades_dict[guest["grade"]]
        guest["date_given"] = process_date(guest["date_given"])

        guest["title"] = process_text(guest["title"])
        guest["description"] = process_text(guest["description"])
    return guest_lecture


def format_homework(id):
    db = SQL(f"sqlite:///{database}")
    assignments = db.execute("SELECT * FROM homework WHERE homework_id = ? ", id)
    assignments = process_homework(assignments)
    assignment = assignments[0]
    title = "Homework Schedule"
    schedule = f'Isucceed Coaching Class-Homework Schedule\nTitle: {assignment["title"]}\nClass: {assignment["grade"]}\nSubject: {assignment["subject"]}\nDescription: {assignment["description"]}\nDue Date: {assignment["due_date"]}\n{name}'
    return (title, schedule)


def format_exam(id):
    db = SQL(f"sqlite:///{database}")
    exams = db.execute("SELECT * FROM exam WHERE exam_id = ?", id)
    exams = process_exams(exams)
    exam = exams[0]
    title = "Exam Schedule"
    schedule = f'Isucceed Coaching Class-Exam Schedule\nTitle: {exam["title"]}\nClass: {exam["grade"]}\nSubject: {exam["subject"]}\nPortion: {exam["portion"]}\nDate: {exam["exam_date"]}\nTime: {exam["exam_time"]}\nMarks: {exam["marks"]}\n{name}'
    return (title, schedule)


def format_outline(id):
    db = SQL(f"sqlite:///{database}")
    outlines = db.execute("SELECT * FROM outline WHERE outline_id = ?", id)
    outlines = process_outline(outlines)
    outline = outlines[0]
    title = "Class Outline"
    schedule = f'Isucceed Coaching Class-Class Outline\nTitle: {outline["title"]}\nClass: {outline["grade"]}Time: {outline["time"]}\nSubject: {outline["subject"]}\nDescription: {outline["description"]}\nDate: {outline["class_date"]}\n{name}'
    return (title, schedule)


def format_timetable(id):
    db = SQL(f"sqlite:///{database}")
    timetables = db.execute("SELECT * FROM timetable WHERE timetable_id = ?", id)
    timetables = process_timetable(timetables)
    timetable = timetables[0]
    title = "Class Schedule"
    schedule = f'Isucceed Coaching Class-Class Schedule\nClass: {timetable["grade"]}\nSubject: {timetable["subject"]}\nDate: {timetable["class_date"]}\nTime: {timetable["start_time"]} - {timetable["end_time"]}\n{name}'
    return (title, schedule)


def format_worksheet(id):
    db = SQL(f"sqlite:///{database}")
    worksheets = db.execute("SELECT * FROM worksheet WHERE worksheet_id = ?", id)
    worksheets = process_worksheet(worksheets)
    worksheet = worksheets[0]
    title = "Worksheet Issued"
    schedule = f'Isucceed Coaching Class-Worksheet Record Schedule\nTitle: {worksheet["title"]}\nClass: {worksheet["grade"]}\nSubject: {worksheet["subject"]}\nDate: {worksheet["given_date"]}\nCopies: {worksheet["copies"]}\nNotes: {worksheet["notes"]}\n{name}'
    return (title, schedule)


def format_guest(id):
    db = SQL(f"sqlite:///{database}")
    guests = db.execute("SELECT * FROM guest WHERE guest_id = ?", id)
    guests = process_guest(guests)
    guest = guests[0]
    title = "Guest Lecture"
    schedule = f'Isucceed Coaching Class-Guest Lecture\nTitle: {guest["title"]}\nClass: {guest["grade"]}\nSubject: {guest["subject"]}\nDate: {guest["date_given"]}\nDuration: {guest["duration"]}\nDescription: {guest["description"]}\n{name}'
    return (title, schedule)


def homework_from_session(session):
    db = SQL(f"sqlite:///{database}")
    if session[0] == "I":
        assignments = db.execute("SELECT * FROM homework WHERE homework_id = ?", session.removeprefix("IH"))
    elif session[0] == "G":
        assignments = db.execute("SELECT * FROM homework WHERE grade = ? ORDER BY due_date DESC", session.removeprefix("GH"))
    elif session[0] == "D":
        assignments = db.execute("SELECT * FROM homework WHERE due_date = ? ORDER BY grade", session.removeprefix("DH"))
    elif session[0] == "A":
        assignments = db.execute("SELECT * FROM homework ORDER BY due_date DESC")

    assignments = process_homework(assignments)

    return assignments


def exam_from_session(session):
    db = SQL(f"sqlite:///{database}")
    if session[0] == "I":
        exams = db.execute("SELECT * FROM exam WHERE exam_id = ?", session.removeprefix("IE"))
    elif session[0] == "G":
        exams = db.execute("SELECT * FROM exam WHERE grade = ? ORDER BY exam_date DESC", session.removeprefix("GE"))
    elif session[0] == "D":
        exams = db.execute("SELECT * FROM exam WHERE exam_date = ? ORDER BY grade", session.removeprefix("DE"))
    elif session[0] == "A":
        exams = db.execute("SELECT * FROM exam ORDER BY exam_date DESC")

    exams = process_exams(exams)

    return exams


def outline_from_session(session):
    db = SQL(f"sqlite:///{database}")
    if session[0] == "I":
        outlines = db.execute("SELECT * FROM outline WHERE outline_id = ?", session.removeprefix("IO"))
    elif session[0] == "G":
        outlines = db.execute("SELECT * FROM outline WHERE grade = ? ORDER BY class_date DESC", session.removeprefix("GO"))
    elif session[0] == "D":
        outlines = db.execute("SELECT * FROM outline WHERE class_date = ? ORDER BY grade", session.removeprefix("DO"))
    elif session[0] == "A":
        outlines = db.execute("SELECT * FROM outline ORDER BY class_date DESC")

    outlines = process_outline(outlines)

    return outlines


def timetable_from_session(session):
    db = SQL(f"sqlite:///{database}")
    if session[0] == "I":
        timetables = db.execute("SELECT * FROM timetable WHERE timetable_id = ?", session.removeprefix("IT"))
    elif session[0] == "G":
        timetables = db.execute("SELECT * FROM timetable WHERE grade = ? ORDER BY class_date DESC", session.removeprefix("GT"))
    elif session[0] == "D":
        timetables = db.execute("SELECT * FROM timetable WHERE class_date = ? ORDER BY start_time", session.removeprefix("DT"))
    elif session[0] == "A":
        timetables = db.execute("SELECT * FROM timetable ORDER BY class_date DESC, start_time")

    timetables = process_timetable(timetables)
    
    return timetables


def worksheet_from_session(session):
    db = SQL(f"sqlite:///{database}")
    if session[0] == "I":
        worksheets = db.execute("SELECT * FROM worksheet WHERE worksheet_id = ?", session.removeprefix("IW"))
    elif session[0] == "G":
        worksheets = db.execute("SELECT * FROM worksheet WHERE grade = ? ORDER BY given_date", session.removeprefix("GW"))
    elif session[0] == "D":
        worksheets = db.execute("SELECT * FROM worksheet WHERE given_date = ? ORDER BY grade", session.removeprefix("DW"))
    elif session[0] == "A":
        worksheets = db.execute("SELECT * FROM worksheet ORDER BY given_date")

    worksheets = process_worksheet(worksheets)

    return worksheets

def guest_from_session(session):
    db = SQL(f"sqlite:///{database}")
    if session[0] == "I":
        guests = db.execute("SELECT * FROM guest WHERE guest_id = ?", session.removeprefix("IL"))
    elif session[0] == "G":
        guests = db.execute("SELECT * FROM guest WHERE grade = ? ORDER BY date_given DESC", session.removeprefix("GL"))
    elif session[0] == "D":
        guests = db.execute("SELECT * FROM guest WHERE class_date = ? ORDER BY grade", session.removeprefix("DL"))
    elif session[0] == "A":
        guests = db.execute("SELECT * FROM guest ORDER BY date_given DESC")

    guests = process_guest(guests)

    return guests


def add_timedelta_to_time(time, delta):
    datetime_time = datetime.strptime(time, "%H:%M")
    time_delta = timedelta(minutes=delta)
    
    new_time = datetime_time + time_delta
    result = new_time.strftime("%H:%M")

    return result