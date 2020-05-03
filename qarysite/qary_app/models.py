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

    def __str__(self):

        return f"{self.question} {self.answer} {self.create_date}"

    def get_absolute_url(self):
        return reverse('chat', kwargs={pk: self.pk})

# this class to save data from scrape wikipedia


class Document(models.Model):

    title = models.TextField()
    text = models.TextField(null=True,
                            blank=True)
    url = models.URLField(max_length=250, null=True,
                          blank=True)  # change the kind

    def __str__(self):
        return self.title
