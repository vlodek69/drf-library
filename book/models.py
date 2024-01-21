from django.db import models


class Book(models.Model):
    HARD = "HC"
    SOFT = "SC"
    COVER_CHOICES = {HARD: "Hard", SOFT: "Soft"}
    cover = models.CharField(max_length=2, choices=COVER_CHOICES, default=SOFT)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title + " ($" + str(self.daily_fee) + ")"
