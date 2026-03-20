# Content Monitoring & Flagging System

This is a backend system built with Django and Django REST Framework that monitors external content, identifies keyword-based matches, and generates "Flags" for human review. It implements a core business suppression rule to ignore irrelevant content in future scans unless the underlying text has changed.

## Requirements
* Python 3.10+ (Recommended)
* Django 6.0+
* Django REST Framework 3.17+

## Setup Instructions

1. **Clone the repository** and navigate to the root directory.
2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install django djangorestframework
   ```
4. **Run Migrations**:
   The default database is SQLite.
   ```bash
   python manage.py migrate
   ```
5. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

## Assumptions and Trade-offs
* **External Source**: For simplicity and test predictability, I opted for a **mock hardcoded payload** in `services.py`. To fetch from a real source, one simply updates the `fetch_content()` function to use the `requests` library.
* **Database**: SQLite is used per the requirements. For production, PostgreSQL would be ideal.
* **Matching Logic**: The baseline behavior searches for EXACT full-keyword matches in the title, then partial substrings in the title, and finally substrings in the body. Casing is ignored via `.lower()`.
* **Suppression Rule Logic**: 
  When the reviewer marks a flag as `irrelevant`, it remains `irrelevant` indefinitely. When `POST /scan/` is triggered:
  - If the flag status is `irrelevant`, the system compares `flag.content_last_updated` against the new `last_updated` timestamp of the fetched content.
  - If the content has not been updated since the flag was evaluated, the scan skips it (Suppression).
  - If the content *was* updated, the flag's status is reset to `pending` and its score is re-evaluated.
* **Separation of Concerns**: Django models handle data shapes. DRF handles API validation/routing. Pure business logic parsing/scoring/suppression was extracted perfectly into `monitoring/services.py`.

## Example cURL Requests

1. **Create a Keyword**
```bash
curl -X POST http://127.0.0.1:8000/api/keywords/ \
     -H "Content-Type: application/json" \
     -d '{"name": "django"}'

curl -X POST http://127.0.0.1:8000/api/keywords/ \
     -H "Content-Type: application/json" \
     -d '{"name": "python"}'
```

2. **Trigger a Scan**
This pulls the mock data, updates `ContentItem` models, runs the scoring mechanism, and creates/updates `Flag` models.
```bash
curl -X POST http://127.0.0.1:8000/api/scan/
```

3. **List all Flags**
```bash
curl -X GET http://127.0.0.1:8000/api/flags/
```

4. **Review a Flag**
Update the flag's status to `irrelevant` (replace `1` with an actual flag ID).
```bash
curl -X PATCH http://127.0.0.1:8000/api/flags/1/ \
     -H "Content-Type: application/json" \
     -d '{"status": "irrelevant"}'
```
