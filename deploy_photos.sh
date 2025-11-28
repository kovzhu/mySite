#!/bin/bash

# Photo Deployment Script for mySite
# This script helps manage photo files separately from code deployment

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== mySite Photo Deployment Script ===${NC}"

# Function to display usage
usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  zip-all           - Create zip files for all photo directories"
    echo "  zip-gallery       - Create zip file for gallery photos only"
    echo "  zip-collections   - Create zip file for collection photos only"
    echo "  list-photos       - Show photo directories and their sizes"
    echo "  clean-zips        - Remove all zip files"
    echo "  help              - Show this help message"
    echo ""
    echo "Example: $0 zip-all"
}

# Function to check if directory exists and has files
check_directory() {
    local dir=$1
    if [ -d "$dir" ] && [ "$(ls -A "$dir" 2>/dev/null)" ]; then
        return 0
    else
        return 1
    fi
}

# Function to get directory size
get_dir_size() {
    local dir=$1
    if [ -d "$dir" ]; then
        du -sh "$dir" 2>/dev/null | cut -f1
    else
        echo "0B"
    fi
}

# Function to list all photo directories
list_photos() {
    echo -e "${YELLOW}Photo directories and their sizes:${NC}"
    echo ""
    
    local directories=(
        "mySite/static/gallery_images"
        "mySite/static/book_photos"
        "mySite/static/exercise_photos"
        "mySite/static/reading_quote_photos"
        "mySite/static/intellectual_photos"
        "mySite/static/fragmented_quote_photos"
        "mySite/static/guitar_photos"
        "mySite/static/guitar_videos"
        "mySite/static/collection_images"
        "mySite/static/collection_videos"
        "mySite/static/personal_images"
        "mySite/static/project_images"
        "mySite/static/blog_media"
    )
    
    local total_size=0
    
    for dir in "${directories[@]}"; do
        if check_directory "$dir"; then
            size=$(get_dir_size "$dir")
            echo -e "${GREEN}✓${NC} $dir - $size"
            # Extract numeric part for calculation
            numeric_size=$(echo "$size" | sed 's/[^0-9.]//g')
            unit=$(echo "$size" | sed 's/[0-9.]//g')
            
            # Convert to bytes for rough total
            case $unit in
                "K") numeric_size=$(echo "$numeric_size * 1024" | bc) ;;
                "M") numeric_size=$(echo "$numeric_size * 1024 * 1024" | bc) ;;
                "G") numeric_size=$(echo "$numeric_size * 1024 * 1024 * 1024" | bc) ;;
                *) numeric_size=$(echo "$numeric_size" | bc) ;;
            esac
            
            total_size=$(echo "$total_size + $numeric_size" | bc)
        else
            echo -e "${RED}✗${NC} $dir - Empty or not found"
        fi
    done
    
    echo ""
    echo -e "${YELLOW}Total estimated size: $(echo "scale=2; $total_size / (1024*1024)" | bc) MB${NC}"
}

# Function to create zip files
create_zip() {
    local name=$1
    local directories=("${@:2}")
    
    echo -e "${BLUE}Creating $name zip file...${NC}"
    
    local zip_file="${name}_photos_$(date +%Y%m%d_%H%M%S).zip"
    local temp_dir="temp_${name}_$(date +%s)"
    
    mkdir -p "$temp_dir"
    
    for dir in "${directories[@]}"; do
        if check_directory "$dir"; then
            echo "Adding: $dir"
            # Copy directory structure
            cp -r "$dir" "$temp_dir/" 2>/dev/null || true
        fi
    done
    
    # Create zip file
    if [ "$(ls -A "$temp_dir" 2>/dev/null)" ]; then
        zip -r "$zip_file" "$temp_dir" > /dev/null
        zip_size=$(get_dir_size "$zip_file")
        echo -e "${GREEN}✓ Created: $zip_file ($zip_size)${NC}"
    else
        echo -e "${RED}✗ No files found to zip${NC}"
    fi
    
    # Clean up
    rm -rf "$temp_dir"
}

# Function to zip all photos
zip_all() {
    echo -e "${YELLOW}Creating zip file with ALL photos...${NC}"
    
    local all_directories=(
        "mySite/static/gallery_images"
        "mySite/static/book_photos"
        "mySite/static/exercise_photos"
        "mySite/static/reading_quote_photos"
        "mySite/static/intellectual_photos"
        "mySite/static/fragmented_quote_photos"
        "mySite/static/guitar_photos"
        "mySite/static/guitar_videos"
        "mySite/static/collection_images"
        "mySite/static/collection_videos"
        "mySite/static/personal_images"
        "mySite/static/project_images"
        "mySite/static/blog_media"
    )
    
    create_zip "all" "${all_directories[@]}"
}

# Function to zip gallery photos only
zip_gallery() {
    echo -e "${YELLOW}Creating zip file with gallery photos only...${NC}"
    
    local gallery_directories=(
        "mySite/static/gallery_images"
    )
    
    create_zip "gallery" "${gallery_directories[@]}"
}

# Function to zip collection photos only
zip_collections() {
    echo -e "${YELLOW}Creating zip file with collection photos only...${NC}"
    
    local collection_directories=(
        "mySite/static/book_photos"
        "mySite/static/exercise_photos"
        "mySite/static/reading_quote_photos"
        "mySite/static/intellectual_photos"
        "mySite/static/fragmented_quote_photos"
        "mySite/static/guitar_photos"
        "mySite/static/collection_images"
    )
    
    create_zip "collections" "${collection_directories[@]}"
}

# Function to clean zip files
clean_zips() {
    echo -e "${YELLOW}Cleaning up zip files...${NC}"
    
    local zip_files=$(find . -name "*.zip" -type f)
    
    if [ -n "$zip_files" ]; then
        echo "Removing zip files:"
        echo "$zip_files"
        rm -f *.zip
        echo -e "${GREEN}✓ All zip files removed${NC}"
    else
        echo -e "${YELLOW}No zip files found${NC}"
    fi
}

# Main script logic
case "${1:-help}" in
    "zip-all")
        zip_all
        ;;
    "zip-gallery")
        zip_gallery
        ;;
    "zip-collections")
        zip_collections
        ;;
    "list-photos")
        list_photos
        ;;
    "clean-zips")
        clean_zips
        ;;
    "help"|"-h"|"--help")
        usage
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        usage
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}=== Deployment Instructions ===${NC}"
echo "1. Push code changes to GitHub:"
echo "   git add ."
echo "   git commit -m 'Update photo viewing interface'"
echo "   git push origin main"
echo ""
echo "2. Deploy photos to server:"
echo "   - Upload the generated zip file to your server"
echo "   - Unzip in the project directory: unzip [filename].zip"
echo "   - Ensure photos are in mySite/static/ directory"
echo ""
echo -e "${GREEN}Done!${NC}"
