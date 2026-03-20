import json
from datetime import datetime
from django.utils import timezone
from .models import Keyword, ContentItem, Flag

MOCK_DATA = [
    {
        "title": "Learn Django Fast",
        "body": "Django is a powerful Python framework",
        "source": "Blog A",
        "last_updated": "2026-03-20T10:00:00Z"
    },
    {
        "title": "Cooking Tips",
        "body": "Best recipes for beginners",
        "source": "Blog B",
        "last_updated": "2026-03-20T10:00:00Z"
    },
    {
        "title": "FastAPI vs Django",
        "body": "Which python framework is better for APIs?",
        "source": "Tech News",
        "last_updated": "2026-03-21T09:00:00Z"
    },
     {
        "title": "i love django",
        "body": "Which python framework is better for APIs?",
        "source": "Tech News",
        "last_updated": "2026-03-21T09:00:00Z"
    }
    
]

def fetch_content(source):
    """
    Simulates fetching content from an external source.
    """
    if source == 'mock':
        return MOCK_DATA
    return []

def calculate_score(keyword_name, title, body):
    """
    Calculates the match score based on simple deterministic logic.
    - Exact keyword match in title: 100
    - Partial keyword match in title: 70
    - Keyword appears only in body: 40
    - No match: 0
    """
    keyword_lower = keyword_name.lower()
    title_lower = title.lower()
    body_lower = body.lower()

    if keyword_lower == title_lower:
        return 100
    elif keyword_lower in title_lower:
        return 70
    elif keyword_lower in body_lower:
        return 40
    
    return 0

def run_scan(source='mock'):
    """
    Fetches raw content items, saves them into the DB (or updates existing ones),
    then evaluates them against all Keywords to create/update Flags.
    """
    raw_items = fetch_content(source)
    keywords = Keyword.objects.all()
    
    processed_count = 0

    for raw in raw_items:
        last_updated_dt = datetime.fromisoformat(raw['last_updated'].replace('Z', '+00:00'))
        
        # Save or update ContentItem
        content_item, _ = ContentItem.objects.update_or_create(
            title=raw['title'],
            source=raw['source'],
            defaults={
                'body': raw['body'],
                'last_updated': last_updated_dt
            }
        )

        for keyword in keywords:
            score = calculate_score(keyword.name, content_item.title, content_item.body)
            
            if score > 0:
                flag = Flag.objects.filter(keyword=keyword, content_item=content_item).first()
                
                if flag:
                    # SUPPRESSION LOGIC
                    # If flag is irrelevant, skip unless content has been updated
                    if flag.status == 'irrelevant':
                        if content_item.last_updated <= flag.content_last_updated:
                            continue  # Suppress! Do not re-surface
                        else:
                            # Content changed: re-evaluate
                            flag.status = 'pending'
                    
                    flag.score = score
                    flag.content_last_updated = content_item.last_updated
                    flag.save()
                    processed_count += 1
                else:
                    # Create new flag
                    Flag.objects.create(
                        keyword=keyword,
                        content_item=content_item,
                        score=score,
                        status='pending',
                        content_last_updated=content_item.last_updated
                    )
                    processed_count += 1

    return {'processed': processed_count}
