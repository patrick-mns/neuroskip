from peewee import Model, CharField, DateTimeField, AutoField, TextField, IntegerField, BooleanField
from datetime import datetime
from database import db

class Segment(Model):
    id = AutoField()                                          # Auto-incrementing primary key
    hash_id = CharField(max_length=255)                       # Identifier of the video associated with the segment
    start = CharField(max_length=10)                           # Segment start time
    end = CharField(max_length=10)                             # Segment end time
    text = TextField()                                        # Text content of the segment
    type = CharField(max_length=5, null=True)                 # Segment type (optional)
    revised = BooleanField(default=False)                     # Indicates if the segment has been revised
    revised_at = DateTimeField(null=True)                     # Revision date
    porcentage = IntegerField()                               # Percentage of video processing completion
    provider = CharField(max_length=15, null=True)            # Percentage of video processing completion
    external_id = CharField(max_length=15, null=True)         # External identifier
    created_at = DateTimeField(default=datetime.utcnow)       # Creation date
    updated_at = DateTimeField(default=datetime.utcnow)       # Last update date

    def save(self, *args, **kwargs):
        # Update the updated_at field on every save
        self.updated_at = datetime.utcnow()
        # Se revised for True e revised_at ainda não foi definido, define revised_at
        if self.revised and self.revised_at is None:
            self.revised_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    class Meta:
        database = db  # Conexão com o banco de dados
