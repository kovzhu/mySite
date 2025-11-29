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
    
    # Check if zip file is under 500MB
    zip_size=$(du -m "library_books_${safe_name}.zip" | cut -f1)
    if [ $zip_size -gt 500 ]; then
        echo "WARNING: $category zip file is ${zip_size}MB (over 500MB)"
        echo "Consider splitting this category manually"
    else
        echo "✓ $category: ${zip_size}MB"
    fi
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
    
    # Use zip with split option (creates multiple files like filename.z01, filename.z02, etc.)
    echo "Creating split zip files for $category (450MB chunks)..."
    zip -r -s 450m "library_books_${safe_name}.zip" "mySite/static/library_books/$category"
    
    # Count the number of split files created
    split_count=$(ls "library_books_${safe_name}.zip"* 2>/dev/null | wc -l)
    echo "✓ $category: Split into $split_count files"
done

echo ""
echo "All zip files created successfully!"
echo "Total files created: $(ls library_books_*.zip* 2>/dev/null | wc -l)"
echo ""
echo "Upload these files to: /root/projects/mySite/mySite/static/"
echo ""
echo "Verification commands:"
echo "  ls -lh library_books_*.zip*"
echo "  du -sh library_books_*.zip*"
