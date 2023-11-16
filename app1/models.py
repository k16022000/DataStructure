# from django.db import models
from mongoengine import fields, Document

class items(Document):
    name = fields.StringField()
    quantity = fields.IntField(default = 0)

# Create your models here.
