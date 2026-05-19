import os
import secrets
from flask import Flask, render_template, redirect, url_for, flash, request
from models import db, User, WasteReport
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey_waste_management'
# Using v2 database for new features to safely recreate the schema
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///waste_management_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
            
        new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
        # If it's the first user or username is admin, make them admin
        if User.query.count() == 0 or username.lower() == 'admin':
            new_user.is_admin = True
            
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check username and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    from datetime import datetime, timedelta

    if current_user.is_admin:
        reports = WasteReport.query.order_by(WasteReport.date_reported.desc()).all()
    else:
        reports = WasteReport.query.filter_by(user_id=current_user.id).order_by(WasteReport.date_reported.desc()).all()
        
    total_reports = len(reports)
    pending_reports = sum(1 for r in reports if r.status == 'Pending')
    collected_reports = sum(1 for r in reports if r.status == 'Collected')
    
    # Weekly target calculation
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_collected = sum(1 for r in reports if r.status == 'Collected' and r.date_reported >= one_week_ago)
    weekly_target = 20 if current_user.is_admin else 5
    target_progress = min(int((weekly_collected / weekly_target) * 100), 100) if weekly_target > 0 else 0
    
    return render_template('dashboard.html', 
                           reports=reports, 
                           total=total_reports, 
                           pending=pending_reports, 
                           collected=collected_reports,
                           weekly_collected=weekly_collected,
                           weekly_target=weekly_target,
                           target_progress=target_progress)

@app.route('/report', methods=['GET', 'POST'])
@login_required
def report_waste():
    if request.method == 'POST':
        location = request.form.get('location')
        waste_type = request.form.get('waste_type')
        description = request.form.get('description')
        priority = request.form.get('priority')
        
        picture_file = None
        if 'waste_image' in request.files:
            file = request.files['waste_image']
            if file and file.filename != '':
                picture_file = save_picture(file)
                
        new_report = WasteReport(
            location=location, 
            waste_type=waste_type, 
            description=description, 
            priority=priority,
            author=current_user
        )
        if picture_file:
            new_report.image_file = picture_file
            
        db.session.add(new_report)
        db.session.commit()
        flash('Waste reported successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('report.html')

@app.route('/update_status/<int:report_id>', methods=['POST'])
@login_required
def update_status(report_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('dashboard'))
        
    report = WasteReport.query.get_or_404(report_id)
    report.status = request.form.get('status')
    db.session.commit()
    flash('Report status updated.', 'success')
    return redirect(url_for('dashboard'))
with app.app_context():
    db.create_all()

app = app
