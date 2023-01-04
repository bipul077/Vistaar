from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


# Create your models here.

STATES = (
    ("Province 1","Province 1"),
    ("Province 2","Province 2"),
    ("Bagmati","Bagmati"),
    ("Gandaki","Gandaki"),
    ("Lumbini","Lumbini"),
    ("Karnali","Karnali"),
    ("Sudur Paschim","Sudur Paschim")
)


class Supplier(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    verified = models.BooleanField(default=False)
    phone_number = models.PositiveIntegerField(null=True,blank=True)
    
    mobile_number = models.BigIntegerField()

    company_name = models.CharField(max_length=200)
    establishment_year = models.CharField(max_length=10)
    ceo_name = models.CharField(max_length=100)
    email = models.CharField(max_length=150)
    website = models.CharField(max_length=150)

    pin_code = models.CharField(max_length=15)
    state = models.CharField(max_length=50,choices=STATES)
    city = models.CharField(max_length=20)
    street = models.CharField(max_length=100)
    building_number = models.CharField(max_length=10, null=True, blank=True)
    locality = models.CharField(max_length=30, null=True, blank=True)
    landmark = models.CharField(max_length=50, null=True, blank=True)

    exim = models.CharField(max_length=20, null=True, blank=True)
    pan = models.CharField(max_length=20, null=True, blank=True)
    vat = models.CharField(max_length=20, null=True, blank=True)

    def get_image_path(self, filename):
        path = ''.join(['suppliers/',self.company_name,'/',filename])
        return path

    profile_picture = models.ImageField(upload_to=get_image_path, default='default.jpg', blank=True, null=True)
    qr_code = models.ImageField(upload_to=get_image_path, default='default.jpg', blank=True, null=True)

    def __str__(self):
        return self.company_name

    
class Company(models.Model):
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    establishment_year = models.CharField(max_length=10)
    ceo_name = models.CharField(max_length=100)
    email = models.CharField(max_length=150)
    website = models.CharField(max_length=150)

    def __str__(self) -> str:
        return self.company_name


class CompanyAddress(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    pin_code = models.CharField(max_length=15)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    building_number = models.CharField(max_length=10, null=True, blank=True)
    street = models.CharField(max_length=20, null=True, blank=True)
    locality = models.CharField(max_length=30, null=True, blank=True)
    landmark = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self) -> str:
        return self.company.name


class CompanyStatutory(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    exim = models.CharField(max_length=20)
    pan = models.CharField(max_length=20)
    vat = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.company.name