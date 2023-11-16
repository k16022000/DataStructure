# from django.db import models

from mongoengine import fields, Document, EmbeddedDocument,ReferenceField

class Instamart(Document):
    firstname = fields.StringField(max_length=50, required=True)
    lastname = fields.StringField(max_length=50, required=True)
    email = fields.EmailField(max_length=50, required=True)
    dateOfBirth = fields.DateField(required=True)
    password = fields.StringField(max_length=50, required=True)
    mobile_number = fields.IntField()

class package_contain(Document):
    name = fields.StringField()
    resource_link = fields.StringField()
    packagecontains_amount = fields.IntField()
    brand = fields.StringField()
    Dimension = fields.StringField()

class InstamartPackages(Document):
    expiry_date = fields.DateTimeField()
    package_image = fields.StringField()
    package = fields.StringField()
    package_amount = fields.IntField()
    combo = fields.StringField()
    resource_link = fields.StringField()
    # package_contains_list = fields.ListField(fields.EmbeddedDocumentField(package_contain),default = [])
    package_contains_list = fields.ListField(fields.ReferenceField(package_contain))
    