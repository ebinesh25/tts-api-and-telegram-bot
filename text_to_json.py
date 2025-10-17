from google import genai
from pydantic import BaseModel
from typing import List, Literal
import json

# --- Pydantic schema ---
class ContentBlock(BaseModel):
    type: Literal["mainText", "scripture", "reflection"]
    value: str

class LocalizedContent(BaseModel):
    tamil: List[ContentBlock]
    english: List[ContentBlock]

class Title(BaseModel):
    tamil: str
    english: str

class Author(BaseModel):
    tamil: str
    english: str

class Article(BaseModel):
    id: str
    title: Title
    content: LocalizedContent
    author: Author


def get_json(content: str) -> Article:
    
    # --- Gemini setup ---
    client = genai.Client()

    plain_text = content

    prompt = f"""
    You are a precise text-to-structure converter.

    Rules:
    1. Do NOT add, remove, translate, or paraphrase any content.
    2. Only correct punctuation, spacing, and capitalization.
    3. Use the same sentences and ordering exactly as provided.
    4. Split the text into English and Tamil sections.
    5. Within each language, identify:
        - 'mainText' for normal paragraphs
        - 'scripture' for Bible verses
        - 'reflection' for the reflective question section
    6. Generate a valid JSON strictly matching this Pydantic schema: Article
    7. id should be a simple lowercase hyphenated version of the title.
    8. Author must be:
        - tamil: "ஜெஸ்ஸி ஆனந்த்"
        - english: "Jessie Anand"
    9. Do not invent or change text — preserve everything faithfully.

    Here is the raw input:

    {plain_text}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": Article,
        },
    )

    # Parsed structured object
    article: Article = response.parsed
    return article

if __name__ == "__main__":
    content = """
    Be cautious ! Jealousy & envy are natural emotions,it often arises from feelings of insecurity, fear, pride,lack of gratitude and lack of contentment and comparison. When we struggle with jealousy & envy if we leave it untreated and try to either ignore it or cover it up, it doesn’t matter how many good things we try to put into our lives—their growth will be stunted, and we won’t see fruit.Recently I was struggling with myself  when others receive opportunity or appreciation, I lack of happiness for them, later while preparing this I found that it could be a mix of envy and jealousy. Envy is the feeling of wanting what another person has, while jealousy is the feeling of resentment that someone else has gained something you feel you deserve or want to keep.According to the Bible, jealousy and envy arise from a focus on what others have instead of focusing on God's blessings and provision in our lives . Many times we take envy and jealousy as the same,but both are different.First identify and recognise it as sin,James 3:16 NIV [16] For where you have envy and selfish ambition, there you find disorder and every evil practice. The first murder in the Bible, Cain killing Abel, is directly attributed to envy, according to the bible. Envy and jealousy are troublesome to others but a torment to themselves ,so consider it as serious in our life . To help ourselves,instead of dwelling on what others have, Focus and count your  blessings and thank God for what we already have.Recognizing that all good things come from God and that we are all equally loved and valued by Him can help diminish envy. We need to understand the truth the true fulfillment comes from a relationship with God, not from material possessions or the achievements of others.Remember we are called to rejoice with others and be grateful.so let's overcome together. God provides a way out of temptation, including the temptation to jealousy and envy,so let's confess and ask forgiveness today . Reflection : What specific circumstances or people trigger feelings of jealousy or envy in your life? How do these feelings affect your  relationships with God and others? எச்சரிக்கையாக இருங்கள்! Jealousy" மற்றும் "Envy" இரண்டிற்குமான தமிழ் சொல் "பொறாமை" என்பதாகும். இருப்பினும், சூழலைப் பொறுத்து இந்த இரண்டு சொற்களுக்கும் இடையே பெரிய வேறுபாடு இருக்கிறது. இது இரண்டுமே இயற்கையான உணர்ச்சிகள், அவை பெரும்பாலும் பாதுகாப்பின்மை, பயம், பெருமை, நன்றியின்மை மற்றும் மனநிறைவு இல்லாமை மற்றும் ஒப்பீடு போன்ற உணர்வுகளிலிருந்து எழுகின்றன. நாம் பொறாமை  அல்லது அழுக்காறு ( envy) போராடும்போது, அதை நாம் மறைக்கவும், புறக்கணிக்கவும், அல்லது  கவனிக்கவும் தவறவிட்டாள்  நம் வாழ்க்கையில் எத்தனை நல்ல விஷயங்களைச் செய்ய முயற்சித்தாலும் பரவாயில்லை - அவற்றின் வளர்ச்சி தடைபடும், மேலும் நாம் பலனைக் காண மாட்டோம். சமீபத்தில் மற்றவர்கள்  வாய்ப்பு அல்லது பாராட்டுகளைப் பெறும்போது நான்  அவர்களுக்காக  மகிழ்ச்சியாக  இல்லை, பின்னர் இதைத் எழுதும்போது அது பொறாமை மற்றும் அழுக்காறு  கலவையாக இருக்கலாம் என்பதைக் கண்டறிந்தேன்.  அழுக்காறு என்பது மற்றொரு நபரிடம் இருப்பதை விரும்புவது போன்ற உணர்வு, அதே சமயம் பொறாமை என்பது நீங்கள் தகுதியானவர் அல்லது வைத்திருக்க விரும்பும் ஒன்றை வேறொருவர் பெற்றுள்ளார் என்ற வெறுப்பு உணர்வு. வேதாகம் படி , பொறாமை மற்றும் அழுக்காறு நம் வாழ்க்கையில் கடவுளின் ஆசிர்வாதங்களை கவனம் செலுத்துவதற்குப் பதிலாக மற்றவர்களிடம் உள்ளவற்றில் கவனம் செலுத்துவதிலிருந்து எழுகிறது.  பல சமயங்களில் நாம் பொறாமையையும் அழுக்காறு  ஒரே மாதிரியாக எடுத்துக்கொள்கிறோம், ஆனால் இரண்டும் வேறுபட்டவை, முதலில் நாம் வேறுபாட்டை கண்டுபிடித்து அது பாவம் என்று உணர வேண்டும் யாக்கோபு 3:16 பார்த்தாள் வைராக்கியமும் விரோதமும் எங்கே உண்டோ, அங்கே கலகமும் சகல துர்ச்செய்கைகளுமுண்டு. பைபிளில் உள்ள முதல் கொலை, காயீன் ஆபேலைக் கொன்றது, நேரடியாக பொறாமைக்குக் காரணம். பொறாமை மற்றும் அழுக்காறு  மற்றவர்களுக்கு தொந்தரவாக இருக்கிறது, ஆனால் தங்களைத் தாங்களே வேதனைப்படுத்துகின்றன, என்று புரிந்து கொள்ள வேண்டும் . நம்மை நாமே காப்பாற்றிக் கொள்ள, மற்றவர்களிடம் இருப்பதைப் பற்றி சிந்திப்பதற்குப் பதிலாக, மாறாக உங்கள் ஆசீர்வாதங்களை எண்ணி, நம்மிடம் ஏற்கனவே உள்ளதற்கு கடவுளுக்கு நன்றி சொல்லுங்கள். எல்லா நல்ல விஷயங்களும் கடவுளிடமிருந்து வருகின்றன, நாம் அனைவரும் அவரால் சமமாக நேசிக்கப்படுகிறோம், மதிக்கப்படுகிறோம் என்பதை அங்கீகரிப்பது பொறாமையைக் குறைக்க உதவும். உண்மையான நிறைவு கடவுளுடனான உறவிலிருந்து வருகிறது என்பதை நாம் புரிந்து கொள்ள வேண்டும், பொருள் உடைமைகளிலிருந்தோ அல்லது மற்றவர்களின் சாதனைகளிலிருந்தோ அல்ல. மற்றவர்களுடன் மகிழ்ச்சியடையவும் நன்றியுடன் இருக்கவும் நாம் அழைக்கப்பட்டுள்ளோம் என்பதை நினைவில் கொள்ளுங்கள். எனவே ஒன்றாக ஜெயிப்போம். அழுக்காறு மற்றும் பொறாமைக்கான சோதனை உட்பட சோதனையிலிருந்து வெளியேற தேவன் உதவி செய்வார் அவரிடம் அறிக்கை செய்து மன்னிப்பு கேட்போம். சிந்தனை: உங்கள் வாழ்க்கையில் பொறாமை அல்லது அழுக்காறு  உணர்வுகளைத் தூண்டும் குறிப்பிட்ட சூழ்நிலைகள் அல்லது நபர்கள் என்ன? இந்த உணர்வுகள் கடவுள் மற்றும் பிறருடனான உங்கள் உறவுகளை எவ்வாறு பாதிக்கின்றன? என்று  சிந்தியுங்கள்.
    """
    article = get_json(content)
    print(json.dumps(article.model_dump(), ensure_ascii=False, indent=2))
    