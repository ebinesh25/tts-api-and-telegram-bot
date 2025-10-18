import os
from supabase import create_client, Client
from supabase.client import ClientOptions
from convert_to_speech import TTSHandler
from text_to_json import get_json
from dotenv import load_dotenv
import json


load_dotenv()
import logging
from tqdm import tqdm

# Configure logging to file
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("process.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class SupabaseManager:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_SERVICE_KEY")
        self.db = 'articles_duplicate'
        # self.db = 'articles_duplicate'
        self.supabase: Client = create_client(
            url,
            key,
            options=ClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
                schema="public",
            )
        )

    def get_articles(self, query:str = '*'):
        """Fetches all articles."""
        return self.supabase.table(self.db).select(query).execute()

    def insert_article(self, json_data: dict):
        """Inserts a new article."""
        return self.supabase.table(self.db).insert(json_data).execute()

    def delete_article(self, id: str):
        """Deletes an article by ID."""
        return self.supabase.table(self.db).delete().eq("id", id).execute()

    def get_article(self, id: str):
        """Fetches an article by ID."""
        try:
            res = self.supabase.table(self.db).select("*").eq("id", id).execute()
            if not res.data:
                raise Exception(f"No data found for {id} from DB {self.db} \n {res}")
            return res
        except Exception as e:
            print(e)
            return None

    def update_article(self, id: str, json_data: dict):
        """Updates an article by ID."""
        return self.supabase.table(self.db).update(json_data).eq("id", id).execute()

    def upload_audio_file(self, file_path: str, bucket_name: str = "blog_audio"):
        """
        Uploads an audio file to Supabase Storage.
        Args:
            file_path (str): Local path to the audio file.
            bucket_name (str): Name of the Supabase Storage bucket.
        Returns:
            str: Public URL of the uploaded file, or None if upload failed.
        """
        try:
            file_name = os.path.basename(file_path)
            with open(file_path, "rb") as audio_file:
                data = self.supabase.storage.from_(bucket_name).upload(
                    path=f"audio/{file_name}",
                    file=audio_file,
                    file_options={"content-type": "audio/mpeg"}
                )
            if data:
                public_url = self.supabase.storage.from_(bucket_name).get_public_url(f"audio/{file_name}")
                print(f"File uploaded successfully! Public URL: {public_url}")
                return public_url
            else:
                print("Upload failed.")
                return None
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None

    def get_audio_file_url(self, file_name: str, bucket_name: str = "blog_audio"):
        """
        Gets the public URL of an audio file if it exists in Supabase Storage.
        Args:
            file_name (str): Name of the audio file.
            bucket_name (str): Name of the Supabase Storage bucket.
        Returns:
            str: Public URL of the file, or None if it doesn't exist.
        """
        try:
            # List files in the 'audio' folder of the bucket
            files = self.supabase.storage.from_(bucket_name).list(path="audio")
            
            # Check if the file exists in the list
            file_exists = any(file['name'] == file_name for file in files)
            
            if file_exists:
                public_url = self.supabase.storage.from_(bucket_name).get_public_url(f"audio/{file_name}")
                return public_url
            else:
                return None
        except Exception as e:
            print(f"Error checking for file: {e}")
            return None

class ProcessData:
    def __init__(self, manager: SupabaseManager, tts: TTSHandler):
        self.manager = manager
        self.tts = tts
        
    def parse_content(self, article_id: str)-> tuple[str, str]:
        logger.info(f"Parsing content for article_id: {article_id}")
        try:
            json_data = self.manager.get_article(article_id)    
            if not json_data.data:
                raise Exception("No data found")
            
            tamil_content = json_data.data[0]['content']['tamil']
            english_content = json_data.data[0]['content']['english']
            
            tamil_text = ""
            english_text = ""
            
            for obj in tamil_content:
                tamil_text += obj['value'] + " "
            
            for obj in english_content:
                english_text += obj['value'] + " "
            
            return (tamil_text, english_text)
        except Exception as e:
            logger.error(f"Error parsing content for article {article_id}: {e}")
            return None, None
        
    def get_all_articles(self):
        json_data = self.manager.get_articles("id")
        ids = json_data.data
        return ids
    
    def convet_to_speech_and_upload(self, article_id: str):
        """
        Process text to speech conversion and upload for a given article.

        Args:
            article_id (str): Identifier of the article to process.

        Returns:
            tuple: (tamil_url, english_url) on success, (None, None) on failure.
        """
        # Define processing steps for progress bar
        steps = [
            "Parsing content",
            "Generating Tamil audio",
            "Generating English audio",
            "Uploading Tamil audio",
            "Uploading English audio",
            "Updating database"
        ]
        pbar = tqdm(total=len(steps), desc=f"Processing article {article_id}", unit="step")
        try:
            # Prepare file paths
            tamil_file_path = f"{article_id}_tamil.mp3"
            english_file_path = f"{article_id}_english.mp3"
            
            # Check if files already exist in storage
            tamil_url = self.manager.get_audio_file_url(os.path.basename(tamil_file_path))
            english_url = self.manager.get_audio_file_url(os.path.basename(english_file_path))

            if tamil_url and english_url:
                logger.info(f"Audio files for article {article_id} already exist. Skipping generation and upload.")
                # Update the database with the existing URLs
                json_data = {"audio": {"tamil": tamil_url, "english": english_url}}
                self.manager.update_article(article_id, json_data)
                logger.info(f"Updated article {article_id} with existing audio URLs")
                return tamil_url, english_url
            
            # Step 1: Parse content
            pbar.set_description("Parsing content")
            tamil_text, english_text = self.parse_content(article_id)
            pbar.update(1)


            # Step 2: Generate Tamil audio
            pbar.set_description("Generating Tamil audio")
            self.tts.text_to_speech_file(tamil_text, tamil_file_path, language_code="ta-IN")
            logger.info(f"Generated Tamil audio file: {tamil_file_path}")
            pbar.update(1)

            # Step 3: Generate English audio
            pbar.set_description("Generating English audio")
            self.tts.text_to_speech_file(english_text, english_file_path, language_code="en-IN")
            logger.info(f"Generated English audio file: {english_file_path}")
            pbar.update(1)

            # Step 4: Upload Tamil audio
            pbar.set_description("Uploading Tamil audio")
            tamil_url = self.manager.upload_audio_file(tamil_file_path)
            logger.info(f"Uploaded Tamil audio for {article_id}: {tamil_url}")
            pbar.update(1)

            # Step 5: Upload English audio
            pbar.set_description("Uploading English audio")
            english_url = self.manager.upload_audio_file(english_file_path)
            logger.info(f"Uploaded English audio for {article_id}: {english_url}")
            pbar.update(1)

            # Step 6: Update database
            pbar.set_description("Updating database")
            json_data = {"audio": {"tamil": tamil_url, "english": english_url}}
            self.manager.update_article(article_id, json_data)
            logger.info(f"Updated article {article_id} with audio URLs")
            pbar.update(1)

            pbar.close()
            return tamil_url, english_url
        except Exception as e:
            pbar.close()
            logger.error(f"Error in TTS conversion and upload for article {article_id}: {e}")
            return None, None
    
    def upload_article_from_content(self, raw_text: str, upload: bool = True, json_data: dict = {})-> dict:
        steps = [
            "Generate Json From Data",
            "Upload Article" if upload else "",
            "Upload Audio" if upload else ""
        ]
        pbar = tqdm(total=len(steps), desc=f"Processing article", unit="step")
        try: 
            
            # Step 1: Convert content to json
            pbar.set_description("Generate Json From Data")
            article_id, json_data = get_json(raw_text)
            
            pbar.update(1)
            
            
            if upload:
                # Step 2: Upload article
                pbar.set_description("Upload Article")
                existing_article = self.manager.get_article(article_id)
                if existing_article and existing_article.data:
                    logger.info(f"Article with id {article_id} already exists. Skipping insertion.")
                else:
                    self.manager.insert_article(json_data)
                pbar.update(1)
                
                
                pbar.set_description("Upload Audio")
                tamil_url, english_url = self.convet_to_speech_and_upload(article_id)
                pbar.update(1)
                
                return {
                        "status": "success",
                        "message": "Article uploaded successfully with audio",
                        "data": {
                            "article_id": article_id,
                            "json_data": json_data,
                            "audio": {
                                "tamil": tamil_url,
                                "english": english_url
                            }
                        }
                    }
               
            return {
                "status": "success",
                "message": "Article transformed to json",
                "data": {
                    "article_id": article_id,
                    "json_data": json_data
                }
            }
        except Exception as e:
            print(e)
            return {
                "status": "error",
                "message": "Error uploading article",
                "data": None
            }

if __name__ == "__main__":
    manager = SupabaseManager()
    tts = TTSHandler()
    pd = ProcessData(manager, tts)
    
    # print(manager.get_article('jealousy-and-envy'))
    
    """Upload from raw_text"""
    with open('raw_text.txt', 'r') as f:
        raw_text = f.read()
    
    pd.upload_article_from_content(raw_text)
    
    # article_id, article_json = get_json(raw_text)
    
    # with open(f'{article_id}-output.json', 'r') as f:
    #     article_json = json.load(f)
    
    # """Upload from json"""
    # resp = manager.insert_article(article_json)
    # print(resp)
  
    # """Get content and upload"""
    # tamil_url, english_url = pd.convet_to_speech_and_upload(article_id)
    # print(tamil_url)
    # print(english_url)
    
    # """Get the content"""
    # tamil_text, english_text = pd.parse_content('jealousy-and-envy')
    # print(english_text)
    # print(tamil_text)
    
    # Test database query
    # res = manager.get_articles()
    # print(res)
    # Test audio upload (uncomment to use)
    # url = manager.upload_audio_file("weakness_english.mp3")
    # print(url)
    # print(manager.supabase.storage.list_buckets())

