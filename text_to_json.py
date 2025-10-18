from google import genai
from pydantic import BaseModel
from typing import List, Literal
import json
import os

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


def get_json(content: str) -> tuple[str, dict]:
    
    # output_filename = "output.json"
    # if os.path.exists(output_filename):
    #     with open(output_filename, 'r') as f:
    #         json_data = json.load(f)
    #         article_id = json_data.get('id')
    #         if article_id:
    #             print(f"Loaded from existing file: {output_filename}")
    #             return (article_id, json_data)

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
    
    json_data = article.model_dump()
    article_id = json_data['id']
    
    # Note: The user requested to use a fixed "output.json" file.
    # For multiple articles, you might want to use a dynamic filename like:
    output_filename = f"{article_id}-output.json"
    
    with open(output_filename, "w") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
        
    return (article_id, json_data)

if __name__ == "__main__":
    raw_text = """
   """
    article = get_json(raw_text)
    
    print(json.dumps(article.model_dump(), ensure_ascii=False, indent=2))
    