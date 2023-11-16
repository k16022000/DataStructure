# from django.db import models
from mongoengine import fields, Document

class Books(Document):
    title = fields.StringField(max_length=50)
    price = fields.IntField(default = 0)
# Create your models here.
