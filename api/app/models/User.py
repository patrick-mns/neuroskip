from peewee import Model, CharField, DateTimeField, AutoField, TextField, IntegerField, BooleanField, DecimalField
from datetime import datetime
from database import db
import decimal

class User(Model):
    
    id = AutoField()
    google_id = CharField(unique=True, index=True)
    email = CharField(unique=True, index=True)
    name = CharField(null=True)
    given_name = CharField(null=True)
    picture = CharField(null=True)
    balance = DecimalField(default=0)                         # User's balance 
    requests = IntegerField(default=0)                        # Number of requests made by the user
    created_at = DateTimeField(default=datetime.utcnow)       # Creation date
    updated_at = DateTimeField(default=datetime.utcnow)       # Last update date

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def get_user_by_google_id(google_id: str):
        try:
            return User.get(User.google_id == google_id)
        except User.DoesNotExist:
            return None
    
    def add_balance(self, amount: decimal.Decimal):
        if amount < 0:
            raise ValueError("Amount must be positive")
        self.balance += amount
        self.save()
        
    def subtract_balance(self, amount: float):
        if amount < 0:
            raise ValueError("Amount must be positive")
        if self.balance < amount:
            raise ValueError("Insufficient balance")
        self.balance -= amount
        self.save()
    
    class Meta:
        database = db
        table_name = 'users'
