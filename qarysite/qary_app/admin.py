from django.contrib import admin

from . models import Post, Chat, Document

admin.site.register(Post)
admin.site.register(Chat)
admin.site.register(Document)
