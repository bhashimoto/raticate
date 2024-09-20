import logging
from django.shortcuts import render
from django.shortcuts import HttpResponse, render

from .models import Post

logger = logging.getLogger(__name__)
# Create your views here.
def index(request):
    posts = Post.objects.filter(published_at__isnull=False).order_by("-published_at")[:5]

    return render(request, 'blog/index.html', {"posts": posts})

def post_details(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Exception:
        logger.error(f"Error trying to retrieve post with id: {post_id}")
    else:
        return render(request, 'blog/post_detail.html', {"post": post})