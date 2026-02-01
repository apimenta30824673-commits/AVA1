from backend.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=True, default=None)
    # Use a FK to a Career table instead of a free text field
    career = db.Column(db.String(150), nullable=True)

    # Relationship to Career
    career_obj = db.relationship('Career', back_populates='users')

    # Many-to-many convenience: user.courses -> list of Course
    courses = db.relationship(
        'Course',
        secondary='user_course',
        backref=db.backref('students', lazy='dynamic'),
        lazy='dynamic'
    )

    # Relationship to association rows (User_course)
    user_courses = db.relationship('User_course', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    aula = db.Column(db.String(100), nullable=True)
    dia = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    carrer = db.Column(db.String(150), nullable=True)

    # Relationship to association rows (User_course)
    user_courses = db.relationship('User_course', back_populates='course', cascade='all, delete-orphan')


class Career(db.Model):
    __tablename__ = 'career'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)

    # Users that belong to this career
    users = db.relationship('User', back_populates='career_obj', lazy='dynamic')


class User_course(db.Model):
    __tablename__ = 'user_course'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    # Ensure a given (user, course) pair is unique
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='uix_user_course'),)

    user = db.relationship('User', back_populates='user_courses')
    course = db.relationship('Course', back_populates='user_courses')


class Asistencia(db.Model):
    __tablename__ = 'asistencia'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    state = db.Column(db.String(50), nullable=False)

    user = db.relationship('User', backref='asistencias')
    course = db.relationship('Course', backref='asistencias')
