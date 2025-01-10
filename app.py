from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets
from markupsafe import Markup
import os
from flask_migrate import Migrate
import re

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Secure secret key for session management

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Using SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db) # Initialize Flask-Migrate

# Custom filter to convert newlines to <br> tags
@app.template_filter('nl2br')
def nl2br(value):
    return Markup(value.replace('\n', '<br>\n'))

# Custom filter to truncate text to the first 20 words
@app.template_filter('truncate')
def truncate(value, words=20):
    word_list = value.split()
    if len(word_list) > words:
        return ' '.join(word_list[:words]) + '...'
    return value

def sanitize_filename(filename):
    # Remove invalid characters and replace spaces with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    return sanitized.replace('\\', '/')

@app.context_processor
def inject_now():
    return {'current_year': datetime.now().year}

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_picture = db.Column(db.String(200), nullable=True)
    role = db.Column(db.String(50), nullable=False, default='user')  # 'admin' or 'user'

# Article model
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='article', lazy=True)
    image = db.Column(db.String(200), nullable=True) 

# Comment model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    author = db.relationship('User', backref='comments')

# Helper function to normalize titles and file names
def normalize_title(title):
    return title.strip().replace(" ", "_").lower()  # Normalize spaces and case

# Function to get user by username
def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

# Home route with pagination
@app.route('/')
@app.route('/page/<int:page>')
def home(page=1):
    per_page = 5
    articles = Article.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('home.html', articles=articles)

# Dashboard
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    articles = Article.query.all()
    return render_template('dashboard.html', articles=articles)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials, try again.", "danger")
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        bio = request.form.get('bio')
        profile_picture = request.files.get('profile_picture')
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Check if user already exists
        if get_user_by_username(username):
            flash("Username already exists.", "danger")
            return render_template('register.html')
        
        # Save profile picture if provided
        profile_picture_path = None
        if profile_picture:
            profile_pictures_dir = os.path.join('static', 'profile_pictures')
            if not os.path.exists(profile_pictures_dir):
                os.makedirs(profile_pictures_dir)
            profile_picture_filename = f'{username}_{profile_picture.filename}'
            profile_picture_path = os.path.join('profile_pictures', profile_picture_filename)
            profile_picture.save(os.path.join('static', profile_picture_path))
        
        # Assign role
        role = 'admin' if User.query.count() == 0 else 'user'
        
        new_user = User(
            username=username,
            password=hashed_password,
            email=email,
            bio=bio,
            profile_picture=profile_picture_path,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

# Profile
@app.route('/profile')
def profile():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    articles = Article.query.filter_by(author_id=user.id).all()
    print(f"Profile Picture Path: {user.profile_picture}")
    return render_template('profile.html', user=user, articles=articles)

# Update Profile
@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.bio = request.form['bio']
        if request.files.get('profile_picture'):
            profile_picture = request.files['profile_picture']
            profile_pictures_dir = os.path.join('static', 'profile_pictures')
            if not os.path.exists(profile_pictures_dir):
                os.makedirs(profile_pictures_dir)
            profile_picture_filename = f'{user.username}_{profile_picture.filename}'
            profile_picture_path = os.path.join('profile_pictures', profile_picture_filename)
            profile_picture.save(os.path.join('static', profile_picture_path))
            user.profile_picture = profile_picture_path
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))
    return render_template('update_profile.html', user=user)

# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
def add_article():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image = request.files.get('image')
        image_path = None
        if image:
            image_dir = os.path.join('static', 'article_images')
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)
            sanitized_filename = sanitize_filename(f'{title}_{image.filename}')
            image_path = os.path.join('article_images', sanitized_filename).replace('\\', '/')
            image.save(os.path.join('static', image_path))
        article = Article(
            title=title,
            content=content,
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            author_id=session['user_id'],
            image=image_path
        )
        db.session.add(article)
        db.session.commit()
        flash("Article added successfully!", "success")
        return redirect(url_for('dashboard'))
    return render_template('add_article.html')

# View Article
@app.route('/article/<int:id>')
def article(id):
    article = Article.query.get_or_404(id)
    comments = Comment.query.filter_by(article_id=id).all()
    print(f"Article: {article.title}, Comments: {comments}")  # Debug print statement
    return render_template('article.html', article=article, comments=comments)

# Edit Article
@app.route('/edit_article/<int:id>', methods=['GET', 'POST'])
def edit_article(id):
    article = Article.query.get_or_404(id)
    if request.method == 'POST':
        if article.author_id != session['user_id'] and session['role'] != 'admin':
            flash("You are not authorized to edit this article", "danger")
            return redirect(url_for('home'))
        article.title = request.form['title']
        article.content = request.form['content']
        article.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if request.files.get('image'):
            image = request.files['image']
            image_dir = os.path.join('static', 'article_images')
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)
            sanitized_filename = sanitize_filename(f'{article.title}_{image.filename}')
            image_path = os.path.join('article_images', sanitized_filename).replace('\\', '/')
            image.save(os.path.join('static', image_path))
            article.image = image_path
        db.session.commit()
        flash("Article updated successfully!", "success")
        return redirect(url_for('home'))
    return render_template('edit_article.html', article=article)

# Delete Article
@app.route('/delete_article/<int:id>', methods=['POST'])
def delete_article(id):
    article = Article.query.get_or_404(id)
    if article.author_id != session['user_id'] and session['role'] != 'admin':
        flash("You are not authorized to delete this article", "danger")
        return redirect(url_for('home'))
    db.session.delete(article)
    db.session.commit()
    flash("Article deleted successfully!", "success")
    return redirect(url_for('home'))

# Add Comment
@app.route('/add_comment/<int:article_id>', methods=['POST'])
def add_comment(article_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    content = request.form['content']
    comment = Comment(
        content=content,
        date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        author_id=session['user_id'],
        article_id=article_id
    )
    db.session.add(comment)
    db.session.commit()
    flash("Comment added successfully!", "success")
    return redirect(url_for('article', id=article_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)