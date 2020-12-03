import atexit
import os
import sqlite3
import sys



# The Repository
class _Repository:
    def __init__(self):
        self._conn = sqlite3.connect('schedule.db')
        # self.students = _Students(self._conn)
        # self.assignments = _Assignments(self._conn)
        # self.grades = _Grades(self._conn)

    def _close(self):
        self._conn.commit()
        self._conn.close()

    def create_tables(self):
        self._conn.executescript("""
        

        CREATE TABLE students (
            grade                   TEXT         PRIMARY KEY,
            count                   INTEGER        NOT NULL
        );

        CREATE TABLE classrooms (
            id                      INTEGER     PRIMARY KEY,
            location                TEXT        NOT NULL,
            current_course_id       INTEGER     NOT NULL,
            current_course_time_left INTEGER    NOT NULL
        );

        CREATE TABLE courses (
            id                      INTEGER     PRIMARY KEY ,
            course_name             TEXT        NOT NULL,
            student                 TEXT        NOT NULL,
            number_of_students      INTEGER     NOT NULL,
            class_id                INTEGER     NOT NULL,
            course_length           INTEGER     NOT NULL,
			
			FOREIGN KEY(class_id) REFERENCES classrooms(id)


        );
    """)



##########student_group DTA AND DTO ##############

class student_group:
    def __init__(self, grade, count):
        self.grade = grade
        self.count = count

    def print(self):
        print("{},{}".format(self.grade, self.count))


class _student_groups:
    def __init__(self, conn):
        self._conn = conn


    def insert(self,student_group):
        self._conn.execute("""
               INSERT INTO students (grade, count) VALUES (?, ?)
           """, [student_group.grade, student_group.count])

    def get_all(self):
        c = self._conn.cursor()
        c.execute("""
            SELECT * FROM students
        """)
        return c.fetchall()


##########classroom DTA AND DTO ##############

class classroom:

    # constructor for reading from SQLITE db.
    # if current_course_id and current_course_time_left are not passed as parameters, put default value 0.
    # if they are passed as values, then copy those values as usuall.
    def __init__(self, id, location,current_course_id=0,current_course_time_left=0):
        self.id, = id
        self.location = location
        self.current_course_id = current_course_id
        self.current_course_time_left = current_course_time_left


class _classrooms:
    def __init__(self, conn):
        self._conn = conn


    def insert(self,classroom):
        self._conn.execute("""
               INSERT INTO classrooms (id,location,current_course_id,current_course_time_left) VALUES (?, ?, ?, ?)
           """, [classroom.id, classroom.location,classroom.current_course_id,classroom.current_course_time_left])


    def get_all(self):
        c = self._conn.cursor()
        c.execute("""
            SELECT * FROM classrooms
        """)
        return c.fetchall()


##########Course DTA AND DTO ##############


class course:
    def __init__(self, id, course_name,student,number_of_students,class_id,course_length) :
        self.id = id
        self.course_name = course_name
        self.student = student
        self.number_of_students = number_of_students
        self.class_id = class_id
        self.course_length = course_length



class _courses:
    def __init__(self, conn):
        self._conn = conn


    def insert(self,course):
        self._conn.execute("""
               INSERT INTO courses (id,course_name,student,number_of_students,class_id,course_length ) VALUES (?, ?, ?, ?, ?, ?)
           """, [course.id, course.course_name,course.student,course.number_of_students,course.class_id,course.course_length])

    def get_all(self):
        c = self._conn.cursor()
        c.execute("""
            SELECT * FROM courses
        """)
        return c.fetchall()








def formatAndInsert(line):
    line = line.split(',')
    line = [word.strip() for word in line]  # remove leading and trailing whitespaces
    if line[0] == 'S':
        student_group_Object = student_group(*line[1:])
        students.insert(student_group_Object)
    elif line[0] == 'R':
        classroomObject = classroom(*line[1:])
        rooms.insert(classroomObject)
    else:
        courseObject = course(*line[1:])
        courses.insert(courseObject)



def printPostInsertion(cours,rooms,students):
    print("courses")
    list = cours.get_all()
    [print(row) for row in list]
    print("classrooms")
    list = rooms.get_all()
    [print(row) for row in list]
    print("students")
    list = students.get_all()
    [print(row) for row in list]

################################# MAIN #########################################


# the repository singleton
configFile=sys.argv[1]
if os.path.isfile('schedule.db'):
    sys.exit();
else:
    repo = _Repository()
    atexit.register(repo._close)                    #catch inturrpts and gracefull exit, upon reciving any kind of inturrpt, close resource gracefully.
    students = _student_groups(repo._conn)
    rooms = _classrooms(repo._conn)
    courses = _courses(repo._conn)
    repo.create_tables()
    with open(configFile) as f:
        content = f.readlines()
    for line in content:
        formatAndInsert(line)
    printPostInsertion(courses, rooms, students)









