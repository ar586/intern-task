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
5. **Run Tests**:
   The logic is covered by automated unit tests.
   ```bash
   python manage.py test
   ```
6. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

## Assumptions, Trade-offs & Architecture
* **External Source & Deduplication**: I opted for a mock payload in `services.py`. Content duplication is prevented by using a unique `external_id` as a stable identifier for each article, ensuring title edits don't spawn duplicate `ContentItem` instances into the database.
* **Database**: SQLite is used per the requirements. For production, PostgreSQL would be ideal.
* **Matching Logic**: 
  - Score 100: **Exact whole-word match** in the title (checked efficiently via regex boundaries).
  - Score 70: Partial substring match in the title.
  - Score 40: Substring match anywhere in the body.
* **Suppression Rule**: 
  When the reviewer marks a flag as `irrelevant`, it remains `irrelevant` indefinitely. On subsequent scans (`POST /scan/`), the logic compares `flag.content_last_updated` against the article's `last_updated`. The flag is ignored (*suppressed*) unless the article content actually changed since the human review. Additionally, if the flag is `relevant` or `pending`, it is only overwritten if the underlying content has actually been updated, preserving the reviewer's work.
* **Separation of Concerns**: Django models handle data shapes. DRF handles API validation/routing. Pure business logic parsing/scoring/suppression was extracted perfectly into `monitoring/services.py`. All API errors explicitly return standard JSON 500 responses instead of raw Django traces.

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
