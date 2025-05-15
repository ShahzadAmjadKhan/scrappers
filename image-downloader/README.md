# Image Downloader

A Python-based tool that downloads all images from a specified website, supporting multiple image formats and parallel processing.

## Overview

This tool automates the process of downloading images from websites, handling various image formats including SVG, JPG, PNG, GIF, and base64 encoded images. It uses parallel processing for improved performance.

## Features

- Multi-format image support
- Base64 image decoding
- SVG content extraction
- Parallel download processing
- Automatic file naming
- Directory organization

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd image-downloader
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the downloader:
```bash
python image.py "https://example.com"
```

The script will:
1. Visit the specified website
2. Parse the HTML content
3. Identify all image resources
4. Download images in parallel
5. Save them to the `images` folder

## Supported Image Types

The downloader handles:
- SVG (both inline and linked)
- JPG/JPEG
- PNG
- GIF
- Base64 encoded images

## Image Processing

### Base64 Images
- Detects base64 encoded images in `src` attributes
- Extracts content-type for proper file extension
- Decodes and saves to file

### SVG Processing
- Extracts inline SVG tag content
- Downloads linked SVG files
- Preserves SVG markup

### URL-based Images
- Downloads images from external URLs
- Preserves original file names when possible
- Handles various URL formats

## Technologies Used

- **Python**: Core programming language
- **Requests**: HTTP communication
- **BeautifulSoup4**: HTML parsing
- **multiprocessing**: Parallel download handling

## Error Handling

The downloader includes error handling for:
- Network connectivity issues
- Invalid URLs
- Failed downloads
- Malformed base64 data
- File system operations

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is open-source and available under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Please ensure you have permission to download images from target websites.
