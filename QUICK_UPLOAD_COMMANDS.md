# Quick Upload Commands Reference

## Local Machine (Before Upload)

### 1. Create All Zip Files
```bash
./create_upload_zips.sh
```

### 2. Verify Zip Files
```bash
# Check file sizes
ls -lh library_books_*.zip*

# Check total count
ls library_books_*.zip* | wc -l

# Test extraction (optional)
unzip -t library_books_Biography.zip
```

### 3. Upload to Server
```bash
# Replace YOUR_SERVER_IP with your actual server IP
scp library_books_*.zip* root@YOUR_SERVER_IP:/root/projects/mySite/mySite/static/
```

## Server (After Upload)

### 1. Connect to Server
```bash
ssh root@YOUR_SERVER_IP
```

### 2. Navigate to Directory
```bash
cd /root/projects/mySite/mySite/static/
```

### 3. Copy Deployment Script (if not already there)
```bash
# Copy from local machine or create manually
```

### 4. Run Deployment
```bash
chmod +x deploy_books.sh
./deploy_books.sh
```

### 5. Verify Deployment
```bash
# Check final structure
ls -la library_books/

# Check total size
du -sh library_books/

# Test a few categories
ls library_books/History/
ls library_books/Python/
```

## Expected Results

### After Local Script:
- ~20-25 zip files created
- All files under 500MB
- Files named: `library_books_CategoryName.zip` or `library_books_CategoryName.z01`, `.z02`, etc.

### After Server Deployment:
- 7.1GB total in `library_books/` directory
- 19 categories restored
- Proper permissions set
- Web-accessible files

## Troubleshooting Quick Commands

### Zip Creation Issues
```bash
# If zip command not found
sudo apt-get install zip  # Ubuntu/Debian
brew install zip         # macOS

# If split zip not working
zip -r -s 450m filename.zip directory/
```

### Upload Issues
```bash
# Check server connectivity
ping YOUR_SERVER_IP

# Check if directory exists on server
ssh root@YOUR_SERVER_IP "ls -la /root/projects/mySite/mySite/static/"

# Upload single file test
scp library_books_Biography.zip root@YOUR_SERVER_IP:/root/projects/mySite/mySite/static/
```

### Server Deployment Issues
```bash
# Check disk space
df -h

# Check if unzip is installed
which unzip

# Manual extraction test
unzip -o library_books_Biography.zip -d test_extraction/
```

## Quick Verification Checklist

- [ ] All 19 categories have corresponding zip files
- [ ] No zip file exceeds 500MB
- [ ] All zip files uploaded to server
- [ ] Server has at least 8GB free space
- [ ] Deployment script runs without errors
- [ ] All 19 categories appear in final directory
- [ ] Books are accessible via web interface
