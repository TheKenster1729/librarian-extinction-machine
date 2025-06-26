# IP Webcam Book Processing Pipeline

This extension adds IP Webcam functionality to the book processing pipeline, allowing you to capture book title page images using your phone's camera and process them automatically through a complete workflow.

## Features

- **Complete automated workflow**: Capture → Extract → Classify → Add to Database → Cleanup
- **Simple command interface**: No admin privileges required
- **Automatic information extraction**: Extracts book information using GPT-4 Vision
- **Subject inference**: Automatically categorizes books based on your existing database subjects
- **Reading status selection**: Simple input (C/P/N) for reading status
- **Location tracking**: Add location information for each book
- **Database integration**: Adds processed books directly to your database
- **Automatic cleanup**: Deletes captured images to save space
- **Interactive mode**: Continuous operation with simple commands
- **Single capture mode**: Process one book at a time

## Complete Workflow

1. **Capture**: Use 'capture' command to capture book title page image
2. **Extract**: GPT-4 Vision extracts Title, Author, Publisher, Description
3. **Classify**: AI infers Subject and SpecificSubject categories
4. **Enhance**: Add Location (provided by user) and ReadingStatus (user selects)
5. **Store**: Add complete book record to database
6. **Cleanup**: Delete image file to save space
7. **Repeat**: Ready for next book

## Prerequisites

### 1. IP Webcam App Setup

1. **Install IP Webcam** on your phone:
   - Android: [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam)
   - iOS: [IP Camera Lite](https://apps.apple.com/us/app/ip-camera-lite/id570912928)

2. **Configure IP Webcam**:
   - Open the app on your phone
   - Make sure your phone and computer are on the same WiFi network
   - Start the server (usually by tapping "Start server")
   - Note the URL displayed (e.g., `http://192.168.1.15:8080`)

### 2. Python Environment

Install required packages:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install requests pillow openai pymysql sqlalchemy pandas imagehash pyzbar
```

### 3. Database Setup

Ensure your database is running and accessible. The pipeline supports:
- MySQL
- PostgreSQL  
- SQLite

## Usage

### Quick Start

1. **Update the configuration** in `example_usage.py`:
   ```python
   IP_WEBCAM_URL = "http://YOUR_PHONE_IP:8080"  # Replace with your phone's IP
   LOCATION = "Your Location"  # e.g., "Home Office", "Living Room", etc.
   ```

2. **Run the example script**:
   ```bash
   python example_usage.py
   ```

3. **Choose operation mode**:
   - **Interactive mode**: Use commands to capture and process books
   - **Single capture**: Process one book at a time
   - **Test connection**: Verify IP Webcam is working

4. **Reading Status Selection**:
   - **C**: Complete
   - **P**: Partially Complete
   - **N**: Not Started

### Programmatic Usage

```python
from utils import FullPipeline

# Initialize pipeline
pipeline = FullPipeline(
    ip_webcam_url="http://192.168.1.15:8080",
    location="Home Office",  # Book location
    db_password="your_password"
)

# Interactive mode
pipeline.run_interactive_mode()

# Or single capture
result = pipeline.run_single_capture()

# Or run complete workflow manually
result = pipeline.process_complete_book_workflow()
```

## Interactive Commands

When running in interactive mode, you can use these commands:

- **`capture`** - Capture and process a book title page
- **`test`** - Test IP Webcam connection
- **`quit`** - Exit the program

### Example Interactive Session

```
Starting interactive book processing mode...
Commands:
  'capture' - Capture and process a book
  'test' - Test IP Webcam connection
  'quit' - Exit the program
--------------------------------------------------

Enter command (capture/test/quit): test

Testing IP Webcam connection...
Requesting image from: http://192.168.1.15:8080/shot.jpg
Image captured and saved to: captured_images/captured_20231201_143022.jpg
✓ Connection successful! Image saved to: captured_images/captured_20231201_143022.jpg
✓ Deleted image: captured_images/captured_20231201_143022.jpg

Enter command (capture/test/quit): capture

Position a book title page in front of the camera...
Press Enter when ready to capture...

============================================================
STARTING COMPLETE BOOK PROCESSING WORKFLOW
============================================================

Step 1: Capturing image...
Requesting image from: http://192.168.1.15:8080/shot.jpg
Image captured and saved to: captured_images/captured_20231201_143025.jpg

Step 2: Extracting book information...
Extracting information from title page...
Successfully extracted book information:
{
  "Title": "The Great Gatsby",
  "Author": "F. Scott Fitzgerald",
  "Publisher": "Scribner",
  "Description": "A story of the Jazz Age and the American Dream"
}

Step 3: Inferring subjects...
Inferring subjects...
Successfully inferred subjects:
{
  "Subject": "Literature",
  "SpecificSubject": "American Literature"
}

Step 4: Merging information...
Added location: Home Office

Step 5: Getting reading status...
Select reading status:
  C - Complete
  P - Partially Complete
  N - Not Started
Enter C, P, or N: c
Selected: Complete

Step 6: Final book information:
----------------------------------------
Title: The Great Gatsby
Author: F. Scott Fitzgerald
Publisher: Scribner
Description: A story of the Jazz Age and the American Dream
Subject: Literature
SpecificSubject: American Literature
Location: Home Office
ReadingStatus: Complete
----------------------------------------

Step 7: Adding to database...
✓ Successfully added to database!

Step 8: Cleaning up...
✓ Deleted image: captured_images/captured_20231201_143025.jpg

============================================================
WORKFLOW COMPLETED SUCCESSFULLY!
============================================================

Ready for next book.

Enter command (capture/test/quit): quit

Exiting...
```

## API Reference

### FullPipeline Class

#### Constructor Parameters

- `ip_webcam_url` (str): URL of your IP Webcam server
- `location` (str): Location where books are stored
- `db_password` (str): Database password
- `db_type` (str): Database type ("mysql", "postgresql", "sqlite")
- `host` (str): Database host
- `port` (int): Database port
- `username` (str): Database username
- `database` (str): Database name

#### Methods

- `run_interactive_mode()`: Start interactive capture mode
- `run_single_capture()`: Capture and process one image
- `process_complete_book_workflow()`: Run the complete workflow
- `capture_image_from_webcam()`: Capture image from IP Webcam
- `process_captured_image(image_path)`: Extract book information from image
- `infer_subjects(book_info)`: Infer subject categories
- `get_reading_status_from_user()`: Get reading status via input
- `add_book_to_database(complete_book_info)`: Add book to database
- `cleanup_image(image_path)`: Delete image file

## Workflow Details

### Step 1: Image Capture
- Use 'capture' command to trigger capture
- Image is saved with timestamp: `captured_YYYYMMDD_HHMMSS.jpg`
- Automatic error handling for connection issues

### Step 2: Information Extraction
- GPT-4 Vision analyzes the title page
- Extracts: Title, Author, Publisher, Description
- Handles multiple authors and contributors (editors, translators, etc.)

### Step 3: Subject Classification
- AI infers Subject and SpecificSubject based on your existing database
- Uses your current subject categories for consistency

### Step 4: User Input
- **Location**: Automatically added from class initialization
- **Reading Status**: User selects via input:
  - `C` → Complete
  - `P` → Partially Complete  
  - `N` → Not Started

### Step 5: Database Update
- Merges all information into complete record
- Adds to database with auto-incremented ID
- Provides success/failure feedback

### Step 6: Cleanup
- Deletes captured image file to save disk space
- Ready for next book

## File Structure

```
├── utils.py                 # Main pipeline code
├── example_usage.py         # Example usage script
├── requirements.txt         # Python dependencies
├── README_IP_WEBCAM.md      # This file
└── captured_images/         # Temporary directory (auto-created)
    └── (images deleted after processing)
```

## Troubleshooting

### Connection Issues

1. **Check IP address**: Ensure you're using the correct IP address from your phone
2. **Network connectivity**: Verify phone and computer are on same network
3. **Firewall**: Check if firewall is blocking the connection
4. **App settings**: Make sure IP Webcam server is running

### Database Issues

1. **Connection**: Verify database credentials and connectivity
2. **Schema**: Ensure your database has the required `master_table`
3. **Permissions**: Check database user permissions

### Image Processing Issues

1. **Image quality**: Ensure good lighting and clear text
2. **Camera focus**: Make sure text is in focus
3. **API key**: Verify OpenAI API key is set in environment variables

## Environment Variables

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Customization

### Change Location

```python
pipeline = FullPipeline(
    ip_webcam_url="http://192.168.1.15:8080",
    location="Living Room"  # Change location
)
```

### Custom Reading Status Options

```python
# Modify the reading_status_options dictionary in the class
pipeline.reading_status_options = {
    'c': 'Complete',
    'p': 'Partially Complete',
    'n': 'Not Started',
    'r': 'Reading Now'  # Add custom status
}
```

### Custom Image Directory

```python
pipeline.captured_images_dir = "my_custom_directory"
```

### Different IP Webcam Endpoints

If your IP Webcam app uses different endpoints:

```python
# Modify the capture URL in capture_image_from_webcam method
capture_url = f"{self.ip_webcam_url}/capture"  # Instead of /shot.jpg
```

## Security Notes

- IP Webcam is typically unsecured - only use on trusted networks
- Consider using HTTPS if your IP Webcam app supports it
- Be aware that captured images are stored temporarily then deleted
- Ensure your OpenAI API key is kept secure

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Test with the connection test mode first
4. Check the console output for error messages 