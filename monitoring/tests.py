from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import Keyword, ContentItem, Flag
from .services import calculate_score, run_scan

class ScoringTests(TestCase):
    def test_exact_title_match(self):
        self.assertEqual(calculate_score("django", "django", "some body"), 100)

    def test_partial_title_match(self):
        self.assertEqual(calculate_score("djan", "Learn Django Fast", "body"), 70)

    def test_body_only_match(self):
        self.assertEqual(calculate_score("django", "Cooking Tips", "Django is great"), 40)

    def test_no_match(self):
        self.assertEqual(calculate_score("django", "Cooking Tips", "Best recipes"), 0)

    def test_case_insensitive(self):
        self.assertEqual(calculate_score("DJANGO", "Learn Django Fast", "body"), 100)

class SuppressionTests(TestCase):
    def test_irrelevant_flag_is_suppressed(self):
        kw = Keyword.objects.create(name="django")
        item = ContentItem.objects.create(
            external_id="mock-1",
            title="Learn Django", 
            body="body", 
            source="mock",
            last_updated=timezone.now() - timedelta(days=1)
        )
        Flag.objects.create(
            keyword=kw, 
            content_item=item, 
            score=70,
            status='irrelevant',
            content_last_updated=item.last_updated
        )
        
        # Run scan - content hasn't changed. The mock data has fixed entries, 
        # so this test's item won't be updated by run_scan's mock unless we mock it specifically.
        # But wait, run_scan gets MOCK_DATA. Let's patch MOCK_DATA to just this item.
        import monitoring.services as services
        original_mock = services.MOCK_DATA
        services.MOCK_DATA = [{
            "external_id": "mock-1",
            "title": "Learn Django",
            "body": "body",
            "source": "mock",
            "last_updated": item.last_updated.isoformat().replace('+00:00', 'Z')
        }]
        
        try:
            run_scan(source='mock')
            flag = Flag.objects.get(keyword=kw, content_item=item)
            self.assertEqual(flag.status, 'irrelevant')
        finally:
            services.MOCK_DATA = original_mock
