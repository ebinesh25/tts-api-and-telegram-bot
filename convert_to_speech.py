from google.cloud import texttospeech

class TTSHandler:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()

    def text_to_speech_bytes(self, text: str, language_code: str = "en-US", voice_name: str = None) -> bytes:
        """
        Convert text to speech and return audio as bytes (MP3).
        
        :param text: Text to convert
        :param language_code: Language code (default: en-US)
        :param voice_name: Specific voice name (optional)
        :return: MP3 audio bytes
        """
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name if voice_name else None
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config
        )
        
        return response.audio_content

# Example usage
if __name__ == "__main__":
    tts = TTSHandler()
    audio_bytes = tts.text_to_speech_bytes("Hello, world!", "en-US")
    
    # Optionally save to a file for testing
    with open("output.mp3", "wb") as f:
        f.write(audio_bytes)
    
    # audio_bytes can now be stored directly in a database (BLOB field)
    print("MP3 bytes length:", len(audio_bytes))
