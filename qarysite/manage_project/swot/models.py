from django.db import models
from django.urls import reverse

# Create your models here.


class Purpose(models.Model):
    purpose = models.CharField(max_length=256)

    def __str__(self):
        return self.purpose

    def get_absolute_url(self):
        return reverse('swot:detail', kwargs={'pk': self.pk})


class SWOT(models.Model):
    strength = models.CharField(max_length=256, blank=True, default=None)
    strength_rate = models.PositiveIntegerField(null=True, default=0)
    weaknesses = models.CharField(max_length=256, blank=True, default=None)
    weaknesses_rate = models.PositiveIntegerField(null=True, default=0)
    oportinuties = models.CharField(max_length=256, blank=True, default=None)
    oportinuties_rate = models.PositiveIntegerField(null=True, default=0)
    threats = models.CharField(max_length=256, blank=True, default=None)
    threats_rate = models.PositiveIntegerField(null=True, default=0)
    strategy = models.TextField(blank=True, default=None)
    purpose = models.ForeignKey(
        Purpose, on_delete=models.CASCADE, related_name='s')

    def __str__(self):
        return self.strength

    # def get_absolute_url(self):
    #     return reverse('swot:detail', kwargs={'pk': self.pk})
