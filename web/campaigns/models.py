from django.db import models
import uuid


class Campaign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    template = models.TextField()
    total_sent = models.IntegerField(default=0)
    total_delivered = models.IntegerField(default=0)
    total_failed = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'campaigns'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def delivery_rate(self):
        if self.total_sent == 0:
            return 0
        return round((self.total_delivered / self.total_sent) * 100, 1)


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    business_type = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contacts'

    def __str__(self):
        return f"{self.business_name} - {self.phone}"