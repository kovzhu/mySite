"""
Main Application File for the Portfolio Website

This Flask application provides a complete personal portfolio website with:
- User authentication system (register, login, logout)
- Blog post management (create, read, update, delete)
- Project portfolio showcase
- Photo gallery with image upload and optimization
- Responsive design for desktop and mobile

Author: K.
"""

import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    send_from_directory,
    make_response,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os  # Make sure to import os
from werkzeug.utils import (
    secure_filename,
)  # Make sure to import this for secure filenames
from PIL import Image
from functools import wraps


# NOTE: For a real application, you would also initialize Flask-Login here
# and use @login_required to protect the create, edit, and delete routes.

# --- Configuration ---
# Initialize Flask application
# __name__ is the name of the current Python module. It is used to determine the root path of the application, which is important for locating resources and templates.
app = Flask(__name__)

# Define upload folders for different content types
# Use absolute paths to ensure folders are created in the correct location
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, "static/project_images")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}  # Allowed image file extensions

# Configure database path using absolute path to avoid issues with instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "database.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Secret key for session management and flash messages
# In production, this should be stored securely (environment variable)
app.config["SECRET_KEY"] = "your_super_secret_key_change_this_later"

# --- Initialize Extensions ---
# Setup database with SQLAlchemy ORM
db = SQLAlchemy(app)

# Setup migration tool for database schema changes
migrate = Migrate(app, db)

# Initialize Flask-Login for user session management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    """
    Callback function for Flask-Login to reload a user object from the user ID stored in the session.

    Args:
        user_id (str): The user ID as a string

    Returns:
        User: The user object if found, None otherwise
    """
    return User.query.get(int(user_id))


# --- Database Models ---


class User(UserMixin, db.Model):
    """
    User model representing registered users of the website.

    Attributes:
        id (int): Primary key
        username (str): Unique username for the user
        email (str): Unique email address
        password_hash (str): Hashed password for security
        role (str): User role ('admin' or 'user')
        created_at (datetime): Timestamp when user was created
        is_active (bool): Whether the user account is active
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default="reader")  # 'admin', 'member', or 'reader'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        """
        Hash and store the user's password.

        Args:
            password (str): Plain text password to hash and store
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verify a password against the stored hash.

        Args:
            password (str): Plain text password to verify

        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """
        Check if the user has admin privileges.

        Returns:
            bool: True if user is admin, False otherwise
        """
        return self.role == "admin"

    def is_member(self):
        """
        Check if the user has member privileges (can comment/like).
        
        Returns:
            bool: True if user is member or admin, False otherwise
        """
        return self.role in ["admin", "member"]


class Comment(db.Model):
    """
    Comment model for blog posts.
    """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('comments', lazy=True))


class Like(db.Model):
    """
    Like model for blog posts.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('likes', lazy=True))


class Message(db.Model):
    """
    Message model for contact form submissions.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    user = db.relationship('User', backref=db.backref('messages', lazy=True))



class Project(db.Model):
    """
    Project model representing portfolio items.

    Attributes:
        id (int): Primary key
        title (str): Project title
        description (str): Detailed description of the project
        url (str): Optional URL link to the project
        year (int): Year the project was completed
        image_filename (str): Name of the associated image file
    """

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(200))
    year = db.Column(db.Integer)
    image_filename = db.Column(db.String(255))


post_labels = db.Table('post_labels',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('label_id', db.Integer, db.ForeignKey('label.id'), primary_key=True)
)

class Label(db.Model):
    """
    Label model for tagging blog posts.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Label {self.name}>'


class Post(db.Model):
    """
    Post model representing blog posts.

    Attributes:
        id (int): Primary key
        title (str): Post title
        content (str): Main content of the post
        created_at (datetime): Timestamp when post was created
    """

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    media_filename = db.Column(db.String(255))
    media_type = db.Column(db.String(50))  # 'image', 'video', 'audio'
    
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")
    likes = db.relationship('Like', backref='post', lazy=True, cascade="all, delete-orphan")
    labels = db.relationship('Label', secondary=post_labels, lazy='subquery',
        backref=db.backref('posts', lazy=True))



class Photo(db.Model):
    """
    Photo model representing gallery images.

    Attributes:
        id (int): Primary key
        title (str): Photo title
        description (str): Optional description of the photo
        filename (str): Name of the image file
        created_at (datetime): Timestamp when photo was uploaded
        month (str): Month identifier (e.g., "nov23", "oct23")
        year (int): Year the photo was taken/uploaded
    """

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    month = db.Column(db.String(20))  # e.g., "nov23", "oct23"
    year = db.Column(db.Integer, default=datetime.now().year)


# --- Authentication Routes ---


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle user registration.

    GET: Display registration form
    POST: Process registration form and create new user

    Returns:
        Rendered template or redirect response
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Validation
        if not username or not password:
            flash("Username and password are required!", "error")
            return render_template("auth/register.html")

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template("auth/register.html")

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return render_template("auth/register.html")

        # Create new user with username as email (for compatibility)
        new_user = User(username=username, email=f"{username}@example.com", role="reader")
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("auth/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login.

    GET: Display login form
    POST: Authenticate user credentials and establish session

    Returns:
        Rendered template or redirect response
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get("next")
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash("Invalid username or password!", "error")

    return render_template("auth/login.html")


@app.route("/logout")
@login_required
def logout():
    """
    Log out the current user and end their session.

    Returns:
        Redirect to homepage with success message
    """
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# --- Decorators ---

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def member_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_member():
            flash("You need to be a member to perform this action.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# --- Main Page Routes ---



@app.route("/")
def index():
    """
    Homepage route that displays recent photos and projects.

    Returns:
        Rendered index.html template with recent photos and projects
    """
    # Get 6 most recent photos for the gallery section
    recent_photos = Photo.query.order_by(Photo.created_at.desc()).limit(6).all()
    # Get 6 most recent blog posts for the humanity section
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(6).all()
    projects = Project.query.order_by(Project.year.desc()).all()

    return render_template(
        "index.html",
        recent_photos=recent_photos,
        recent_posts=recent_posts,
        projects=projects,
    )


@app.route("/about")
def about():
    """
    About page route.

    Returns:
        Rendered about.html template
    """
    return render_template("about.html")


# --- Gallery Routes ---


@app.route("/gallery")
def gallery():
    """
    Photo gallery page that displays all photos grouped by month.

    Returns:
        Rendered photo_gallery.html template with photos organized by month
    """
    # Get distinct years for navigation
    # We can't easily use distinct() on the year column if some photos might not have it set (though our logic tries to set it)
    # So we'll query all years efficiently
    years_query = db.session.query(Photo.year).distinct().all()
    years = sorted([y[0] for y in years_query if y[0] is not None], reverse=True)
    
    # Get current year filter and page
    selected_year = request.args.get('year')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = Photo.query
    
    if selected_year and selected_year != 'all':
        try:
            year_int = int(selected_year)
            query = query.filter_by(year=year_int)
        except ValueError:
            pass # Ignore invalid year format
            
    # Order by year descending, then by filename descending (assuming higher filenames = newer photos)
    pagination = query.order_by(Photo.year.desc(), Photo.filename.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template(
        "gallery/photo_gallery.html", 
        pagination=pagination, 
        years=years,
        selected_year=selected_year if selected_year != 'all' else None
    )


# --- Blog Post Routes ---


@app.route("/blogs")
def blog_index():
    """
    Display all blog posts.
    """
    label_name = request.args.get('label')
    if label_name:
        label = Label.query.filter_by(name=label_name).first()
        if label:
            # Sort posts by date descending
            posts = sorted(label.posts, key=lambda x: x.created_at, reverse=True)
        else:
            posts = []
    else:
        posts = Post.query.order_by(Post.created_at.desc()).all()
    
    all_labels = Label.query.order_by(Label.name).all()
    return render_template("blogs/index.html", posts=posts, labels=all_labels, current_label=label_name)


def get_media_type(filename):
    ext = filename.rsplit(".", 1)[1].lower()
    if ext in {"jpg", "jpeg", "png", "gif"}:
        return "image"
    elif ext in {"mp4", "webm", "ogg"}:
        return "video"
    elif ext in {"mp3", "wav"}:
        return "audio"
    return None


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """
    Create a new blog post.
    """
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        labels_str = request.form.get("labels", "")
        file = request.files.get("media")

        if not title or not content:
            flash("Title and Content are required!", "error")
            return render_template("blogs/create.html", title=title, content=content, labels_str=labels_str)

        media_filename = None
        media_type = None

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            media_type = get_media_type(filename)
            if media_type:
                file.save(os.path.join(app.config["BLOG_UPLOAD_FOLDER"], filename))
                media_filename = filename
            else:
                flash("Unsupported file type!", "error")
                return render_template(
                    "blogs/create.html", title=title, content=content, labels_str=labels_str
                )
        
        # Process labels
        post_labels = []
        if labels_str:
            label_names = [l.strip() for l in labels_str.split(',') if l.strip()]
            for name in label_names:
                label = Label.query.filter_by(name=name).first()
                if not label:
                    label = Label(name=name)
                    db.session.add(label)
                post_labels.append(label)

        new_post = Post(
            title=title,
            content=content,
            media_filename=media_filename,
            media_type=media_type,
            labels=post_labels
        )
        db.session.add(new_post)
        db.session.commit()

        flash("Post created successfully!", "success")
        return redirect(url_for("blog_index"))

    return render_template("blogs/create.html")


@app.route("/posts/<int:post_id>")
def post(post_id):
    """
    Display a single blog post.
    """
    post = Post.query.get_or_404(post_id)
    return render_template("blogs/post.html", post=post)


@app.route("/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit(post_id):
    """
    Edit an existing blog post.
    """
    post = Post.query.get_or_404(post_id)

    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        labels_str = request.form.get("labels", "")
        file = request.files.get("media")

        if not post.title or not post.content:
            flash("Title and Content are required!", "error")
            return render_template("blogs/edit.html", post=post)

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            media_type = get_media_type(filename)
            if media_type:
                # Delete old file if exists
                if post.media_filename:
                    old_path = os.path.join(
                        app.config["BLOG_UPLOAD_FOLDER"], post.media_filename
                    )
                    if os.path.exists(old_path):
                        os.remove(old_path)

                file.save(os.path.join(app.config["BLOG_UPLOAD_FOLDER"], filename))
                post.media_filename = filename
                post.media_type = media_type
            else:
                flash("Unsupported file type!", "error")
                return render_template("blogs/edit.html", post=post)
        
        # Process labels
        post.labels = [] # Clear existing labels
        if labels_str:
            label_names = [l.strip() for l in labels_str.split(',') if l.strip()]
            for name in label_names:
                label = Label.query.filter_by(name=name).first()
                if not label:
                    label = Label(name=name)
                    db.session.add(label)
                post.labels.append(label)

        db.session.commit()

        flash("Post updated successfully!", "success")
        return redirect(url_for("post", post_id=post.id))

    return render_template("blogs/edit.html", post=post)


@app.route("/<int:post_id>/delete", methods=["POST"])
@login_required
def delete(post_id):
    """
    Delete a blog post.
    """
    post = Post.query.get_or_404(post_id)

    if post.media_filename:
        file_path = os.path.join(app.config["BLOG_UPLOAD_FOLDER"], post.media_filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(post)
    db.session.commit()

    flash(f'Post "{post.title}" was successfully deleted.', "info")
    return redirect(url_for("blog_index"))


@app.route("/upload_image", methods=["POST"])
@login_required
def upload_image():
    """
    Handle image uploads from TinyMCE editor.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        # Ensure unique filename to prevent overwrites?
        # For now, just save it. TinyMCE handles the upload.
        file.save(os.path.join(app.config["BLOG_UPLOAD_FOLDER"], filename))
        return jsonify({'location': url_for('static', filename='blog_media/' + filename)})
    return jsonify({'error': 'Upload failed'}), 500


# --- Comment & Like Routes ---

@app.route("/posts/<int:post_id>/comment", methods=["POST"])
@member_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get("content")
    
    if not content:
        flash("Comment cannot be empty.", "error")
        return redirect(url_for("post", post_id=post_id))
        
    comment = Comment(content=content, user_id=current_user.id, post_id=post_id)
    db.session.add(comment)
    db.session.commit()
    
    flash("Comment added!", "success")
    return redirect(url_for("post", post_id=post_id))

@app.route("/comments/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # Allow deletion if user is admin or the comment author
    if not current_user.is_admin() and current_user.id != comment.user_id:
        abort(403)
        
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    
    flash("Comment deleted.", "info")
    return redirect(url_for("post", post_id=post_id))

@app.route("/posts/<int:post_id>/like", methods=["POST"])
@member_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if like:
        db.session.delete(like)
        db.session.commit()
        flash("Unliked.", "info")
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        flash("Liked!", "success")
        
    return redirect(url_for("post", post_id=post_id))


# --- Message Routes ---

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        content = request.form.get("content")
        
        if not name or not email or not content:
            flash("All fields are required!", "error")
            return render_template("contact.html")
            
        user_id = current_user.id if current_user.is_authenticated else None
        
        message = Message(name=name, email=email, content=content, user_id=user_id)
        db.session.add(message)
        db.session.commit()
        
        flash("Message sent! We will get back to you soon.", "success")
        return redirect(url_for("contact"))
        
    return render_template("contact.html")


# --- Admin Routes ---

@app.route("/admin/users")
@admin_required
def admin_users():
    users = User.query.all()
    return render_template("admin/users.html", users=users)

@app.route("/admin/users/<int:user_id>/update", methods=["POST"])
@admin_required
def update_user_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get("role")
    
    if new_role in ["admin", "member", "reader"]:
        user.role = new_role
        db.session.commit()
        flash(f"User {user.username} role updated to {new_role}.", "success")
    else:
        flash("Invalid role selected.", "error")
        
    return redirect(url_for("admin_users"))

@app.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete yourself!", "error")
        return redirect(url_for("admin_users"))
        
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.username} deleted.", "info")
    return redirect(url_for("admin_users"))

@app.route("/admin/messages")
@admin_required
def admin_messages():
    messages = Message.query.order_by(Message.created_at.desc()).all()
    return render_template("admin/messages.html", messages=messages)


# --- Project Management Routes ---



def allowed_file(filename):
    """
    Check if the file extension is allowed.

    Args:
        filename (str): Name of the file to check

    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/add_project", methods=["GET", "POST"])
@login_required
def add_project():
    """
    Add a new project to the portfolio.

    GET: Display the project creation form
    POST: Process the form, handle image upload, and save project to database

    Returns:
        Rendered template or redirect response
    """
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
PHOTO_UPLOAD_FOLDER = os.path.join(basedir, "static/gallery_images")
app.config["PHOTO_UPLOAD_FOLDER"] = PHOTO_UPLOAD_FOLDER

# Create photo upload directory if it doesn't exist
os.makedirs(PHOTO_UPLOAD_FOLDER, exist_ok=True)

# Add blog media upload folder
BLOG_UPLOAD_FOLDER = os.path.join(basedir, "static/blog_media")
app.config["BLOG_UPLOAD_FOLDER"] = BLOG_UPLOAD_FOLDER
os.makedirs(BLOG_UPLOAD_FOLDER, exist_ok=True)


# Add static route for gallery images
@app.route("/static/gallery_images/<path:filename>")
def serve_gallery_images(filename):
    return send_from_directory(app.config["PHOTO_UPLOAD_FOLDER"], filename)


@app.route("/sitemap.xml")
def sitemap():
    """
    Generate sitemap.xml dynamically.
    """
    posts = Post.query.order_by(Post.created_at.desc()).all()
    template = render_template("sitemap.xml", posts=posts)
    response = make_response(template)
    response.headers["Content-Type"] = "application/xml"
    return response


@app.route("/robots.txt")
def robots():
    """
    Generate robots.txt dynamically.
    """
    template = render_template("robots.txt")
    response = make_response(template)
    response.headers["Content-Type"] = "text/plain"
    return response




# --- Photo Gallery Routes ---


@app.route("/upload_photo", methods=["GET", "POST"])
@login_required
def upload_photo():
    """
    Handle photo uploads for the gallery.

    GET: Redirect to gallery page
    POST: Process uploaded photo, optimize it, and save to database

    Returns:
        Redirect response to gallery page
    """
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
            title = filename_without_ext.replace("_", " ").replace("-", " ").title()

        # Get current year for folder organization
        current_date = datetime.now()
        current_year = current_date.year
        
        # Create year directory if it doesn't exist
        year_dir = os.path.join(app.config["PHOTO_UPLOAD_FOLDER"], str(current_year))
        os.makedirs(year_dir, exist_ok=True)

        # Save and resize the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(year_dir, filename)

        # Save original file temporarily
        file.save(file_path)

        try:
            # Open and resize the image
            with Image.open(file_path) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")

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
                    img.save(file_path, "JPEG", quality=85, optimize=True)

                    flash(
                        f"Photo uploaded and optimized! Original: {width}x{height}, Optimized: {new_width}x{new_height}",
                        "success",
                    )
                else:
                    # Image is already small enough, just optimize
                    img.save(file_path, "JPEG", quality=85, optimize=True)
                    flash("Photo uploaded successfully!", "success")
            
            # Generate Thumbnail
            with Image.open(file_path) as img:
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")
                
                # Create thumbnail directory
                thumb_year_dir = os.path.join(app.config["PHOTO_UPLOAD_FOLDER"], "thumbnails", str(current_year))
                os.makedirs(thumb_year_dir, exist_ok=True)
                
                thumb_path = os.path.join(thumb_year_dir, filename)
                
                img.thumbnail((400, 400))
                img.save(thumb_path, "JPEG", quality=80, optimize=True)

        except Exception as e:
            flash(f"Error processing image: {str(e)}", "error")
            return redirect(url_for("gallery"))

        # Auto-generate month from current date (format: "nov23", "dec23", etc.)
        month_abbr = current_date.strftime("%b").lower()  # "nov", "dec", etc.
        year_short = current_date.strftime("%y")  # "23", "24", etc.
        auto_month = f"{month_abbr}{year_short}"

        # Create photo record
        # Store filename as "year/filename"
        db_filename = f"{current_year}/{filename}"
        
        new_photo = Photo(
            title=title,
            description=description,
            filename=db_filename,
            month=auto_month,
            year=current_year,
        )
        db.session.add(new_photo)
        db.session.commit()

        return redirect(url_for("gallery"))

    return redirect(url_for("gallery"))


@app.route("/delete_photo/<int:photo_id>", methods=["POST"])
@login_required
def delete_photo(photo_id):
    """
    Delete a photo from the gallery.

    Args:
        photo_id (int): ID of the photo to delete

    Returns:
        Redirect to gallery page with success message
    """
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
