from django.db import models
from django.contrib.auth.models import User
import markdown

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200, blank=False)
    text = models.TextField(blank=False)
    
    author = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    @property
    def html(self):
        md = markdown.Markdown(extensions=["fenced_code", "sane_lists"])
        text = md.convert(self.text)
        print(text)
        return text