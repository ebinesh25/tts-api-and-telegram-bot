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

    def preprocess_text(self, text:str) -> str:
        """Replace all the , with ."""
        if text:
            return text.replace(",", ".")
        return ""
    
    def text_to_speech_file(self, text: str, file_path: str, language_code: str = "en-IN"):
        """
        Convert text to MP3 and save directly to a file, chunk by chunk.
        """
        voice_name = self.get_despina_voice(language_code)
        with open(file_path, "wb") as f:
            for chunk in self._split_text(text):
                chunk = self.preprocess_text(chunk)
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
    tamil_text = """Jealousy" மற்றும் "Envy" இரண்டிற்குமான தமிழ் சொல் "பொறாமை" என்பதாகும். இருப்பினும், சூழலைப் பொறுத்து இந்த இரண்டு சொற்களுக்கும் இடையே பெரிய வேறுபாடு இருக்கிறது. இது இரண்டுமே இயற்கையான உணர்ச்சிகள், அவை பெரும்பாலும் பாதுகாப்பின்மை, பயம், பெருமை, நன்றியின்மை மற்றும் மனநிறைவு இல்லாமை மற்றும் ஒப்பீடு போன்ற உணர்வுகளிலிருந்து எழுகின்றன. நாம் பொறாமை  அல்லது அழுக்காறு ( envy) போராடும்போது, அதை நாம் மறைக்கவும், புறக்கணிக்கவும், அல்லது  கவனிக்கவும் தவறவிட்டாள்  நம் வாழ்க்கையில் எத்தனை நல்ல விஷயங்களைச் செய்ய முயற்சித்தாலும் பரவாயில்லை -- அவற்றின் வளர்ச்சி தடைபடும், மேலும் நாம் பலனைக் காண மாட்டோம். சமீபத்தில் மற்றவர்கள்  வாய்ப்பு அல்லது பாராட்டுகளைப் பெறும்போது நான்  அவர்களுக்காக  மகிழ்ச்சியாக  இல்லை, பின்னர் இதைத் எழுதும்போது  அது பொறாமை மற்றும் அழுக்காறு  கலவையாக இருக்கலாம் என்பதைக் கண்டறிந்தேன்.  """

    # Directly save long texts to MP3 files
    # tts.text_to_speech_file(english_text, "output_en.mp3", language_code="en-IN")
    tts.text_to_speech_file(tamil_text, "output_ta.mp3", language_code="ta-IN")
