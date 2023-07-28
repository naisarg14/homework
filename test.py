import uuid
import google_calander
from cs50 import SQL

# unique_id = str(uuid.uuid4()).replace("-", "")
# print(unique_id)
"""print(
    google_calander.add_event(
        id=unique_id,
        start_date="2023-07-28",
        start_time="11:00:00",
        end_date="2023-07-28",
        end_time="13:00:00",
        summary="test&test",
        location="hogwards",
        description="timepassispasstime",
    )
)

print(google_calander.delete_event("dd901e23505e41ca9642780fb7fd286c"))
"""
db = SQL("sqlite:///homework.db")
assignment = db.execute("SELECT * FROM homework WHERE homework_id = ? ", 2)
assignment = assignment[0]
timetables = db.execute(
    "SELECT * FROM timetable WHERE grade = ? AND subject = ? AND class_date = ?",
    assignment["grade"],
    assignment["subject"],
    assignment["due_date"],
)

if timetables:
    print("ok")
else:
    print("not ok")
