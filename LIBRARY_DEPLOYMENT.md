# Library Books Deployment Guide

## Overview
This guide explains how to deploy the library books to your server after pushing code updates to GitHub.

## Prerequisites
- Code has been pushed to GitHub (library_books folder is gitignored)
- You have SSH access to your server
- The zip file `library_books.zip` is ready in `mySite/static/`

## Deployment Steps

### 1. Push Code to GitHub
```bash
cd "/Users/k/Library/Mobile Documents/com~apple~CloudDocs/08_Python/Working projects/mySite"

# Add all changes
git add .

# Commit changes
git commit -m "Add library feature with book management"

# Push to GitHub
git push origin main
```

### 2. Upload Books Zip File to Server
Use SCP to upload the zip file to your server:

```bash
# Upload to your server
scp "mySite/static/library_books.zip" root@YOUR_SERVER_IP:/root/projects/mySite/mySite/static/
```

### 3. SSH into Server and Pull Code
```bash
# SSH into server
ssh root@YOUR_SERVER_IP

# Navigate to project directory
cd /root/projects/mySite

# Pull latest code from GitHub
git pull origin main

# Apply database migrations
cd mySite
flask db upgrade

# Navigate to static folder
cd static
```

### 4. Extract Books on Server
```bash
# Unzip the library books
unzip library_books.zip

# Verify extraction
ls -la library_books/

# Remove zip file to save space (optional)
rm library_books.zip
```

### 5. Set Correct Permissions
```bash
# Ensure proper permissions
chmod -R 755 library_books/

# If using a web user (e.g., www-data, nginx)
# chown -R www-data:www-data library_books/
```

### 6. Restart Application
```bash
# If using Baota Panel, restart the app through the panel
# Or use your process manager (supervisor, systemd, etc.)

# Example for supervisor:
# supervisorctl restart mysite

# Example for systemd:
# systemctl restart mysite
```

## Verification

1. Visit your website's library page: `https://yoursite.com/library`
2. Check that all categories appear
3. Click into a category to verify books are listed
4. Log in as admin and test the visibility toggle
5. Log in as member and test downloading a book

## Troubleshooting

### Books Not Appearing
- Check that `library_books` folder exists in `mySite/static/`
- Verify file permissions: `ls -la mySite/static/library_books/`
- Check database migrations ran: `flask db current`

### Download Not Working
- Verify file paths in database match actual files
- Check file permissions are readable by web server
- Review server error logs

### Database Issues
If books aren't in the database after migration:
```bash
cd /root/projects/mySite/mySite/scripts
python3 import_books.py
```
Note: This requires the source books directory, which won't be on the server.
Instead, manually insert records or export/import the database.

## Database Export/Import (Alternative Method)

If you want to avoid re-running the import script on the server:

### On Local Machine (before deployment):
```bash
cd mySite
sqlite3 database.db ".dump book" > books_data.sql
```

### On Server (after pulling code):
```bash
cd /root/projects/mySite/mySite
sqlite3 database.db < books_data.sql
```

## Future Book Uploads

For individual book uploads after initial deployment:
1. Log in as admin or member
2. Navigate to the relevant category
3. Click "Upload Book"
4. Select file and upload

The uploaded books will be stored directly on the server in `mySite/static/library_books/`.

## Notes
- The `library_books.zip` file is approximately 1-2 GB (depending on your collection)
- Upload may take several minutes depending on your connection speed
- Consider compressing with higher compression if needed: `zip -9 -r library_books.zip library_books/`
- Keep the local zip file as a backup
