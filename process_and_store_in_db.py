import os
from supabase import create_client, Client
from supabase.client import ClientOptions
from convert_to_speech import TTSHandler
from text_to_json import get_json
from dotenv import load_dotenv


load_dotenv()

class SupabaseManager:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_SERVICE_KEY")
        self.db = 'articles'
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

class ProcessData:
    def __init__(self, manager: SupabaseManager, tts: TTSHandler):
        self.manager = manager
        self.tts = tts
        
    def parse_content(self, article_id: str)-> tuple[str, str]:
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
            print(e)
            return None, None
        
    def get_all_articles(self):
        json_data = self.manager.get_articles("id")
        ids = json_data.data
        return ids
    
    def convet_to_speech_and_upload(self, article_id: str):
        """_summary_

        Args:
            article_id (str): _description_

        Returns:
            tamil_url, english_url
        
        Parse the text 
        Converts to audio file
        Upload to supabase storage. 
        Update the article with the urls. 
        Return the urls
        """
        try:
            tamil_text, english_text = self.parse_content(article_id)
            
            tamil_file_path = f"{article_id}_tamil.mp3"
            english_file_path = f"{article_id}_english.mp3"
            
            self.tts.text_to_speech_file(tamil_text, tamil_file_path, language_code="ta-IN")
            self.tts.text_to_speech_file(english_text, english_file_path, language_code="en-IN")
            
            tamil_url = self.manager.upload_audio_file(tamil_file_path)
            english_url = self.manager.upload_audio_file(english_file_path)
            
            json_data = {
                "audio": {
                    "tamil": tamil_url,
                    "english": english_url
                }
            }
            
            self.manager.update_article(article_id, json_data)
            
            return tamil_url, english_url
        except Exception as e:
            print(e)
            return None, None
    
    def upload_article_from_content(self, raw_text: str, upload: bool = True, gen_audio: bool = True, json_data: dict = {})-> dict:
        try: 
            article_json = get_json(raw_text)
            article_id  = article_json.id
            
            if upload:
                self.manager.insert_article(json_data)
                return {
                    "status": "success",
                    "message": "Article uploaded successfully",
                    "data": {
                        "article_id": article_id,
                        "json_data": json_data
                    }
                }
            if gen_audio and upload:
                tamil_url, english_url = self.convet_to_speech_and_upload(article_id)
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
    raw_text = """
    Be watchful
    Humans have desires because they were created by God to have them, with the intention that these desires would be focused on Him. We all know how Satan tempted Adam & Eve in Genesis! Eve's desire for the fruit came from her perception that it was "good for food," "pleasing to the eye," and "desirable for gaining wisdom." The serpent deceives Eve by twisting God's words, creating doubt, and making the fruit appear desirable for its promise of wisdom. We know what happens in the end. We see the tactics he used, and still he uses us too. As we read in 1 Peter 5:8, Be alert and of a sober mind. Your enemy the devil prowls around like a roaring lion looking for someone to devour." We have to be watchful; sin starts with our desire. Recently I realize that the battle is often won or lost in the mind.  When a thought arises that could lead to sin,Today I encourage everyone to dismiss it before it can lead to a sinful act. There are some cases where we react not even thinking before, because we used to, and Satan knows how to trigger us. To overcome this focus on Jesus rather than dwelling on the sin, hold on to your personal quiet time with God daily. My life was going well, but I wasn't happy. Once I was reading this passage, I understood that focusing on what is lacking is also a sin that makes us unhappy.  Eve made that mistake; she isn't satisfied with what God has given. She desired more; that made her fall. That's true, I started to see more on what I don't have instead of seeing what I have . Today I would like to remind myself and everyone God created us not by mistake; he knows what we should have, so we need to accept  and start to live the life that he has given.Not all your desires and needs are wrong,Sometimes it might be a natural, God-given desire also, so instead of we  chasing our desires, let's bring to God ,he will bless our desires .Start to focus on what he has given; believe that he knows and cares for us more than we do for  ourselves.Reflection: Examine yourselves. How conscious are you of sin? How often do you pray about sin?
    
    கவனமாக இருங்கள்!
    மனிதர்கள்  ஆசைகள்  கொண்டிருப்பது , தேவனால் உருவாக்கப்பட்டது, ஏனென்றால் இந்த ஆசைகள் அவரை மையமாகக் கொண்டிருக்கும் நோக்கத்துக்காக . ஆதியாகமத்தில் ஆதாமையும் ஏவாளையும் சாத்தான் எவ்வாறு சோதித்தான் என்பதை நாம் அனைவரும் அறிவோம்! ஏவாளின் பழத்தின் மீதான ஆசை, அது "உணவுக்கு நல்லது", "கண்ணுக்குப் பிரியமானது" மற்றும் "ஞானத்தைப் பெற விரும்பத்தக்கது" என்ற அவளுடைய பார்வையிலிருந்து வந்தது. சர்ப்பம் கடவுளின் வார்த்தைகளைத் திரித்து, சந்தேகத்தை உருவாக்கி, அதன் ஞான வாக்குறுதிக்காக பழத்தை விரும்பத்தக்கதாகக் காட்டுவதன் மூலம் ஏவாளை ஏமாற்றுகிறது. இறுதியில் என்ன நடக்கிறது என்பது நமக்குத் தெரியும். அவன் தந்திரங்களை ஆதாம் ஏவாள் முதற்கொண்டு நம்மிடமும் பயன்படுத்திக் கொண்டு இருக்கிறான் இன்று வரை.
 1 பேதுரு 5 அதிகாரம் 8-ல் நாம் படிக்கும்போது,
 தெளிந்த புத்தியுள்ளவர்களாயிருங்கள், விழித்திருங்கள்; ஏனெனில், உங்கள் எதிராளியாகிய பிசாசானவன் கெர்ச்சிக்கிற சிங்கம்போல் எவனை விழுங்கலாமோ என்று வகைதேடிச் சுற்றித்திரிகிறான்.
  நாம் விழிப்புடன் இருக்க வேண்டும்; பாவம் நம் ஆசையிலிருந்து தொடங்குகிறது.  இந்த ஆசை போராட்டம்   மனதில் தொடங்கி, வெற்றியோ தோல்வியோ என்று முடிவு செய்கிறது .  இன்று,  பாவச் செயலுக்கு வழிவகுக்கும் முன், அதை நாம் நிராகரிக்குமாறு அனைவரையும் நான் ஊக்குவிக்கிறேன். சில சமயங்களில்  சிந்திக்காமல் எதிர்வினையாற்றும்  சந்தர்ப்பங்கள் உள்ளன, காரணம் அதற்கு நாம் பழக்கப்பட்டு இருப்போம் , மேலும் சாத்தான் நம்மை எப்படித் தூண்டுவது என்று அறிந்திருக்கிறான். இதிலிருந்து மீண்டுக் கொள்ள பாவத்தில் கவனம் செலுத்துவதற்குப் பதிலாக இயேசுவின் மீது கவனம் செலுத்துவோம் , தினமும் கடவுளுடன்  தனிப்பட்ட  நேரத்தைப் தவறாமல் பிடித்துக் கொள்வோம் . எல்லாம் நன்றாக போய்க் கொண்டிருந்தது ஆனால் நான் மகிழ்ச்சியாக இல்லை,இந்தப் பகுதியைப் படித்த போது தெரிந்து கொண்டேன், இல்லாதவற்றில் கவனம் செலுத்துவதும் நம்மை மகிழ்ச்சியற்றவர்களாக மாற்றும், அது பாவம் என்பதை நான் புரிந்துகொண்டேன். ஏவாள் அந்தத் தவறைச் செய்தாள்; கடவுள் கொடுத்ததில் அவள் திருப்தி அடையவில்லை. அவள் அதிகமாக விரும்பினாள்; அது அவளை வீழ்ச்சியடையச் செய்தது. ஏவாளை போல நானும்  தேவன்  எனக்கு என்ன கொடுத்திருக்கிறார்  பார்ப்பதற்குப் பதிலாக, என்னிடம் இல்லாதவற்றில் கவனம் செலுத்தி வந்தேன்; என் ஆசைகள் என்னைப் கைதியாக்கியது, அதிலிருந்து விடு பெற இந்த புரிதலை  நம்ப வேண்டும் என்று கற்றுக்கொண்டேன் , நமக்கு என்ன வேண்டும் என்று அவருக்குத் தெரியும், எனவே அவர் கொடுத்த வாழ்க்கையை நாம் அதனுடன் வாழ பழகிக் கொள்ள வேண்டும் என்று. நமக்கு சில தேவைகள் அல்லது ஆசைகள் இருக்கலாம்; எல்லாம் தவறாக இருக்காது. சில நேரங்களில் அது இயற்கையானது, தேவன் கொடுத்த விருப்பமாகவும் கூட இருக்கலாம், எனவே ஆசைகளைத் பின் நாம்  துரத்துவதற்குப் பதிலாக, ஆசைகளை தேவனிடம் கொண்டு வாருங்கள்; அது நம் வாழ்க்கைக்கு சிறந்த தீர்வாக இருக்கும். அவர் நம்மை  வழிநடத்துவார். அவர் கொடுத்தவற்றில் கவனம் செலுத்தத் தொடங்குங்கள்; அவர் நம்மை விட நம்மை அறிந்திருக்கிறார், அக்கறை காட்டுகிறார் என்பது நம்புங்கள். பிரதிபலிப்பு: உங்களை நீங்களே ஆராய்ந்து பாருங்கள். பாவத்தைப் பற்றி நீங்கள் எவ்வளவு உணர்வுள்ளவராக இருக்கிறீர்கள்? பாவத்தைப் பற்றி நீங்கள் எத்தனை முறை ஜெபிக்கிறீர்கள்?
    """
    resp = pd.upload_article_from_content(raw_text, upload=True, gen_audio=True)
    print(resp)
    
    """Get content and upload"""
    tamil_url, english_url = pd.convet_to_speech_and_upload('jealousy-and-envy')
    print(tamil_url)
    print(english_url)
    
    """Get the content"""
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

