import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os  # Make sure to import os
from werkzeug.utils import (
    secure_filename,
)  # Make sure to import this for secure filenames
from PIL import Image

# NOTE: For a real application, you would also initialize Flask-Login here
# and use @login_required to protect the create, edit, and delete routes.

# --- Configuration ---
app = Flask(__name__)
# Define your upload folder
UPLOAD_FOLDER = "static/project_images"  # This is where images will be saved
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
# SQLite configuration (relative path) - use absolute path to avoid instance folder
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "database.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Set a secret key (required for flash messages)
app.config["SECRET_KEY"] = "your_super_secret_key_change_this_later"

# --- Initialize Extensions ---
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Database Models ---


class User(UserMixin, db.Model):
    """Represents users in the system."""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'


class Project(db.Model):
    """Represents the 'projects' table for portfolio items."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(200))
    year = db.Column(db.Integer)
    image_filename = db.Column(db.String(255))


class Post(db.Model):
    """Represents the 'posts' table for blog/updates."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # media_path = db.Column(db.String(255)) # Uncomment if adding file uploads


class Photo(db.Model):
    """Represents photos in the gallery."""
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    month = db.Column(db.String(20))  # e.g., "nov23", "oct23"
    year = db.Column(db.Integer, default=datetime.now().year)


# --- Routes ---


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Validation
        if not username or not email or not password:
            flash("All fields are required!", "error")
            return render_template("auth/register.html")
        
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template("auth/register.html")
        
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return render_template("auth/register.html")
        
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "error")
            return render_template("auth/register.html")
        
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    
    return render_template("auth/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = bool(request.form.get("remember"))
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash("Invalid username or password!", "error")
    
    return render_template("auth/login.html")


@app.route("/logout")
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))


@app.route("/")
def index():
    """Main page route: fetches recent photos and projects."""
    # Get 6 most recent photos for the gallery section
    recent_photos = Photo.query.order_by(Photo.created_at.desc()).limit(6).all()
    projects = Project.query.order_by(Project.year.desc()).all()

    return render_template("index.html", recent_photos=recent_photos, projects=projects)


@app.route("/about")
def about():
    """About Me page route."""
    return render_template("about.html")


@app.route("/gallery")
def gallery():
    """Photo gallery page route."""
    # Get all photos grouped by month
    photos = Photo.query.order_by(Photo.created_at.desc()).all()
    
    # Group photos by month
    photos_by_month = {}
    for photo in photos:
        if photo.month not in photos_by_month:
            photos_by_month[photo.month] = []
        photos_by_month[photo.month].append(photo)
    
    return render_template("gallery/photo_gallery.html", photos_by_month=photos_by_month)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Renders creation form (GET) or processes submission (POST)."""
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title or not content:
            flash("Title and Content are required!", "error")
            # The 'preserve_context=True' keeps form data if validation fails
            return render_template("create.html", title=title, content=content)

        # Create a new Post object and commit to the database
        new_post = Post(title=title, content=content)
        db.session.add(new_post)
        db.session.commit()

        flash("Post created successfully!", "success")
        return redirect(url_for("index"))

    return render_template("create.html")


@app.route("/posts/<int:post_id>")
def post(post_id):
    """Displays a single post."""
    # Use get_or_404() which automatically throws a 404 if the post is not found
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", post=post)


@app.route("/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit(post_id):
    """Handles displaying and processing the post edit form."""
    post = Post.query.get_or_404(post_id)

    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]

        if not post.title or not post.content:
            flash("Title and Content are required!", "error")
            return render_template("edit.html", post=post)

        # SQLAlchemy tracks changes automatically; just commit the session
        db.session.commit()

        flash("Post updated successfully!", "success")
        return redirect(url_for("post", post_id=post.id))

    return render_template("edit.html", post=post)


@app.route("/<int:post_id>/delete", methods=["POST"])
@login_required
def delete(post_id):
    """Deletes a post from the database."""
    post = Post.query.get_or_404(post_id)

    # Delete the object from the session and commit
    db.session.delete(post)
    db.session.commit()

    flash(f'Post "{post.title}" was successfully deleted.', "info")
    return redirect(url_for("index"))


# app.py (Add this new route)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/add_project", methods=["GET", "POST"])
@login_required
def add_project():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        url = request.form["url"]
        year = request.form["year"]

        # Handle file upload
        file = request.files.get("project_image")  # Get the file from the request
        image_filename = None

        if file and file.filename != "" and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Create the upload directory if it doesn't exist
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            image_filename = filename  # Store only the filename in DB

        if not title or not description:
            flash("Title and Description are required for a project!", "error")
            # You might want to pass back the submitted data to pre-fill the form
            return render_template(
                "add_project.html",
                title=title,
                description=description,
                url=url,
                year=year,
            )

        new_project = Project(
            title=title,
            description=description,
            url=url,
            year=year,
            image_filename=image_filename,  # Save the filename to the database
        )
        db.session.add(new_project)
        db.session.commit()

        flash("Project added successfully!", "success")
        return redirect(url_for("index"))

    return render_template("add_project.html")


# Don't forget to add this to your app.config
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Add photo upload folder
PHOTO_UPLOAD_FOLDER = "static/gallery_images"
app.config["PHOTO_UPLOAD_FOLDER"] = PHOTO_UPLOAD_FOLDER

# Create photo upload directory if it doesn't exist
os.makedirs(PHOTO_UPLOAD_FOLDER, exist_ok=True)

# Add static route for gallery images
@app.route('/static/gallery_images/<path:filename>')
def serve_gallery_images(filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'gallery_images'), filename)

# --- Photo Gallery Routes ---

@app.route("/upload_photo", methods=["GET", "POST"])
@login_required
def upload_photo():
    """Handle photo uploads for the gallery."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        file = request.files.get("photo")
        
        if not file or file.filename == "":
            flash("Photo file is required!", "error")
            return redirect(url_for("gallery"))
        
        if not allowed_file(file.filename):
            flash("Invalid file type. Allowed types: png, jpg, jpeg, gif", "error")
            return redirect(url_for("gallery"))
        
        # Generate default title if empty
        if not title:
            # Use filename without extension as default title
            filename_without_ext = os.path.splitext(secure_filename(file.filename))[0]
            title = filename_without_ext.replace('_', ' ').replace('-', ' ').title()
        
        # Save and resize the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["PHOTO_UPLOAD_FOLDER"], filename)
        
        # Save original file temporarily
        file.save(file_path)
        
        try:
            # Open and resize the image
            with Image.open(file_path) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Calculate new dimensions while maintaining aspect ratio
                max_width = 1200  # Optimal for web display
                max_height = 800
                
                # Get current dimensions
                width, height = img.size
                
                # Calculate new dimensions
                if width > max_width or height > max_height:
                    # Calculate scaling factor
                    width_ratio = max_width / width
                    height_ratio = max_height / height
                    scale_factor = min(width_ratio, height_ratio)
                    
                    # Calculate new dimensions
                    new_width = int(width * scale_factor)
                    new_height = int(height * scale_factor)
                    
                    # Resize image
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Save optimized version (overwrite original)
                    img.save(file_path, 'JPEG', quality=85, optimize=True)
                    
                    flash(f"Photo uploaded and optimized! Original: {width}x{height}, Optimized: {new_width}x{new_height}", "success")
                else:
                    # Image is already small enough, just optimize
                    img.save(file_path, 'JPEG', quality=85, optimize=True)
                    flash("Photo uploaded successfully!", "success")
        
        except Exception as e:
            flash(f"Error processing image: {str(e)}", "error")
            return redirect(url_for("gallery"))
        
        # Auto-generate month from current date (format: "nov23", "dec23", etc.)
        current_date = datetime.now()
        month_abbr = current_date.strftime("%b").lower()  # "nov", "dec", etc.
        year_short = current_date.strftime("%y")  # "23", "24", etc.
        auto_month = f"{month_abbr}{year_short}"
        
        # Create photo record
        new_photo = Photo(
            title=title,
            description=description,
            filename=filename,
            month=auto_month,
            year=current_date.year
        )
        db.session.add(new_photo)
        db.session.commit()
        
        return redirect(url_for("gallery"))
    
    return redirect(url_for("gallery"))


@app.route("/delete_photo/<int:photo_id>", methods=["POST"])
@login_required
def delete_photo(photo_id):
    """Delete a photo from the gallery."""
    photo = Photo.query.get_or_404(photo_id)
    
    # Delete the file from filesystem
    file_path = os.path.join(app.config["PHOTO_UPLOAD_FOLDER"], photo.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete from database
    db.session.delete(photo)
    db.session.commit()
    
    flash(f'Photo "{photo.title}" was successfully deleted.', "info")
    return redirect(url_for("gallery"))


# --- Initial Run Block ---
if __name__ == "__main__":
    # You MUST run flask db init, flask db migrate, and flask db upgrade
    # in the terminal before running this script for the first time.
    app.run(debug=True, port=5001)
