from django.db import models
from django.conf import settings

# お店モデル（Item）がすでにある前提）
from base.models import Item  

# ----------------------
# 予約モデル
# ----------------------
class Reservation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations"
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="reservations"
    )
    date_time = models.DateTimeField()
    num_people = models.PositiveIntegerField()
    seat_type = models.CharField(
        max_length=20,
        choices=[
            ("テーブル席", "テーブル席"),
            ("カウンター席", "カウンター席")
        ]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} - {self.user.username} ({self.date_time})"


