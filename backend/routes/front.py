from flask import Blueprint, render_template, session, redirect, url_for, request
from backend.models import User, Course, User_course
from backend.extensions import db
from datetime import datetime, timedelta

front_bp = Blueprint('front', __name__)

@front_bp.route('/')
def index():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user and user.role in ('student', 'teacher'):
            return redirect(url_for('front.dashboard'))
        return redirect(url_for('front.predashboard'))
    return render_template('index.html')

@front_bp.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('front.index'))
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('front.index'))
    if user.role not in ('student', 'teacher'):
        return redirect(url_for('front.predashboard'))

    # Optional query param to focus on a single course
    selected_course_id = request.args.get('course_id', type=int)

    # Gather the user's courses
    courses = Course.query.join(User_course, User_course.course_id == Course.id).filter(User_course.user_id == user.id).all()

    # Initialize schedule for weekdays (1=Monday ... 5=Friday)
    schedule = {i: [] for i in range(1, 6)}
    for c in courses:
        try:
            start = c.start_time.strftime('%H:%M')
            end = c.end_time.strftime('%H:%M')
        except Exception:
            start = ''
            end = ''
        day = c.dia if c.dia in schedule else None
        if day:
            schedule[day].append({
                'id': c.id,
                'name': c.name,
                'aula': c.aula,
                'start_time': start,
                'end_time': end
            })

    # Simple helpers for template
    days_names = {1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 5: 'Viernes'}

    # Week date numbers (use current week's Monday..Friday)
    today = datetime.today()
    monday = today - timedelta(days=today.weekday())
    week_dates = {i+1: (monday + timedelta(days=i)).day for i in range(5)}

    # Today's day index (1-7), only show highlight if Monday-Friday
    today_index = today.isoweekday() if 1 <= today.isoweekday() <= 5 else None

    return render_template(
        'dashboard.html',
        username=session['username'],
        schedule=schedule,
        days_names=days_names,
        week_dates=week_dates,
        selected_course_id=selected_course_id,
        today_index=today_index
    )

@front_bp.route('/login')
def login_page():
    return render_template('login.html')

@front_bp.route('/register')
def register_page():
    return render_template('register.html')

@front_bp.route('/predashboard')
def predashboard():
    if 'username' not in session:
        return redirect(url_for('front.login_page'))
    user = User.query.filter_by(username=session['username']).first()
    if user and user.role in ('student', 'teacher'):
        return redirect(url_for('front.dashboard'))
    return render_template('Predashboard.html')

@front_bp.route('/set_role', methods=['POST'])
def set_role():
    if 'username' not in session:
        return redirect(url_for('front.login_page'))
    role = request.form.get('role')
    if role not in ('student', 'teacher'):
        return redirect(url_for('front.predashboard'))
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('front.index'))
    if user.role not in ('student', 'teacher'):
        user.role = role
        db.session.commit()
    return redirect(url_for('front.dashboard'))
