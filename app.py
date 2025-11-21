import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os  # Make sure to import os
from werkzeug.utils import (
    secure_filename,
)  # Make sure to import this for secure filenames

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


# --- Database Models ---


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


# --- Routes ---


@app.route("/")
def index():
    """Main page route: fetches projects and posts."""
    # Use SQLAlchemy to query the tables
    projects = Project.query.order_by(Project.year.desc()).all()
    posts = Post.query.order_by(Post.created_at.desc()).all()

    return render_template("index.html", projects=projects, posts=posts)


@app.route("/about")
def about():
    """About Me page route."""
    return render_template("about.html")


@app.route("/create", methods=["GET", "POST"])
# @login_required # Add this once Flask-Login is set up
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
# @login_required
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
# @login_required
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
# @login_required # Protect this route with login
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


# --- Initial Run Block ---
if __name__ == "__main__":
    # You MUST run flask db init, flask db migrate, and flask db upgrade
    # in the terminal before running this script for the first time.
    app.run(debug=True, port=5000)
