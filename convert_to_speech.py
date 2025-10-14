from google.cloud import texttospeech

class TTSHandler:
    MAX_BYTES = 4500  # Leave some buffer under 5000

    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()

    def get_despina_voice(self, language_code: str):
        despina_map = {
            "en-US": "en-US-Chirp3-HD-Despina",
            "en-GB": "en-GB-Chirp3-HD-Despina",
            "en-IN": "en-IN-Chirp3-HD-Despina",
            "ta-IN": "ta-IN-Chirp3-HD-Despina",
        }
        return despina_map.get(language_code)

    def _split_text(self, text: str):
        """Split text into chunks <= MAX_BYTES."""
        chunks = []
        current = ""
        for paragraph in text.split("\n"):
            if len((current + paragraph).encode("utf-8")) > self.MAX_BYTES:
                if current:
                    chunks.append(current)
                if len(paragraph.encode("utf-8")) > self.MAX_BYTES:
                    # further split long paragraph
                    start = 0
                    encoded = paragraph.encode("utf-8")
                    while start < len(encoded):
                        end = start + self.MAX_BYTES
                        chunks.append(encoded[start:end].decode("utf-8", errors="ignore"))
                        start = end
                    current = ""
                else:
                    current = paragraph
            else:
                current += "\n" + paragraph if current else paragraph
        if current:
            chunks.append(current)
        return chunks

    def text_to_speech_file(self, text: str, file_path: str, language_code: str = "en-IN"):
        """
        Convert text to MP3 and save directly to a file, chunk by chunk.
        """
        voice_name = self.get_despina_voice(language_code)
        with open(file_path, "wb") as f:
            for chunk in self._split_text(text):
                synthesis_input = texttospeech.SynthesisInput(text=chunk)
                voice_params = texttospeech.VoiceSelectionParams(
                    language_code=language_code,
                    name=voice_name
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3
                )
                response = self.client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice_params,
                    audio_config=audio_config
                )
                f.write(response.audio_content)
        print(f"Saved MP3 to {file_path}")


if __name__ == "__main__":
    tts = TTSHandler()

    english_text = """Is it wrong ? 
How many of you did this ! Many times we blame Adam and Eve for eating the fruit..."""
    tamil_text = """உங்களில் எத்தனை பேர் இதைச் செய்திருக்கிறீர்கள் ! பல சமயங்களில் பழத்தைச் சாப்பிட்டதற்காக ஆதாமையும் ஏவாளையும் குறை சொல்லிருக்கிறோம், ஏனென்றால் அவர்களால்தான் பாவம் இந்த உலகத்திற்குள் நுழைந்தது, இப்போது நாம் போராடி வருகிறோம் என்று, அது உண்மைதான்.. ஆனால் கடவுள் ஏன் அவர்களை அப்படிச் செய்ய அனுமதிக்கிறார் என்று நாம் கேள்வி கேட்கிறோமா? இதைத் தெரிந்துகொள்ள, ஆதியாகமம் 2-ஐப் படித்தால், கடவுள் ஒவ்வொரு மனிதனையும் தங்கள் சொந்தத் தேர்வுகளையும் முடிவுகளையும் எடுக்கும் திறனுடன் படைத்தார் என்பது நமக்குத் தெரியும். அவர் சுதந்திரமான விருப்பத்தைக் கொடுத்திருக்கிறார்; தளபதி கட்டளையிடுவதைச் செய்ய அவர் நம்மை ரோபோக்களாக உருவாக்கவில்லை. இது எல்லாம் நாம் தேர்ந்தெடுப்பதைப் பற்றியது. நாம் அனைவரும் ஒருவரால் கட்டுப்படுத்தப்படுவதை விரும்புவதில்லை. நான் வளர்ந்து வந்த காலத்தில், நான் என்ன செய்கிறேன் என்று எனக்குத் தெரியும் என்று என் அம்மாவிடம் சொன்னது எனக்கு நினைவிருக்கிறது. திருமணமான பிறகு, "என் கணவருடன் எனக்குத் தெரியும் எனக்கு எதுவும் சொல்ல வேண்டாம் " என்று நான் சொல்வேன். ஆமாம், என்னைப் போலவே, நம்மில் பலர் தங்களுக்குத் தேவையானதைத், விருப்பமானது தேர்ந்தெடுக்க சுதந்திரத்தை விரும்புகிறோம், ஆனால் இன்று, அந்த சுதந்திரத்தை எவ்வாறு பயன்படுத்துகிறோம்? யாரையும் குறை சொல்ல முடியாது, கடவுளை கூட, ஏனென்றால் அவர் நம் உணர்வு மூலம் நமக்கு அறிவுறுத்துகிறார்.  நினைவில் கொள்ளுங்கள் நாம் தேர்ந்தெடுக்கும் செயல்களுக்கும் முடிவுகளுக்கு நாமே பொறுப்பு, ஒவ்வொரு காரியத்திற்கும் விளைவுகள் இருக்கு என்று.
1 கொரிந்தியர் 10:23 இல் பவுல் சொல்வது போல், 

எல்லாவற்றையும் அநுபவிக்க எனக்கு அதிகாரமுண்டு, ஆகிலும் எல்லாம் தகுதியாயிராது; எல்லாவற்றையும் அநுபவிக்க எனக்கு அதிகாரமுண்டு, ஆகிலும் எல்லாம் பக்திவிருத்தியை உண்டாக்காது.

எல்லாவற்றையும் செய்ய நமக்கு உரிமை உண்டு, ஆனால் நமக்கு எது நல்லது என்பதைப்  சிந்தியுங்கள். சில நேரங்களில் நாம் பார்வையில் நமக்கு நல்லது என்று தோன்றுகிற  காரியங்களை செய்கிறோம், ஆனால் கிறிஸ்தவர்களாகிய அழைக்கப்பட்டவர்களுக்கு ஒரு பொறுப்பு இருக்கிறது , நமக்கு எது நல்லது  மட்டும் சிந்திக்காமல், மற்றவர்களுக்கும்  அது நல்லதா? அது பிரயோஜனமாக இருக்குமா  என்று யோசிக்க வேண்டும். கடவுளைப் பிரியப்படுத்தும் சரியான வழியில் நமது சுதந்திரத்தைப் பயன்படுத்துவோம். 
பிரதிபலிப்பு:
உங்கள்  வாழ்க்கையில் நீங்கள் தேர்ந்தெடுக்கும் விருப்பங்கள் முடிவுகள்   உங்களை பிரியப்படுத்துகிறதா அல்லது தேவனை தெரியப்படுத்துகிறதா என்று யோசித்துப் பாருங்கள்."""

    # Directly save long texts to MP3 files
    # tts.text_to_speech_file(english_text, "output_en.mp3", language_code="en-IN")
    tts.text_to_speech_file(tamil_text, "output_ta.mp3", language_code="ta-IN")
