#!/usr/bin/env python3
"""
Example usage of the FullPipeline class with IP Webcam functionality.

This script demonstrates the complete workflow:
1. Capture image of book title page
2. Extract book information using GPT-4 Vision
3. Infer subject categories
4. Add location (provided by user)
5. Select reading status (C/P/N keys)
6. Add to database
7. Delete image to save space
8. Ready for next book

Prerequisites:
1. Install IP Webcam app on your phone
2. Connect your phone and computer to the same network
3. Start IP Webcam and note the URL (e.g., http://192.168.1.15:8080)
4. Install required Python packages: pip install keyboard requests pillow openai
"""

from utils import FullPipeline

def main():
    # Configuration
    # Replace with your actual IP Webcam URL
    IP_WEBCAM_URL = "http://192.168.1.15:8080"  # Update this with your phone's IP
    
    # Database configuration (update as needed)
    DB_CONFIG = {
        "db_type": "mysql",
        "host": "localhost",
        "port": 3306,
        "username": "root",
        "password": "",  # Update with your database password
        "database": "booklog"
    }
    
    # Location for books (customize as needed)
    LOCATION = "Home Office"  # e.g., "Living Room", "Bedroom", "Office", etc.
    
    print("Book Processing Pipeline with IP Webcam")
    print("=" * 60)
    print(f"IP Webcam URL: {IP_WEBCAM_URL}")
    print(f"Location: {LOCATION}")
    print("Make sure your phone is running IP Webcam and is accessible at this URL.")
    print()
    
    # Initialize the pipeline
    try:
        pipeline = FullPipeline(
            ip_webcam_url=IP_WEBCAM_URL,
            capture_key="space",  # Press spacebar to capture
            location=LOCATION,
            db_password=DB_CONFIG["password"]
        )
        print("Pipeline initialized successfully!")
        print()
        
        # Choose operation mode
        print("Choose operation mode:")
        print("1. Interactive mode (press spacebar to capture, 'q' to quit)")
        print("2. Single capture mode")
        print("3. Test connection only")
        print()
        print("Reading Status Options:")
        print("  C - Complete")
        print("  P - Partially Complete")
        print("  N - Not Started")
        print()
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            # Interactive mode
            print("\nStarting interactive mode...")
            print("Instructions:")
            print("- Press SPACEBAR to capture an image of a book title page")
            print("- Press 'q' to quit")
            print("- Make sure the book title page is clearly visible in the camera")
            print("- After capture, press C/P/N to select reading status")
            print("- The system will automatically process and add to database")
            print()
            
            pipeline.run_interactive_mode()
            
        elif choice == "2":
            # Single capture mode
            print("\nSingle capture mode...")
            print("Position a book title page in front of the camera and press Enter...")
            input("Press Enter when ready to capture...")
            
            result = pipeline.run_single_capture()
            if result:
                print("\nBook processing completed successfully!")
                print("Final book information:")
                for key, value in result.items():
                    print(f"  {key}: {value}")
            else:
                print("\nBook processing failed.")
                
        elif choice == "3":
            # Test connection
            print("\nTesting IP Webcam connection...")
            image_path = pipeline.capture_image_from_webcam()
            if image_path:
                print(f"✓ Connection successful! Image saved to: {image_path}")
                # Clean up test image
                pipeline.cleanup_image(image_path)
            else:
                print("✗ Connection failed. Please check:")
                print("  - IP Webcam app is running on your phone")
                print("  - URL is correct")
                print("  - Phone and computer are on the same network")
                print("  - Firewall settings allow the connection")
        else:
            print("Invalid choice. Exiting.")
            
    except Exception as e:
        print(f"Error initializing pipeline: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure all required packages are installed:")
        print("   pip install keyboard requests pillow openai pymysql sqlalchemy")
        print("2. Check your database connection settings")
        print("3. Verify your IP Webcam URL is correct")
        print("4. Ensure your phone and computer are on the same network")

def demonstrate_workflow():
    """
    Demonstrate the complete workflow step by step.
    """
    print("Complete Workflow Demonstration")
    print("=" * 50)
    
    # Initialize pipeline
    pipeline = FullPipeline(
        ip_webcam_url="http://192.168.1.15:8080",
        location="Demo Location",
        db_password=""
    )
    
    print("Workflow steps:")
    print("1. Capture image from IP Webcam")
    print("2. Extract book information (Title, Author, Publisher, Description)")
    print("3. Infer subject categories")
    print("4. Add location: Demo Location")
    print("5. Get reading status from user (C/P/N)")
    print("6. Merge all information")
    print("7. Add to database")
    print("8. Delete image to save space")
    print("9. Ready for next book")
    print()
    
    input("Press Enter to start the workflow...")
    
    # Run the complete workflow
    result = pipeline.process_complete_book_workflow()
    
    if result:
        print("\nWorkflow completed successfully!")
    else:
        print("\nWorkflow failed.")

if __name__ == "__main__":
    # Uncomment the line below to run the demonstration
    # demonstrate_workflow()
    
    # Run the main interactive script
    main() 