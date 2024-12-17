#!/bin/bash

# Display usage instructions for the script
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <url_list_file> <download_directory>"
  exit 1
fi

URL_FILE="$1"
DOWNLOAD_DIR="$2/downloaded"  # Set download directory to 'downloaded' folder
EXTRACTED_DIR="$2/extracted"  # Set extraction directory to 'extracted' folder

# Check if the URL list file exists
if [ ! -f "$URL_FILE" ]; then
  echo "Error: URL list file '$URL_FILE' does not exist."
  exit 1
fi

# Check if the download directory exists; create it if it does not
if [ ! -d "$DOWNLOAD_DIR" ]; then
  echo "Directory does not exist. Creating: $DOWNLOAD_DIR"
  mkdir -p "$DOWNLOAD_DIR"
fi

# Check if the extraction directory exists; create it if it does not
if [ ! -d "$EXTRACTED_DIR" ]; then
  echo "Directory does not exist. Creating: $EXTRACTED_DIR"
  mkdir -p "$EXTRACTED_DIR"
fi

# Read URLs from the file and download them
while IFS= read -r URL || [ -n "$URL" ]; do
  if [ -n "$URL" ]; then # Skip empty lines
    FILENAME=$(basename "$URL")
    echo "Downloading $FILENAME..."
    curl -o "$DOWNLOAD_DIR/$FILENAME" "$URL"
  fi
done < "$URL_FILE"

# Extract tar.gz files to the extracted directory
echo "Extracting tar.gz files..."
for TAR_FILE in "$DOWNLOAD_DIR"/*.tar.gz; do
  if [ -f "$TAR_FILE" ]; then
    echo "Extracting $TAR_FILE..."
    tar -xzf "$TAR_FILE" -C "$EXTRACTED_DIR"
  fi
done

echo "All files downloaded to $DOWNLOAD_DIR and extracted to $EXTRACTED_DIR."
