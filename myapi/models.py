from django.db import models

class Transaction(models.Model):
    SUCCESS = 'success'
    FAILED = 'failed'

    wallet_address = models.CharField(max_length=255)
    transaction_id = models.CharField(max_length=255, default="none") #added default
    status = models.CharField(max_length=50, choices=[
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
    ])
    timestamp = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(default="none") #added  error_message and default
    def __str__(self):
        return f'Transaction {self.transaction_id}'
