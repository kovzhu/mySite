# MySite - Personal Portfolio Website

A Flask-based personal portfolio website with project showcase and about me page.

## 🚀 Quick Start

### Method 1: Using the Run Script (Recommended)
```bash
# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run the application
python run.py
```

### Method 2: Using Flask CLI
```bash
# Set Flask environment variable
export FLASK_APP=mySite/app.py

# Run the application
flask run --port 8080
```

### Method 3: Direct Python Execution
```bash
# Run directly from the mySite directory
python mySite/app.py
```

## 📁 Project Structure

```
mySite/
├── app.py                 # Main Flask application
├── run.py                 # Easy run script
├── requirements.txt       # Python dependencies
├── static/               # Static files (CSS, images)
│   ├── personal_images/  # Personal photos and QR codes
│   └── project_images/   # Project screenshots
├── templates/            # HTML templates
│   ├── index.html        # Home page
│   ├── about.html        # About Me page
│   └── ...              # Other templates
└── database.db          # SQLite database
```

## 🌐 Accessing Your Website

Once running, open your browser to:
- **Home Page**: http://127.0.0.1:8080
- **About Me Page**: http://127.0.0.1:8080/about

## 🔧 Features

- ✅ Responsive design
- ✅ Project portfolio showcase
- ✅ About Me page with QR code
- ✅ Image upload functionality
- ✅ SQLite database integration
- ✅ Bootstrap styling

## 📝 Adding Your QR Code

1. Place your QR code image in `static/personal_images/`
2. Name it `qr_code.jpg` (or update the filename in `about.html`)
3. The QR code will automatically display on the About Me page

## 🛠️ Troubleshooting

### Port Already in Use
If you get "Address already in use" error:
- Use a different port: `python run.py` (uses port 8080)
- Or kill the process using the port: `lsof -ti:8080 | xargs kill -9`

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Flask Command Not Found
Make sure Flask is installed:
```bash
pip install flask
```

## 📞 Support

If you encounter any issues:
1. Check that all dependencies are installed
2. Ensure you're in the correct directory
3. Try using the `run.py` script (Method 1)

Your website should now be running successfully! 🎉
