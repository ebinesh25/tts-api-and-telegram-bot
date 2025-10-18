# Async TTS API and Telegram Bot

This project provides:
- A FastAPI service for text-to-speech (TTS) conversion using Google Cloud Text-to-Speech.
- A Telegram bot that forwards messages to the FastAPI service and returns audio URLs.
- Supabase integration for storing article data and audio files.

## Prerequisites

- Python 3.10+
- pip
- Google Cloud account with Text-to-Speech API enabled
- Google Cloud service account JSON key
- Supabase account and project
- Telegram account

## Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd <repo>
   ```
2. Create a virtual environment and install dependencies.

   Option A (using pip):
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

   Option B (using uv for dependency management):
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install uv
   uv install           # installs dependencies from pyproject.toml and uv.lock
   ```

   To add a new package and update lock file:
   ```bash
   uv add <package>     # e.g. uv add fastapi
   ```
3. Create a `.env` file in the project root and add the environment variables (see Configuration).

## Configuration

### Google Cloud Text-to-Speech

1. Create a Google Cloud project.
2. Enable the Text-to-Speech API.
3. Create a service account with `Text-to-Speech Admin` permission.
4. Download the JSON key and save it locally (e.g., `gcloud-key.json`).
5. Set the environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/gcloud-key.json"
   ```

### Supabase

1. Create a Supabase project.
2. Copy the `API URL` and `Service Role` key.
3. Create a storage bucket named `blog_audio`.
4. Make the bucket public (or configure appropriate ACL).
5. In your `.env` file, set:
   ```env
   SUPABASE_URL=https://xyzcompany.supabase.co
   SUPABASE_SERVICE_KEY=your-service-role-key
   ```

### Telegram Bot

1. Open Telegram and start a chat with [BotFather](https://t.me/botfather).
2. Use `/newbot` to create a new bot. Follow prompts for name and username.
3. Copy the bot token.
4. In your `.env` file, set:
   ```env
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   ```

## Environment Variables (`.env`)

```env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcloud-key.json
SUPABASE_URL=https://xyzcompany.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

## Running the Services

### FastAPI Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Telegram Bot

```bash
python telegram_bot.py
```

## Usage

1. Send a `/start` command in Telegram to initialize the bot.
2. Send multi-line text to the bot.
3. The bot will process the text, upload JSON and audio to Supabase, and reply with public URLs.

## Supabase Storage

Audio files are uploaded to the `blog_audio` bucket under the `audio/` path. Public URLs are generated automatically.

## License

This project is licensed under the MIT License.
