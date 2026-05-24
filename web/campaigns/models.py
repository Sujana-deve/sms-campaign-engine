from django.db import models
import uuid


class Campaign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='draft')
    trigger_type = models.CharField(max_length=50, default='manual')
    template = models.TextField()
    segment_filter = models.JSONField(default=dict)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'campaigns'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class CampaignLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE, db_column='campaign_id')
    total_contacts = models.IntegerField(default=0)
    sent = models.IntegerField(default=0)
    delivered = models.IntegerField(default=0)
    failed = models.IntegerField(default=0)
    opted_out_skipped = models.IntegerField(default=0)
    cost_npr = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'campaign_logs'

    @property
    def delivery_rate(self):
        if self.sent == 0:
            return 0
        return round((self.delivered / self.sent) * 100, 1)


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    attributes = models.JSONField(default=dict, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contacts'

    def __str__(self):
        return f"{self.business_name} - {self.phone}"