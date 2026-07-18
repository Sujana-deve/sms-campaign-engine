from django.db import models
import uuid


class InsufficientBalanceError(Exception):
    """Raised when a deduction would take the balance below zero."""
    pass


class Balance(models.Model):
    """
    Singleton row holding the SMS credit balance. Global, not per-client —
    the multi-client story here is separate DBs/instances per client
    (decided earlier), not multiple balance rows in one DB. If that ever
    changes, this model changes with it — not before.

    Always access through get_singleton() / get_locked_singleton(), never
    Balance.objects.create() directly.
    """
    id = models.SmallIntegerField(primary_key=True, default=1, editable=False)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'balance'

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce singleton no matter how it's constructed
        super().save(*args, **kwargs)

    @classmethod
    def get_singleton(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={'current_balance': 0})
        return obj

    @classmethod
    def get_locked_singleton(cls):
        """
        Row-locked version (SELECT ... FOR UPDATE). Must be called inside
        transaction.atomic(). Use this before any check-then-deduct
        sequence — otherwise two concurrent requests (e.g. a campaign
        launch racing a top-up) can both read the same stale balance.
        """
        cls.objects.get_or_create(pk=1, defaults={'current_balance': 0})
        return cls.objects.select_for_update().get(pk=1)

    def has_sufficient(self, amount):
        return self.current_balance >= amount

    def deduct(self, amount, reference=''):
        """Call only on an instance from get_locked_singleton(), inside the same atomic block."""
        if amount <= 0:
            raise ValueError("Deduction amount must be positive")
        if not self.has_sufficient(amount):
            raise InsufficientBalanceError(
                f"Balance {self.current_balance} insufficient for deduction {amount}"
            )
        self.current_balance -= amount
        self.save()
        Transaction.objects.create(
            type=Transaction.Type.DEDUCTION,
            amount=amount,
            balance_after=self.current_balance,
            reference=reference,
        )

    def top_up(self, amount, reference=''):
        """Call only on an instance from get_locked_singleton(), inside the same atomic block."""
        if amount <= 0:
            raise ValueError("Top-up amount must be positive")
        self.current_balance += amount
        self.save()
        Transaction.objects.create(
            type=Transaction.Type.TOPUP,
            amount=amount,
            balance_after=self.current_balance,
            reference=reference,
        )

    def __str__(self):
        return f"Balance: Rs. {self.current_balance}"


class Transaction(models.Model):
    """
    Append-only ledger of every balance change — top-ups (eSewa) and
    deductions (campaign launches). This is the audit trail, not the
    source of truth — Balance.current_balance is authoritative; this is
    the record of how it got there, for when Aashish asks "where did the
    money go."
    """
    class Type(models.TextChoices):
        TOPUP = 'topup', 'Top-up'
        DEDUCTION = 'deduction', 'Deduction'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, choices=Type.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=255, blank=True)  # eSewa transaction_uuid for top-ups, campaign id for deductions
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'balance_transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type} Rs.{self.amount} -> {self.balance_after}"