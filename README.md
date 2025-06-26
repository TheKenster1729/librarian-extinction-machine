# Librarian Extinction Machine

An automated book processing pipeline that uses computer vision and AI to catalog books by simply taking a photo of their title page. This system eliminates the need for manual data entry when building your personal library database.

## 🚀 Features

- **📸 Smart Image Capture**: Use your phone as a webcam to capture book title pages
- **🤖 AI-Powered Extraction**: GPT-4 Vision automatically extracts book metadata (title, author, publisher, description)
- **📚 Intelligent Classification**: AI infers subject categories based on your existing database
- **🗄️ Database Integration**: Seamlessly adds books to MySQL, PostgreSQL, or SQLite databases
- **📍 Location Tracking**: Organize books by physical location
- **📖 Reading Status**: Track your reading progress (Complete/Partially Complete/Not Started)
- **🔄 Automated Workflow**: Complete pipeline from capture to database entry
- **🧹 Automatic Cleanup**: Deletes images after processing to save space

## 🛠️ Prerequisites

### 1. IP Webcam Setup
- **Android**: Install [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam)
- **iOS**: Install [IP Camera Lite](https://apps.apple.com/us/app/ip-camera-lite/id570912928)
- Ensure your phone and computer are on the same WiFi network
- I haven't tested this on Windows, so use at your own risk

### 2. Python Environment
```bash
pip install -r requirements.txt
```

### 3. Database Setup
The system supports:
- MySQL
- PostgreSQL
- SQLite

### 4. OpenAI API Key
You'll need an OpenAI API key for GPT-4 Vision functionality. Store it as an environment variable called `OPENAI_API_KEY`.

## 🚀 Quick Start

1. **Configure your setup** in `example_usage.py`:
   ```python
   IP_WEBCAM_URL = "http://YOUR_PHONE_IP:8080"  # Your phone's IP address
   LOCATION = "Home Office"  # Book location
   ```

2. **Start IP Webcam** on your phone and note the URL

3. **Run the pipeline**:
   ```bash
   python example_usage.py
   ```

4. **Choose your mode**:
   - **Interactive**: Continuous book processing
   - **Single Capture**: Process one book at a time
   - **Test Connection**: Verify setup

## 📖 Usage Examples

### Interactive Mode
```python
from utils import FullPipeline

pipeline = FullPipeline(
    ip_webcam_url="http://192.168.1.15:8080",
    location="Home Office",
    db_password="your_password"
)

# Start interactive processing
pipeline.run_interactive_mode()
```

### Single Book Processing
```python
# Process one book
result = pipeline.run_single_capture()
if result:
    print("Book added successfully!")
    print(f"Title: {result['Title']}")
    print(f"Author: {result['Author']}")
```

### Complete Workflow
```python
# Run the full pipeline manually
result = pipeline.process_complete_book_workflow()
```

## 🔧 Configuration

### Database Configuration
```python
DB_CONFIG = {
    "db_type": "mysql",  # or "postgresql", "sqlite"
    "host": "localhost",
    "port": 3306,
    "username": "root",
    "password": "your_password",
    "database": "booklog"
}
```

### Reading Status Options
- **C**: Complete
- **P**: Partially Complete  
- **N**: Not Started

## 📁 Project Structure

```
librarian-extinction-machine/
├── utils.py              # Core pipeline functionality
├── example_usage.py      # Main usage examples
├── requirements.txt      # Python dependencies
├── captured_images/     # Temporary image storage
├── test_*.py           # Test files
└── README_IP_WEBCAM.md # Detailed IP Webcam guide
```

## 🔍 How It Works

1. **Capture**: Take photo of book title page using phone camera
2. **Extract**: GPT-4 Vision analyzes image and extracts metadata
3. **Classify**: AI infers subject categories from existing database
4. **Enhance**: Add location and reading status
5. **Store**: Save complete record to database
6. **Cleanup**: Delete image file
7. **Repeat**: Ready for next book

## 🐛 Troubleshooting

### IP Webcam Connection Issues
- Ensure phone and computer are on same network
- Check firewall settings
- Verify IP address is correct
- Try restarting IP Webcam app

### Database Connection Issues
- Verify database credentials
- Check if database server is running
- Ensure database exists and is accessible

### OpenAI API Issues
- Verify API key is valid and has credits
- Check internet connection
- Ensure API key is in `api_key.txt`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 Vision API
- IP Webcam developers for mobile camera integration
- Sam Altman and Dario Amodei

---
