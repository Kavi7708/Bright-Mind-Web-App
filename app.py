from flask import Flask, render_template, request, url_for, redirect, session, flash
import json 
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

# 1. Configuration Load Karein
with open('static/config.json', 'r') as C:
    params = json.load(C)["params"]

app = Flask(__name__, template_folder='template')
app.config['SECRET_KEY'] = 'supersecretkey'

# 2. Database Connection (XAMPP MySQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/Bright_Mind'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


UPLOAD_FOLDERS = {
    'Syllabus': 'static/syllabus',
    'Notes': 'static/notes',
    'Paper': 'static/paper',
    'Ebook': 'static/ebook',
    'Covers': 'static/book_covers' 
}
for folder in UPLOAD_FOLDERS.values():
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- DATABASE MODELS ---

class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), nullable=False) # Syllabus, Paper, Ebook
    branch = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(50))
    year = db.Column(db.String(20), nullable=True)
    file_url = db.Column(db.String(255), nullable=False)

class Notes(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), default='Notes')
    branch = db.Column(db.String(50))
    semester = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(50))
    file_url = db.Column(db.String(255), nullable=False)

class Video(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(255), nullable=False)


class Paper(db.Model):
    __tablename__ = 'papers'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), default='Paper')
    branch = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(50))
    year = db.Column(db.String(20),nullable=True)
    file_url = db.Column(db.String(255), nullable=False)

class Ebook(db.Model):
    __tablename__ = 'ebooks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True) # <-- New: Short description
    category = db.Column(db.String(100), default='Ebook')
    branch = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    file_url = db.Column(db.String(255), nullable=False) # Stores the PDF
    cover_url = db.Column(db.String(255), nullable=False) # <-- New: Stores the Cover Image


with app.app_context():
    db.create_all()


#======= ROUTES========

@app.route('/contribute')
def contribute():
    return render_template('contribute.html', params=params)

@app.route('/syllabus')
def syllabus():
    items = Resource.query.filter_by(category='Syllabus').all()
    return render_template('syllabus.html', syllabuses=items, params=params)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!", "success")
    return redirect('/login')

@app.route('/about')
def about():
    return render_template('about.html', params=params)

@app.route('/notes')
def notes():
    items = Notes.query.all()
    return render_template('Notes.html', all_notes=items, params=params)

@app.route('/video')
def video():
    vids = Video.query.all()
    return render_template('video.html', videos=vids, params=params)

@app.route('/video_player/<int:video_id>')
def video_player(video_id):
    vid = Video.query.get_or_404(video_id)
    return render_template('video_player.html', video=vid, params=params)

@app.route('/paper')
def paper():
    items = Paper.query.filter_by(category='Paper').all()
    return render_template("paper.html", papers=items, params=params)

@app.route('/book')
def book():
    items = Ebook.query.filter_by(category='Ebook').all()
    return render_template('Book.html', books=items, params=params)
    
@app.route('/')
def home():
   
    res = Resource.query.order_by(Resource.id.desc()).limit(3).all()
    nts = Notes.query.order_by(Notes.id.desc()).limit(3).all()
    vds = Video.query.order_by(Video.id.desc()).limit(3).all()
    paper = Paper.query.order_by(Paper.id.desc()).limit(3).all()
    ebook = Ebook.query.order_by(Ebook.id.desc()).limit(3).all()
    
    recent_items = []
    for i in res: recent_items.append({'title': i.title, 'category': i.category})
    for i in nts: recent_items.append({'title': i.title, 'category': 'Notes'})
    for i in vds: recent_items.append({'title': i.title, 'category': 'Video'})
    for i in paper: recent_items.append({'title': i.title, 'category': 'Paper'})
    for i in ebook: recent_items.append({'title': i.title, 'category': 'Ebook'})
    
    return render_template('bright_mind.html', recent_items=recent_items, params=params)

@app.route('/admin/upload', methods=['POST'])
def admin_upload():
    if 'user' in session and session['user'] == params['admin_user']:
        category = request.form.get('category')
        file = request.files.get('file')
        
        if file and category:
            filename = secure_filename(file.filename)
            upload_path = os.path.join('static', category.lower())
            file.save(os.path.join(upload_path, filename))

         
            if category == 'Notes':
                new_item = Notes(title=request.form['title'], branch=request.form['branch'], semester=request.form['semester'], subject=request.form['subject'], file_url=filename)
                flash("Notes uploaded successfully!", "success")
            elif category == 'Paper':
                new_item = Paper(
                    title=request.form['title'], 
                    branch=request.form['branch'], 
                    semester=request.form['semester'], 
                    subject=request.form.get('subject'), # <-- ADD THIS LINE
                    year=request.form.get('year'), 
                    file_url=filename
                    )
                flash("Paper uploaded successfully!", "success")
                 
            elif category == 'Syllabus':
   
                new_item = Resource(
                    title=request.form['title'], 
                    category='Syllabus', 
                    branch=request.form['branch'], 
                    semester=request.form['semester'], 
                    subject=request.form.get('subject'), # <-- FIX: Added Subject
                    year=request.form.get('year'),       # <-- FIX: Added Year
                    file_url=filename
                    )  
                flash("Syllabus uploaded successfully!", "success")          
            else:
                flash("Invalid category selected", "danger")
                return redirect('/dashboard')
            db.session.add(new_item)
            db.session.commit()
        return redirect('/dashboard')
    return redirect('/login')


@app.route('/admin/upload_ebook', methods=['POST'])
def admin_upload_ebook():
    if 'user' in session and session['user'] == params['admin_user']:
        title = request.form.get('title')
        description = request.form.get('description')
        branch = request.form.get('branch')
        semester = request.form.get('semester')
        subject = request.form.get('subject')
        
        pdf_file = request.files.get('pdf_file')
        cover_image = request.files.get('cover_image')
        
        if pdf_file and cover_image:
            pdf_filename = secure_filename(pdf_file.filename)
            cover_filename = secure_filename(cover_image.filename)
            
            
            pdf_file.save(os.path.join('static/ebook', pdf_filename))
            cover_image.save(os.path.join('static/book_covers', cover_filename))
            
           
            new_ebook = Ebook(
                title=title, 
                description=description,
                branch=branch, 
                semester=semester, 
                subject=subject, 
                file_url=pdf_filename,
                cover_url=cover_filename
            )
            db.session.add(new_ebook)
            db.session.commit()
            flash("Ebook with cover uploaded successfully!", "success")
        else:
            flash("Please upload both the PDF and the Cover Image.", "danger")
            
        return redirect('/dashboard')
    return redirect('/login')


# --- AUTHENTICATION & DASHBOARD ---

@app.route('/dashboard')
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        return render_template("dashboard.html", params=params)
    flash("Please log in first", "danger")
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session and session['user'] == params['admin_user']:
        flash("Welcome Back Sir!", "success")
        return redirect('/dashboard')

    if request.method == 'POST':
        uname = request.form.get('uname')
        pwd = request.form.get('password')
        if uname == params['admin_user'] and pwd == params['admin_password']:
            session['user'] = uname
            flash("Logged in successfully!", "success")
            return redirect('/dashboard')
        flash("Invalid credentials", "danger")
    
    return render_template('login.html', params=params)



if __name__ == '__main__':
    app.run(debug=True)