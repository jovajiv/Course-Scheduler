import os
import sqlite3
import inspect


class student:
    def __init__(self, grade, count):
        self.grade = grade
        self.count = count


class classroom:

    # constructor for reading from SQLITE db.
    # if current_course_id and current_course_time_left are not passed as parameters, put default value 0.
    # if they are passed as values, then copy those values as usuall.
    def __init__(self, id , location, current_course_id=0, current_course_time_left=0):
        self.id = id
        self.location = location
        self.current_course_id = current_course_id
        self.current_course_time_left = current_course_time_left


class course:
    def __init__(self, id, course_name, student, number_of_students, class_id, course_length) :
        self.id = id
        self.course_name = course_name
        self.student = student
        self.number_of_students = number_of_students
        self.class_id = class_id
        self.course_length = course_length


def orm(cursor, dto_type):
    # the following line retrieve the argument names of the constructor
    args = inspect.getargspec(dto_type.__init__).args

    # the first argument of the constructor will be 'self', it does not correspond
    # to any database field, so we can ignore it.
    args = args[1:]

    # gets the names of the columns returned in the cursor
    col_names = [column[0] for column in cursor.description]

    # map them into the position of the corresponding constructor argument
    col_mapping = [col_names.index(arg) for arg in args]
    return [row_map(row, col_mapping, dto_type) for row in cursor.fetchall()]


def row_map(row, col_mapping, dto_type):
    ctor_args = [row[idx] for idx in col_mapping]
    return dto_type(*ctor_args)


class Dao:
    def __init__(self, dto_type, conn):
        self._conn = conn
        self._dto_type = dto_type

        # dto_type is a class, its __name__ field contains a string representing the name of the class.
        self._table_name = dto_type.__name__.lower() + 's'

    def insert(self, dto_instance):
        ins_dict = vars(dto_instance)

        column_names = ','.join(ins_dict.keys())
        params = ins_dict.values()
        qmarks = ','.join(['?'] * len(ins_dict))

        stmt = 'INSERT INTO {} ({}) VALUES ({})'.format(self._table_name, column_names, qmarks)

        self._conn.execute(stmt, params)

    def find_all(self):
        c = self._conn.cursor()
        c.execute('SELECT * FROM {}'.format(self._table_name))
        return orm(c, self._dto_type)

    def get_all(self):
        c = self._conn.cursor()

        stmt = 'SELECT * FROM {}'.format(self._table_name)
        c.execute(stmt)
        return c.fetchall()

    def find(self, **keyvals):
        column_names = keyvals.keys()
        params = list(keyvals.values())

        stmt = 'SELECT * FROM {} WHERE {}'.format(self._table_name, ' AND '.join([col + '=?' for col in column_names]))

        c = self._conn.cursor()
        c.execute(stmt, params)
        return orm(c, self._dto_type)

    def delete(self, **keyvals):
        column_names = keyvals.keys()
        params = list(keyvals.values())

        stmt = 'DELETE FROM {} WHERE {}'.format(self._table_name, ' AND '.join([col + '=?' for col in column_names]))

        c = self._conn.cursor()
        c.execute(stmt, params)

    def update(self, set_values, cond):
        set_column_names = list(set_values.keys())                       ## ERROR found here ,ORIGIN is set_column_names = set_values.keys() . had to add the list becouse  self._conn.execute(stmt, params) only knows how to run params when its a list , yet originally params is of type dict_values.
        set_params = list(set_values.values())

        cond_column_names = list(cond.keys())
        cond_params = list(cond.values())

        params = set_params + cond_params
                                                                                                                ## ERROR found here , they originally was  "SET ({}) WHERE ({})" , the round () encirle does not run in sqlite , had to remove it
        stmt = 'UPDATE {} SET {} WHERE {}'.format(self._table_name,
                                                      ', '.join([set + '=?' for set in set_column_names]),
                                                      ' AND '.join([cond + '=?' for cond in cond_column_names]))

        self._conn.execute(stmt, params)

    #  Recives set value , if value is positive, then increment, else decrement by that amount.
    # also gives possiblity to decide wheter or not "WHERE" will check if "=" or "!="

    def IncresaeOrDecreaseBy(self, set_values, cond, equalOrNotEqual):
        set_column_names = list(set_values.keys())
        set_params = list(set_values.values())

        cond_column_names = list(cond.keys())
        cond_params = list(cond.values())

        params = set_params + cond_params

        stmt = 'UPDATE {} SET {} WHERE {}'.format(self._table_name,
                                                      ', '.join([set + '=' + set + '+?' for set in set_column_names]),
                                                      ' AND '.join([cond + equalOrNotEqual+'?' for cond in cond_column_names]))
        self._conn.execute(stmt, params)


def CoursesTableIsEmpty(conn):
    if len(Dao(course, conn).find_all()) > 0:
        return False
    else:
        return True


def register_class(room, conn):
    cour = Dao(course, conn).find(class_id=room.id)
    if len(cour) > 0:
        print("({}) {}: {} is schedule to start".format(iter_time, room.location, cour[0].course_name))
        Dao(classroom, conn).update({'current_course_id': cour[0].id}, {'id': cour[0].class_id})
        Dao(classroom, conn).update({'current_course_time_left': cour[0].course_length},
                                    {'id': cour[0].class_id})
        Dao(student, conn).IncresaeOrDecreaseBy({'count': -cour[0].number_of_students},
                                                {'grade': cour[0].student}, "=")


def print_all(conn):
    print("courses")
    list = Dao(course, conn).get_all()
    [print(row) for row in list]
    print("classrooms")
    list = Dao(classroom, conn).get_all()
    [print(row) for row in list]
    print("students")
    list = Dao(student, conn).get_all()
    [print(row) for row in list]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if os.path.isfile('schedule.db'):
    conn = sqlite3.connect('schedule.db')
    iter_time = 0

    # said in the end of the example in the specification:
    # "Now, if we try to run schedule.py again, it will just print the tables and exit immediately
    # because all courses are done already. "
    if CoursesTableIsEmpty(conn):
        print_all(conn)

    while not CoursesTableIsEmpty(conn):  # the "main" loop for iteration.

        for room in Dao(classroom, conn).find_all():

            if room.current_course_id == 0:  # no course in this room. register one.
                register_class(room, conn)

            else:  # there is course in this room
                Dao(classroom, conn).IncresaeOrDecreaseBy({'current_course_time_left': -1},
                                                           {'id': room.id}, "=")
                room.current_course_time_left -= 1
                if room.current_course_time_left == 0:
                    cour = Dao(course, conn).find(class_id=room.id)
                    print("({}) {}: {} is done".format(iter_time, room.location, cour[0].course_name))
                    # delete course that is done
                    Dao(course, conn).delete(id=cour[0].id)
                    Dao(classroom, conn).update({'current_course_id': 0}, {'id': room.id})
                    # if there is another course that is waiting to this room, put him in this iteration
                    register_class(room, conn)

                else:
                    # curr_course_in_room = Dao(course, conn).find(id=room.current_course_id)
                    cour = Dao(course, conn).find(class_id=room.id)
                    print("({}) {}: occupied by {}".format(iter_time, room.location, cour[0].course_name))
        print_all(conn)
        iter_time += 1
        conn.commit()

