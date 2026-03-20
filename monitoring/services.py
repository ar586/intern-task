import json
import re
from datetime import datetime
from django.utils import timezone
from .models import Keyword, ContentItem, Flag

MOCK_DATA = [
    {
        "external_id": "mock-a",
        "title": "Learn Django Fast",
        "body": "Django is a powerful Python framework",
        "source": "Blog A",
        "last_updated": "2026-03-20T10:00:00Z"
    },
    {
        "external_id": "mock-b",
        "title": "Cooking Tips",
        "body": "Best recipes for beginners",
        "source": "Blog B",
        "last_updated": "2026-03-20T10:00:00Z"
    },
    {
        "external_id": "mock-c",
        "title": "FastAPI vs Django",
        "body": "Which python framework is better for APIs?",
        "source": "Tech News",
        "last_updated": "2026-03-21T09:00:00Z"
    }
]

def fetch_content(source):
    if source == 'mock':
        return MOCK_DATA
    return []

def calculate_score(keyword_name, title, body):
    keyword_lower = keyword_name.lower()
    title_lower = title.lower()
    body_lower = body.lower()

    # Exact whole-word match in title
    if re.search(rf'\b{re.escape(keyword_lower)}\b', title_lower):
        return 100
    # Partial substring match in title
    elif keyword_lower in title_lower:
        return 70
    # Match in body only
    elif keyword_lower in body_lower:
        return 40
    
    return 0

def run_scan(source='mock'):
    raw_items = fetch_content(source)
    keywords = Keyword.objects.all()
    
    processed_count = 0

    for raw in raw_items:
        last_updated_dt = datetime.fromisoformat(raw['last_updated'].replace('Z', '+00:00'))
        
        # Use external_id as unique stable identifier
        content_item, _ = ContentItem.objects.update_or_create(
            external_id=raw['external_id'],
            defaults={
                'title': raw['title'],
                'source': raw['source'],
                'body': raw['body'],
                'last_updated': last_updated_dt
            }
        )

        for keyword in keywords:
            score = calculate_score(keyword.name, content_item.title, content_item.body)
            
            if score > 0:
                flag = Flag.objects.filter(keyword=keyword, content_item=content_item).first()
                
                if flag:
                    if flag.status == 'irrelevant':
                        if content_item.last_updated <= flag.content_last_updated:
                            continue
                        else:
                            flag.status = 'pending'
                            flag.score = score
                            flag.content_last_updated = content_item.last_updated
                            flag.save()
                            processed_count += 1
                    else:
                        # Only update if content changed
                        if content_item.last_updated > flag.content_last_updated:
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
