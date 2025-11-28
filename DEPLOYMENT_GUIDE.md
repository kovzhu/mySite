# Photo Deployment Guide for mySite

This guide explains how to deploy your mySite application with large photo files efficiently.

## 🎯 Overview

Since photo files can be large and numerous, we separate code deployment from photo deployment:

- **Code**: Pushed to GitHub (small, fast)
- **Photos**: Deployed separately via zip files (large, infrequent)

## 📁 Photo Directories Structure

The following directories are excluded from Git:

```
mySite/static/
├── gallery_images/          # Daily observations gallery
├── book_photos/             # Books collection
├── exercise_photos/         # Exercises collection  
├── reading_quote_photos/    # Reading quotes
├── intellectual_photos/     # Intellectual masturbation
├── fragmented_quote_photos/ # Fragmented quotes
├── guitar_photos/           # Guitar collection
├── guitar_videos/           # Guitar videos
├── collection_images/       # Collection thumbnails
├── collection_videos/       # Collection videos
├── personal_images/         # Personal photos
├── project_images/          # Project images
└── blog_media/              # Blog media files
```

## 🚀 Deployment Workflow

### Step 1: Deploy Code Changes

```bash
# Add and commit code changes
git add .
git commit -m "Update: Improved photo viewing interface with navigation controls"

# Push to GitHub
git push origin main
```

### Step 2: Deploy Photos (When Needed)

#### Option A: Deploy All Photos
```bash
# Create zip file with all photos
./deploy_photos.sh zip-all

# This creates: all_photos_YYYYMMDD_HHMMSS.zip
```

#### Option B: Deploy Gallery Photos Only
```bash
# Create zip file with gallery photos only
./deploy_photos.sh zip-gallery

# This creates: gallery_photos_YYYYMMDD_HHMMSS.zip
```

#### Option C: Deploy Collection Photos Only
```bash
# Create zip file with collection photos only
./deploy_photos.sh zip-collections

# This creates: collections_photos_YYYYMMDD_HHMMSS.zip
```

### Step 3: Upload to Server

1. **Upload the zip file** to your server (using scp, sftp, or your preferred method)
2. **Unzip on the server**:
   ```bash
   # Navigate to your project directory
   cd /path/to/your/mySite
   
   # Unzip the file (this will create the directory structure)
   unzip all_photos_YYYYMMDD_HHMMSS.zip
   
   # Or if you want to see progress:
   unzip -v all_photos_YYYYMMDD_HHMMSS.zip
   ```

3. **Verify the structure**:
   ```bash
   # Check if photos are in the right place
   ls -la mySite/static/book_photos/
   ls -la mySite/static/gallery_images/
   ```

## 🛠️ Deployment Script Commands

The `deploy_photos.sh` script provides several useful commands:

```bash
# List all photo directories and their sizes
./deploy_photos.sh list-photos

# Create zip files for different purposes
./deploy_photos.sh zip-all
./deploy_photos.sh zip-gallery
./deploy_photos.sh zip-collections

# Clean up old zip files
./deploy_photos.sh clean-zips

# Show help
./deploy_photos.sh help
```

## 🔄 Server Deployment Process

### Initial Server Setup
1. Clone the repository on your server
2. Set up virtual environment and install dependencies
3. Configure your web server (nginx, Apache, etc.)
4. Set up environment variables

### Photo Deployment to Server
```bash
# On your local machine
./deploy_photos.sh zip-all

# Upload to server (example using scp)
scp all_photos_*.zip user@your-server.com:/tmp/

# On server
cd /path/to/your/mySite
unzip /tmp/all_photos_*.zip

# Restart your application if needed
sudo systemctl restart your-app-service
```

## 📊 Monitoring Photo Sizes

Use the script to monitor your photo storage:

```bash
./deploy_photos.sh list-photos
```

This will show:
- Which directories have photos
- The size of each directory
- Total estimated size

## 🗂️ Git Workflow Best Practices

### What to Commit
- ✅ Python files (app.py, models, etc.)
- ✅ HTML templates
- ✅ CSS/JavaScript files
- ✅ Configuration files
- ✅ Documentation
- ✅ Database migrations

### What NOT to Commit (Excluded in .gitignore)
- ❌ Photo files (all static/photo directories)
- ❌ Database files (*.db, *.sqlite3)
- ❌ Environment variables (.env)
- ❌ Virtual environment directories
- ❌ IDE configuration files

## 🔧 Troubleshooting

### Common Issues

**Photos not showing after deployment?**
- Check if the zip file was extracted correctly
- Verify file permissions on the server
- Ensure the directory structure matches: `mySite/static/[collection_name]/`

**Zip file too large?**
- Use separate zip files for different collections
- Consider compressing images before deployment
- Use `./deploy_photos.sh zip-gallery` for gallery-only updates

**Git still tracking photos?**
```bash
# Remove photos from Git cache
git rm -r --cached mySite/static/gallery_images/
git rm -r --cached mySite/static/book_photos/
# ... etc for other photo directories

# Commit the removal
git commit -m "Remove photos from Git tracking"
```

## 📝 Example Deployment Session

```bash
# 1. Check current photo sizes
./deploy_photos.sh list-photos

# 2. Deploy code changes
git add .
git commit -m "Add navigation controls to photo viewing"
git push origin main

# 3. Deploy photos (if needed)
./deploy_photos.sh zip-collections

# 4. Upload to server
scp collections_photos_20241129_123456.zip user@server.com:/tmp/

# 5. On server: extract and verify
ssh user@server.com
cd /var/www/mySite
unzip /tmp/collections_photos_20241129_123456.zip
ls -la mySite/static/book_photos/ | head -5

# 6. Clean up
rm /tmp/collections_photos_20241129_123456.zip
./deploy_photos.sh clean-zips  # On local machine
```

## 🎉 Benefits of This Approach

- **Faster Git operations** - No large binary files in repository
- **Flexible deployment** - Deploy photos only when they change
- **Bandwidth efficient** - Only upload changed photos
- **Version control friendly** - Clean commit history
- **Easy rollback** - Can revert photo changes independently

---

**Need help?** Check the script help: `./deploy_photos.sh help`
