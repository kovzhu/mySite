# Personal Portfolio Website

A dynamic, responsive personal portfolio website built with Python and Flask. This application features a blog, photo gallery, and project showcase, all managed through a secure user authentication system.

## 🚀 Features

- **User Authentication**: Secure login and registration system using Flask-Login.
- **Blog System**: Full CRUD (Create, Read, Update, Delete) functionality for blog posts.
- **Photo Gallery**: 
  - Image upload with automatic optimization (resizing and compression).
  - Gallery view grouped by month.
  - Lightbox modal for viewing photos.
- **Project Showcase**: dedicated section to display portfolio projects.
- **Responsive Design**: Built with Bootstrap 5 and custom CSS Grid, ensuring a great experience on mobile and desktop.
- **Database**: SQLite database with SQLAlchemy ORM and Flask-Migrate for schema management.

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask
- **Database**: SQLite, SQLAlchemy
- **Frontend**: HTML5, CSS3, Bootstrap 5, Jinja2 Templates
- **Image Processing**: Pillow (PIL)

## 📦 Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/kovzhu/mySite.git
    cd mySite
    ```

2.  **Create a virtual environment**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the database**
    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```

## 🏃‍♂️ Usage

1.  **Run the application**
    ```bash
    python3 run.py
    ```

2.  **Access the site**
    Open your browser and navigate to `http://127.0.0.1:8080`.

3.  **Create an Admin User**
    - Go to `/register` to create your first account.
    - By default, new users have the "user" role. You may need to manually update the database or use a script to promote a user to "admin" if you implement role-based access control.

## 📂 Project Structure

```
mySite/
├── mySite/                 # Main application package
│   ├── static/             # Static assets (CSS, images, JS)
│   │   ├── css/            # Stylesheets
│   │   ├── gallery_images/ # User uploaded photos
│   │   └── ...
│   ├── templates/          # Jinja2 HTML templates
│   ├── app.py              # Application factory and routes
│   └── ...
├── migrations/             # Database migrations
├── requirements.txt        # Python dependencies
├── run.py                  # Entry point script
└── README.md               # Project documentation
```

## 🤝 Contributing

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)
