from django.db import models
from django.urls import reverse
from django.utils import timezone


class Post(models.Model):
    author = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    text = models.TextField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={pk: self.pk})


class Chat(models.Model):

    question = models.TextField()
    answer = models.TextField()
    create_date = models.DateTimeField(default=timezone.now())
    # bot_skill = models.CharField(max_length=200)

    def __str__(self):

        return f"{self.question} {self.answer} {self.create_date}"

    def get_absolute_url(self):
        return reverse('chat', kwargs={pk: self.pk})

# this class to save data from scrape wikipedia


class Document(models.Model):

    title = models.CharField(max_length=200, null=True,
                             blank=True)
    text = models.TextField(null=True,
                            blank=True)
    summary = models.TextField(null=True,
                               blank=True)

    def __str__(self):
        return self.title
