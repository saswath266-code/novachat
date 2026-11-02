# NovaChat

NovaChat is a Flask web chat interface backed by the Gemini API.

## Requirements

- Python 3.10 or newer
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

## Run locally

From PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Add your real API key to `.env`, then start the app:

```powershell
python app.py
```

Open `http://127.0.0.1:5000` in a browser. To enable Flask development mode, set `FLASK_DEBUG=1` before starting the app.

If an old virtual environment references a removed Python installation, delete only the project `venv` directory and recreate it with the commands above. The environment is not committed to Git and contains no project source code.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `GEMINI_API_KEY` | — | Required Gemini API key. |
| `GEMINI_MODEL` | `gemini-flash-latest` | Gemini text model to use. |
| `GEMINI_TIMEOUT_MS` | `30000` | Whole-request Gemini timeout, in milliseconds. |
| `MAX_MESSAGE_LENGTH` | `12000` | Largest accepted message, in characters. |
| `MAX_REQUEST_BYTES` | `32768` | Largest accepted request body, in bytes. |

## Tests

```powershell
python -m unittest discover -s tests -v
```

The endpoint tests use a fake response generator, so they do not call Gemini or require an API key.
