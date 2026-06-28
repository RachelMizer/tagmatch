from django.db import models
from django.contrib.auth.models import User


class Match(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="matches"
    )
    matched_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="matched_by"
    )
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} matched with {self.matched_user.username} ({self.score}%)"
