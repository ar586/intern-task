from django.db import models

class Keyword(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ContentItem(models.Model):
    external_id = models.CharField(max_length=255, unique=True, default='')
    title = models.CharField(max_length=512)
    source = models.CharField(max_length=100)
    body = models.TextField()
    last_updated = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.source})"

class Flag(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('relevant', 'Relevant'),
        ('irrelevant', 'Irrelevant'),
    ]

    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name='flags')
    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE, related_name='flags')
    score = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Store the item's last_updated value when this flag was created or last modified.
    # This helps with the suppression rule.
    content_last_updated = models.DateTimeField()

    class Meta:
        # A keyword and a content item should only have one flag together
        unique_together = ('keyword', 'content_item')

    def __str__(self):
        return f"Flag for '{self.keyword.name}' on '{self.content_item.title[:20]}...' (Status: {self.status})"
