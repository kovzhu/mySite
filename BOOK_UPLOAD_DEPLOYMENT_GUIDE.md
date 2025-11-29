# Book Files Upload and Deployment Guide

## Overview
You have 7.1GB of book files that need to be uploaded to your server with a 500MB file size limit. This guide provides a complete strategy for zipping, uploading, and deploying your book files.

## Current Book Files Structure
- **Total size**: 7.1GB
- **Directory**: `mySite/static/library_books/`
- **Categories**: 19 folders with sizes ranging from 3.9MB to 2.2GB

## Zip Strategy - Creating 500MB Chunks

### Option 1: Category-based Zipping (Recommended)
Since some categories are already under 500MB, we can zip them individually:

```bash
# Categories under 500MB (can be zipped individually)
zip -r library_books_part1.zip "mySite/static/library_books/Biography"           # 310M
zip -r library_books_part2.zip "mySite/static/library_books/China classical"     # 3.9M
zip -r library_books_part3.zip "mySite/static/library_books/Economist"           # 86M
zip -r library_books_part4.zip "mySite/static/library_books/General non-fiction" # 228M
zip -r library_books_part5.zip "mySite/static/library_books/Investing"           # 51M
zip -r library_books_part6.zip "mySite/static/library_books/Medical and health"  # 20M
zip -r library_books_part7.zip "mySite/static/library_books/Politics"            # 151M
zip -r library_books_part8.zip "mySite/static/library_books/Power BI"            # 34M
zip -r library_books_part9.zip "mySite/static/library_books/Science"             # 70M
zip -r library_books_part10.zip "mySite/static/library_books/Work related"       # 148M

# Categories over 500MB (need splitting)
# History (2.2G), Humanistic and art (524M), Kids Education (389M), Learning (863M), 
# Literature (215M), Philosophy and religion (478M), Psychology and spiritual (311M), 
# Python (547M), Social (532M)
```

### Option 2: Automated Size-based Splitting
For larger categories, use this script to split them into 450MB chunks:

```bash
#!/bin/bash
# split_large_category.sh
CATEGORY=$1
MAX_SIZE=450000000  # 450MB in bytes

# Create temporary directory
mkdir -p temp_split

# Find all files in the category and split into chunks
find "mySite/static/library_books/$CATEGORY" -type f | while read file; do
    current_size=$(du -b "temp_split/current_chunk" 2>/dev/null | cut -f1)
    if [ -z "$current_size" ] || [ $current_size -gt $MAX_SIZE ]; then
        chunk_num=$((chunk_num+1))
        zip -r "library_books_${CATEGORY// /_}_part${chunk_num}.zip" temp_split/*
        rm -rf temp_split/*
        mkdir -p temp_split
    fi
    cp "$file" "temp_split/"
done

# Don't forget the last chunk
if [ "$(ls -A temp_split)" ]; then
    chunk_num=$((chunk_num+1))
    zip -r "library_books_${CATEGORY// /_}_part${chunk_num}.zip" temp_split/*
fi

rm -rf temp_split
```

## Upload Process

### Step 1: Create All Zip Files
Run this command to create all necessary zip files:

```bash
# Make the script executable
chmod +x create_upload_zips.sh

# Run the script
./create_upload_zips.sh
```

### Step 2: Upload to Server
Upload all zip files to: `/root/projects/mySite/mySite/static/`

You can use:
- `scp` command
- SFTP client
- Your preferred file transfer method

```bash
# Example using scp
scp library_books_*.zip root@your-server-ip:/root/projects/mySite/mySite/static/
```

## Server-side Deployment

### Step 1: Connect to Server
```bash
ssh root@your-server-ip
```

### Step 2: Navigate to Project Directory
```bash
cd /root/projects/mySite/mySite/static/
```

### Step 3: Create and Run Deployment Script
Create `deploy_books.sh` on the server:

```bash
#!/bin/bash
# deploy_books.sh

# Create library_books directory if it doesn't exist
mkdir -p library_books

# Extract all zip files
for zip_file in library_books_*.zip; do
    echo "Extracting $zip_file..."
    unzip -o "$zip_file" -d library_books/
done

# Fix permissions (if needed)
chmod -R 755 library_books/
chown -R www-data:www-data library_books/  # Adjust user:group as needed

echo "Book files deployment completed!"
```

Make it executable and run:
```bash
chmod +x deploy_books.sh
./deploy_books.sh
```

### Step 4: Verify Deployment
```bash
# Check if files are properly extracted
ls -la library_books/

# Check total size
du -sh library_books/

# Verify a few categories
ls library_books/History/
ls library_books/Python/
```

## Complete Automation Scripts

### Local Script: create_upload_zips.sh
```bash
#!/bin/bash
# create_upload_zips.sh - Create zip files for upload

echo "Creating zip files for book upload..."

# Create individual zips for smaller categories
zip_categories=(
    "Biography"
    "China classical" 
    "Economist"
    "General non-fiction"
    "Investing"
    "Medical and health"
    "Politics"
    "Power BI"
    "Science"
    "Work related"
)

for category in "${zip_categories[@]}"; do
    safe_name=$(echo "$category" | tr ' ' '_')
    echo "Zipping $category..."
    zip -r "library_books_${safe_name}.zip" "mySite/static/library_books/$category"
done

# For larger categories, split them
large_categories=(
    "History"
    "Humanistic and art"
    "Kids Education"
    "Learning"
    "Literature"
    "Philosophy and religion"
    "Psychology and spiritual"
    "Python"
    "Social"
)

for category in "${large_categories[@]}"; do
    safe_name=$(echo "$category" | tr ' ' '_')
    echo "Processing large category: $category"
    
    # Use zip with split option (if available) or manual splitting
    zip -r -s 450m "library_books_${safe_name}.zip" "mySite/static/library_books/$category"
done

echo "All zip files created successfully!"
echo "Upload these files to: /root/projects/mySite/mySite/static/"
```

### Server Script: deploy_books.sh (Enhanced)
```bash
#!/bin/bash
# deploy_books.sh - Server-side deployment

set -e  # Exit on error

echo "Starting book files deployment..."

# Backup existing library_books if it exists
if [ -d "library_books" ]; then
    echo "Backing up existing library_books..."
    mv library_books "library_books_backup_$(date +%Y%m%d_%H%M%S)"
fi

# Create fresh directory
mkdir -p library_books

# Extract all zip files
for zip_file in library_books_*.zip; do
    if [ -f "$zip_file" ]; then
        echo "Extracting: $zip_file"
        unzip -o "$zip_file" -d library_books/
    fi
done

# Fix directory structure (in case of nested paths)
if [ -d "library_books/mySite/static/library_books" ]; then
    echo "Fixing directory structure..."
    mv library_books/mySite/static/library_books/* library_books/
    rm -rf library_books/mySite
fi

# Set proper permissions
echo "Setting permissions..."
chmod -R 755 library_books/
chown -R www-data:www-data library_books/ 2>/dev/null || true

# Verify deployment
echo "Verifying deployment..."
total_size=$(du -sh library_books/ | cut -f1)
category_count=$(find library_books/ -maxdepth 1 -type d | wc -l)

echo "Deployment completed successfully!"
echo "Total size: $total_size"
echo "Categories deployed: $((category_count-1))"

# List all categories
echo "Available categories:"
ls -la library_books/
```

## Verification Checklist

### Before Upload
- [ ] All zip files are under 500MB
- [ ] All categories are included in zip files
- [ ] Test extraction locally: `unzip -t library_books_*.zip`

### After Upload
- [ ] All zip files transferred to server
- [ ] Server has enough disk space for extraction
- [ ] Deployment script runs without errors

### After Deployment
- [ ] All categories present in `/root/projects/mySite/mySite/static/library_books/`
- [ ] Files are accessible via web interface
- [ ] No permission issues

## Troubleshooting

### Common Issues
1. **Zip file too large**: Use the split option: `zip -r -s 450m filename.zip directory/`
2. **Permission denied**: Run deployment script as root or with sudo
3. **Disk space**: Check available space: `df -h`
4. **Extraction errors**: Verify zip files aren't corrupted: `unzip -t filename.zip`

### Quick Commands
```bash
# Check server disk space
df -h /root/projects/mySite/

# Check file sizes on server
ls -lh library_books_*.zip

# Verify extraction
unzip -t library_books_part1.zip
```

This strategy ensures your 7.1GB of book files are properly split, uploaded, and deployed within the 500MB file size limit.
