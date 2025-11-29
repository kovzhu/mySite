#!/bin/bash
# deploy_books.sh - Server-side deployment

set -e  # Exit on error

echo "Starting book files deployment..."

# Check if we're in the right directory
CURRENT_DIR=$(pwd)
if [[ ! "$CURRENT_DIR" =~ "/root/projects/mySite/mySite/static" ]]; then
    echo "WARNING: You may not be in the correct directory."
    echo "Expected: /root/projects/mySite/mySite/static/"
    echo "Current: $CURRENT_DIR"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 1
    fi
fi

# Check available disk space
echo "Checking disk space..."
AVAILABLE_SPACE=$(df /root/projects/mySite/ | awk 'NR==2 {print $4}')
if [ "$AVAILABLE_SPACE" -lt 8000000 ]; then  # Less than 8GB
    echo "WARNING: Low disk space. Available: ${AVAILABLE_SPACE}KB"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 1
    fi
fi

# Backup existing library_books if it exists
if [ -d "library_books" ]; then
    BACKUP_NAME="library_books_backup_$(date +%Y%m%d_%H%M%S)"
    echo "Backing up existing library_books to $BACKUP_NAME..."
    mv library_books "$BACKUP_NAME"
    echo "✓ Backup created: $BACKUP_NAME"
fi

# Create fresh directory
mkdir -p library_books
echo "✓ Created fresh library_books directory"

# Extract all zip files
echo "Extracting zip files..."
ZIP_FILES=(library_books_*.zip*)
if [ ${#ZIP_FILES[@]} -eq 0 ]; then
    echo "ERROR: No library_books_*.zip files found in current directory!"
    echo "Make sure you've uploaded all zip files to: /root/projects/mySite/mySite/static/"
    exit 1
fi

for zip_file in "${ZIP_FILES[@]}"; do
    if [ -f "$zip_file" ]; then
        echo "Extracting: $zip_file"
        unzip -o "$zip_file" -d library_books/
        if [ $? -eq 0 ]; then
            echo "✓ Successfully extracted: $zip_file"
        else
            echo "✗ Failed to extract: $zip_file"
            echo "This might be a split archive part. Continuing..."
        fi
    fi
done

# Fix directory structure (in case of nested paths)
if [ -d "library_books/mySite/static/library_books" ]; then
    echo "Fixing directory structure (nested paths detected)..."
    mv library_books/mySite/static/library_books/* library_books/ 2>/dev/null || true
    rm -rf library_books/mySite
    echo "✓ Directory structure fixed"
fi

# Remove any empty directories that might have been created
find library_books/ -type d -empty -delete 2>/dev/null || true

# Set proper permissions
echo "Setting permissions..."
chmod -R 755 library_books/
# Try to set ownership to web server user (adjust as needed)
chown -R www-data:www-data library_books/ 2>/dev/null || chown -R nginx:nginx library_books/ 2>/dev/null || true
echo "✓ Permissions set"

# Verify deployment
echo "Verifying deployment..."
total_size=$(du -sh library_books/ | cut -f1)
category_count=$(find library_books/ -maxdepth 1 -type d | wc -l)
file_count=$(find library_books/ -type f | wc -l)

echo ""
echo "=== DEPLOYMENT COMPLETED SUCCESSFULLY ==="
echo "Total size: $total_size"
echo "Categories deployed: $((category_count-1))"
echo "Total files: $file_count"
echo ""
echo "Available categories:"
ls -la library_books/ | grep '^d' | awk '{print $9}' | grep -v '^\.'

# Check if all expected categories are present
EXPECTED_CATEGORIES=(
    "Biography" "China classical" "Economist" "General non-fiction" "History"
    "Humanistic and art" "Investing" "Kids Education" "Learning" "Literature"
    "Medical and health" "Philosophy and religion" "Politics" "Power BI"
    "Psychology and spiritual" "Python" "Science" "Social" "Work related"
)

echo ""
echo "Category verification:"
for category in "${EXPECTED_CATEGORIES[@]}"; do
    if [ -d "library_books/$category" ]; then
        echo "✓ $category"
    else
        echo "✗ $category (missing)"
    fi
done

echo ""
echo "Next steps:"
echo "1. Restart your web server if needed"
echo "2. Test book access through your website"
echo "3. Remove backup if everything works: rm -rf $BACKUP_NAME (if created)"
