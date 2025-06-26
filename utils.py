import requests
from typing import Optional
import pandas as pd
import os
from sqlalchemy import create_engine, text

import base64
import sys
import openai
import json
from datetime import datetime

class DatabaseUtils:
    def __init__(self, db_type: str = "mysql", 
                 host: str = "localhost", port: int = 3306, 
                 username: str = "root", password: str = "", 
                 database: str = "booklog"):
        self.db_type = db_type
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        
        # Load the database as a pandas dataframe
        self.db_as_df = self.load_master_table()
        
        self.subjects_list = self.get_subjects_list()
        self.subjects_specific_list = self.get_subjects_specific_list()

    def load_master_table(self) -> pd.DataFrame:
        """
        Connect to the SQL database and load the 'master_table' 
        as a pandas dataframe.
        
        Returns:
            pd.DataFrame: The master_table as a pandas dataframe
        """
        try:
            # Create database connection string based on type
            if self.db_type.lower() == "mysql":
                connection_string = f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            elif self.db_type.lower() == "postgresql":
                connection_string = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            elif self.db_type.lower() == "sqlite":
                connection_string = f"sqlite:///{self.database}.db"
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            # Create engine and connect
            engine = create_engine(connection_string)
            
            # Load the master_table as a pandas dataframe
            df = pd.read_sql_query("SELECT * FROM master_table", engine)
            
            # Close the connection
            engine.dispose()
            
            print(f"Successfully loaded master_table with {len(df)} rows and {len(df.columns)} columns")
            return df
            
        except Exception as e:
            print(f"Error loading database: {e}")
            print(f"Database connection details: {self.db_type}://{self.username}@{self.host}:{self.port}/{self.database}")
            return pd.DataFrame()

    def clean_database(self) -> bool:
        """
        Clean the ReadingStatus column by removing "\r" characters from the end of entries.
        Updates the database directly and should only be run once.
        
        Returns:
            bool: True if cleaning was successful, False otherwise
        """
        try:
            # Check if ReadingStatus column exists
            if 'ReadingStatus' not in self.db_as_df.columns:
                print("Warning: ReadingStatus column not found in the database.")
                return False
            
            # Create database connection string based on type
            if self.db_type.lower() == "mysql":
                connection_string = f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            elif self.db_type.lower() == "postgresql":
                connection_string = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            elif self.db_type.lower() == "sqlite":
                connection_string = f"sqlite:///{self.database}.db"
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            # Create engine and connect
            engine = create_engine(connection_string)
            
            # Find entries that need cleaning (have "\r" at the end)
            dirty_entries = self.db_as_df[
                self.db_as_df['ReadingStatus'].notna() & 
                self.db_as_df['ReadingStatus'].astype(str).str.endswith('\r')
            ]
            
            if len(dirty_entries) == 0:
                print("No entries found with '\\r' characters at the end of ReadingStatus.")
                engine.dispose()
                return True
            
            print(f"Found {len(dirty_entries)} entries with '\\r' characters to clean.")
            
            # Update each dirty entry in the database
            cleaned_count = 0
            with engine.connect() as conn:
                for index, row in dirty_entries.iterrows():
                    # Get the primary key or unique identifier
                    # Assuming there's an 'id' column, adjust as needed
                    if 'id' in row:
                        primary_key = row['id']
                        primary_key_col = 'id'
                    elif 'ID' in row:
                        primary_key = row['ID']
                        primary_key_col = 'ID'
                    else:
                        # If no obvious primary key, use the index
                        primary_key = index
                        primary_key_col = 'id'  # Adjust based on your actual primary key column name
                    
                    # Clean the ReadingStatus value
                    cleaned_status = row['ReadingStatus'].rstrip('\r')
                    
                    # Update the database
                    if self.db_type.lower() == "mysql":
                        update_query = f"UPDATE master_table SET ReadingStatus = :status WHERE {primary_key_col} = :pk"
                        conn.execute(text(update_query), {"status": cleaned_status, "pk": primary_key})
                    elif self.db_type.lower() == "postgresql":
                        update_query = f"UPDATE master_table SET ReadingStatus = :status WHERE {primary_key_col} = :pk"
                        conn.execute(text(update_query), {"status": cleaned_status, "pk": primary_key})
                    elif self.db_type.lower() == "sqlite":
                        update_query = f"UPDATE master_table SET ReadingStatus = :status WHERE {primary_key_col} = :pk"
                        conn.execute(text(update_query), {"status": cleaned_status, "pk": primary_key})
                    
                    cleaned_count += 1
                
                # Commit the changes
                conn.commit()
            
            # Close the connection
            engine.dispose()
            
            # Reload the dataframe to reflect changes
            self.db_as_df = self.load_master_table()
            
            print(f"Successfully cleaned {cleaned_count} entries in the ReadingStatus column.")
            return True
            
        except Exception as e:
            print(f"Error cleaning database: {e}")
            return False

    def get_subjects_list(self):
        return self.db_as_df["Subject"].unique()
    
    def get_subjects_specific_list(self):
        return self.db_as_df["SubjectSpecific"].unique()

    def add_to_database(self, complete_book_info: dict):
        """
        Add a new book record to the database with an auto-incremented ID.

        Args:
            complete_book_info (dict): Dictionary containing book information with keys
                                     matching the database columns (excluding ID)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Determine the next ID by finding the maximum ID in the existing database
            if len(self.db_as_df) == 0:
                next_id = 1
            else:
                # Check for different possible ID column names
                id_column = "id"
                if id_column and id_column in self.db_as_df.columns:
                    next_id = self.db_as_df[id_column].max() + 1
                else:
                    next_id = len(self.db_as_df) + 1

            # Create database connection string based on type
            if self.db_type.lower() == "mysql":
                connection_string = f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            elif self.db_type.lower() == "postgresql":
                connection_string = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            elif self.db_type.lower() == "sqlite":
                connection_string = f"sqlite:///{self.database}.db"
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            # Create engine and connect
            engine = create_engine(connection_string)
            
            # Get the column names from the database
            with engine.connect() as conn:
                # Get table schema to understand column names
                if self.db_type.lower() == "mysql":
                    result = conn.execute(text("DESCRIBE master_table"))
                elif self.db_type.lower() == "postgresql":
                    result = conn.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'master_table' 
                        ORDER BY ordinal_position
                    """))
                elif self.db_type.lower() == "sqlite":
                    result = conn.execute(text("PRAGMA table_info(master_table)"))
                
                columns = [row[0] for row in result]
            
            # Prepare the data for insertion
            # Start with the next ID
            insert_data = {'id': next_id} if 'id' in columns else {'ID': next_id}
            
            # Add the book information, mapping keys to database columns
            for key, value in complete_book_info.items():
                # Handle different possible column name variations
                if key.lower() in [col.lower() for col in columns]:
                    # Find the exact column name (case-insensitive match)
                    exact_col = next(col for col in columns if col.lower() == key.lower())
                    insert_data[exact_col] = value
                elif key in columns:
                    insert_data[key] = value
            
            # Create the INSERT query
            column_names = list(insert_data.keys())
            placeholders = [f":{col}" for col in column_names]
            
            insert_query = f"""
                INSERT INTO master_table ({', '.join(column_names)})
                VALUES ({', '.join(placeholders)})
            """
            
            # Execute the insert
            with engine.connect() as conn:
                conn.execute(text(insert_query), insert_data)
                conn.commit()
            
            # Close the connection
            engine.dispose()
            
            # Reload the dataframe to reflect changes
            self.db_as_df = self.load_master_table()
            
            print(f"Successfully added book '{complete_book_info.get('Title', 'Unknown')}' to database with ID {next_id}")
            return True
            
        except Exception as e:
            print(f"Error adding book to database: {e}")
            return False

class InformationExtractor:
    def __init__(self, image_path: str):
        self.MODEL_NAME = "gpt-4.1"
        self.IMAGE_FILE = image_path
        self.IMAGE_DETAIL = "auto" # "low", "auto" (default), or "high"

    def load_image_as_data_uri(self, path: str) -> str:
        """Read `path` and return a data-URI string suitable for the API."""
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/jpg;base64,{b64}"

    def extract_information_from_title_page(self):
        prompt = "This is an image of a title page of a book."
        sys_msg = """You are an expert bibliographic extractor.  
        When the user shows you a book title page image, return ONLY a JSON object with all text exactly as printed and any visible numeric identifiers.  
        Use None if an element is not identifiable. For authors, include all contributers and an abbreviation of their role, e.g. ed. for the editor, trans. for the translator, etc. The JSON object should be in the following format:
        {
            "Title": "The title of the book",
            "Author": "The author and other contributors of the book",
            "Publisher": "The publisher of the book",
            "Description": "A short description of the book",
        }
        Please infer the description from your knowledge of the book. If you cannot, then return None.
        """

        try:
            img_data_uri = self.load_image_as_data_uri(self.IMAGE_FILE)
        except FileNotFoundError:
            sys.exit(f"Error: '{self.IMAGE_FILE}' not found.")

        client = openai.OpenAI()  # uses OPENAI_API_KEY env var

        response1 = client.chat.completions.create(
            model=self.MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": sys_msg,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": img_data_uri,
                                "detail": self.IMAGE_DETAIL,
                            },
                        },
                    ],
                }
            ],
            temperature=0.2,
        )

        return response1.choices[0].message.content
    
    def infer_subject_and_specific_subject(self, book_info: dict, subjects_list: list, subjects_specific_list: list):
        prompt = f"""Given the following subjects and specific subjects, and information about a book, infer the subject and specific subject of the book. Subjects: {subjects_list}. Specific Subjects: {subjects_specific_list}. If you believe the book
        does not fit into any of the subjects, then return None.
        """
        sys_msg = """You are an expert bibliographic subject and specific subject classifier.  
        When the user gives you a JSON object with the title, author, publisher, and description of a book, infer the subject and specific subject of the book and return a JSON object with the following format:
        {
            "Subject": "The subject of the book",
            "SubjectSpecific": "The specific subject of the book",
        }
        """
        client = openai.OpenAI()  # uses OPENAI_API_KEY env var

        response1 = client.chat.completions.create(
            model=self.MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": sys_msg,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "text",
                            "text": book_info,
                        },
                    ],
                }
            ],
            temperature=0.2,
        )

        return response1.choices[0].message.content

    def _fix_json_formatting(self, json_str: str) -> str:
        """
        Fix common JSON formatting issues from GPT-4 responses.
        
        Args:
            json_str (str): The JSON string to fix
            
        Returns:
            str: Fixed JSON string
        """
        # Remove trailing commas before closing braces
        lines = json_str.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # If this line ends with a comma and the next line is a closing brace, remove the comma
            if line.strip().endswith(',') and i + 1 < len(lines) and lines[i + 1].strip() == '}':
                line = line.rstrip(',')
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

class FullPipeline(DatabaseUtils, InformationExtractor):
    def __init__(self, db_password: str = "", image_path: str = None, 
                 ip_webcam_url: str = None, capture_key: str = "space", location = None):
        DatabaseUtils.__init__(self, password=db_password)
        InformationExtractor.__init__(self, image_path)
        
        # IP Webcam settings
        self.ip_webcam_url = ip_webcam_url
        self.capture_key = capture_key
        self.is_capturing = False
        self.captured_images_dir = "captured_images"
        self.location = location
        
        # Reading status options
        self.reading_status_options = {
            'c': 'Complete',
            'p': 'Partially Complete', 
            'n': 'Not Started'
        }
        
        # Create directory for captured images if it doesn't exist
        if not os.path.exists(self.captured_images_dir):
            os.makedirs(self.captured_images_dir)

    def capture_image_from_webcam(self) -> Optional[str]:
        """
        Capture an image from the IP Webcam and save it locally.
        
        Returns:
            str: Path to the captured image file, or None if failed
        """
        if not self.ip_webcam_url:
            print("Error: IP Webcam URL not configured.")
            return None
        
        try:
            # Construct the capture URL
            # IP Webcam typically uses /shot.jpg for capturing images
            capture_url = f"{self.ip_webcam_url}/shot.jpg"
            
            print(f"Requesting image from: {capture_url}")
            
            # Make the request to capture the image
            response = requests.get(capture_url, timeout=10)
            response.raise_for_status()
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captured_{timestamp}.jpg"
            filepath = os.path.join(self.captured_images_dir, filename)
            
            # Save the image
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"Image captured and saved to: {filepath}")
            return filepath
            
        except requests.RequestException as e:
            print(f"Error capturing image from IP Webcam: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error capturing image: {e}")
            return None

    def get_reading_status_from_user(self) -> str:
        """
        Get reading status from user via input.
        
        Returns:
            str: Selected reading status
        """
        print("\nSelect reading status:")
        print("  C - Complete")
        print("  P - Partially Complete")
        print("  N - Not Started")
        
        while True:
            try:
                key = input("Enter C, P, or N: ").lower().strip()
                if key in self.reading_status_options:
                    selected_status = self.reading_status_options[key]
                    print(f"Selected: {selected_status}")
                    return selected_status
                else:
                    print(f"Invalid input '{key}'. Please enter C, P, or N.")
            except Exception as e:
                print(f"Error reading input: {e}")
                return "Not Started"  # Default fallback

    def process_complete_book_workflow(self) -> Optional[dict]:
        """
        Complete workflow: capture image, extract info, get reading status, update database, delete image.
        
        Returns:
            dict: Complete book information, or None if failed
        """
        print("\n" + "="*60)
        print("STARTING COMPLETE BOOK PROCESSING WORKFLOW")
        print("="*60)
        
        # Step 1: Capture image
        print("\nStep 1: Capturing image...")
        image_path = self.capture_image_from_webcam()
        if not image_path:
            print("Failed to capture image. Workflow aborted.")
            return None
        
        # Step 2: Extract book information from title page
        print("\nStep 2: Extracting book information...")
        book_info = self.process_captured_image(image_path)
        if not book_info:
            print("Failed to extract book information. Workflow aborted.")
            self.cleanup_image(image_path)
            return None
        
        # Step 3: Infer subjects
        print("\nStep 3: Inferring subjects...")
        subjects_info = self.infer_subjects(book_info)
        
        # Step 4: Merge all information
        print("\nStep 4: Merging information...")
        complete_info = book_info.copy()
        if subjects_info:
            complete_info.update(subjects_info)
        
        # Step 5: Add location
        if self.location:
            complete_info['Location'] = self.location
            print(f"Added location: {self.location}")
        else:
            complete_info['Location'] = None
            print("No location provided")
        
        # Step 6: Get reading status from user
        print("\nStep 5: Getting reading status...")
        reading_status = self.get_reading_status_from_user()
        complete_info['ReadingStatus'] = reading_status
        
        # Step 7: Display final information
        print("\nStep 6: Final book information:")
        print("-" * 40)
        for key, value in complete_info.items():
            print(f"{key}: {value}")
        print("-" * 40)
        
        # Step 8: Add to database
        print("\nStep 7: Adding to database...")
        success = self.add_book_to_database(complete_info)
        if success:
            print("✓ Successfully added to database!")
        else:
            print("✗ Failed to add to database.")
            self.cleanup_image(image_path)
            return None
        
        # Step 9: Clean up image
        print("\nStep 8: Cleaning up...")
        self.cleanup_image(image_path)
        
        print("\n" + "="*60)
        print("WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nReady for next book.")
        
        return complete_info

    def cleanup_image(self, image_path: str):
        """
        Delete the captured image to save space.
        
        Args:
            image_path (str): Path to the image file to delete
        """
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"✓ Deleted image: {image_path}")
            else:
                print(f"Image not found: {image_path}")
        except Exception as e:
            print(f"Error deleting image {image_path}: {e}")

    def process_captured_image(self, image_path: str) -> Optional[dict]:
        """
        Process a captured image through the information extraction pipeline.
        
        Args:
            image_path (str): Path to the captured image
            
        Returns:
            dict: Extracted book information, or None if failed
        """
        try:
            # Update the image file path for the InformationExtractor
            self.IMAGE_FILE = image_path
            
            # Extract information from the title page
            print("\nExtracting information from title page...")
            extracted_info = self.extract_information_from_title_page()
            
            # Debug: Show the exact response
            print(f"\nDEBUG: Response length: {len(extracted_info)} characters")
            print(f"DEBUG: Response ends with: {repr(extracted_info[-20:])}")
            print(f"DEBUG: Full response:\n{extracted_info}")
            
            # Fix common JSON issues before parsing
            extracted_info = self._fix_json_formatting(extracted_info)
            
            # Parse the JSON response
            try:
                book_info = json.loads(extracted_info)
                print("\nSuccessfully extracted book information:")
                print(json.dumps(book_info, indent=2))
                return book_info
            except json.JSONDecodeError as e:
                print(f"Error parsing extracted information: {e}")
                print(f"Raw response: {extracted_info}")
                return None
                
        except Exception as e:
            print(f"Error processing captured image: {e}")
            return None

    def infer_subjects(self, book_info: dict) -> Optional[dict]:
        """
        Infer subject and specific subject for the book.
        
        Args:
            book_info (dict): Book information from extraction
            
        Returns:
            dict: Subject information, or None if failed
        """
        try:
            print("Inferring subjects...")
            subjects_info = self.infer_subject_and_specific_subject(
                json.dumps(book_info), 
                self.subjects_list.tolist(), 
                self.subjects_specific_list.tolist()
            )
            
            # Parse the JSON response
            try:
                subjects = json.loads(subjects_info)
                print("Successfully inferred subjects:")
                print(json.dumps(subjects, indent=2))
                return subjects
            except json.JSONDecodeError as e:
                print(f"Error parsing subjects information: {e}")
                print(f"Raw response: {subjects_info}")
                return None
                
        except Exception as e:
            print(f"Error inferring subjects: {e}")
            return None

    def add_book_to_database(self, complete_book_info: dict) -> bool:
        """
        Add the book information to the database.
        
        Args:
            complete_book_info (dict): Complete book information including location and reading status
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add to database using the parent class method
            success = self.add_to_database(complete_book_info)
            if success:
                print("✓ Book successfully added to database!")
            else:
                print("✗ Failed to add book to database.")
            
            return success
            
        except Exception as e:
            print(f"Error adding book to database: {e}")
            return False

    def run_interactive_mode(self):
        """
        Run the pipeline in interactive mode with simple input.
        """
        if not self.ip_webcam_url:
            print("Error: IP Webcam URL not configured. Please set ip_webcam_url parameter.")
            return
        
        print("Starting interactive book processing mode...")
        print("Commands:")
        print("  'capture' - Capture and process a book")
        print("  'test' - Test IP Webcam connection")
        print("  'quit' - Exit the program")
        print("-" * 50)
        
        while True:
            try:
                command = input("\nEnter command (capture/test/quit): ").lower().strip()
                
                if command == 'capture':
                    print("\nPosition a book title page in front of the camera...")
                    input("Press Enter when ready to capture...")
                    self.process_complete_book_workflow()
                    
                elif command == 'test':
                    print("\nTesting IP Webcam connection...")
                    image_path = self.capture_image_from_webcam()
                    if image_path:
                        print(f"✓ Connection successful! Image saved to: {image_path}")
                        # Clean up test image
                        self.cleanup_image(image_path)
                    else:
                        print("✗ Connection failed. Please check your IP Webcam setup.")
                        
                elif command == 'quit':
                    print("\nExiting...")
                    break
                    
                else:
                    print("Invalid command. Please enter 'capture', 'test', or 'quit'.")
                    
            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Exiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

    def run_single_capture(self) -> Optional[dict]:
        """
        Capture a single image and process it through the complete workflow.
        
        Returns:
            dict: Complete book information, or None if failed
        """
        if not self.ip_webcam_url:
            print("Error: IP Webcam URL not configured.")
            return None
        
        return self.process_complete_book_workflow()

    def run(self):
        """
        Default run method - starts interactive mode.
        """
        self.run_interactive_mode()

if __name__ == "__main__":
    FullPipeline(ip_webcam_url="", db_password="", location="").run()