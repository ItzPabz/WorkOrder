from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class CustomUser(AbstractUser):
    employee_id = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=[
        ('requestor', 'Requestor'),
        ('technician', 'Technician'),
        ('supervisor', 'Supervisor'),
        ('manager', 'Manager'),
        ('planner', 'Maintenance Planner'),
    ], default='requestor')
    department = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=False)

class Location(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_production_area = models.BooleanField(default=False)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f'{self.code} - {self.name}'
    
class AssetCategory(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    criticality_default = models.CharField(max_length=20, choices=[
        ('critical', 'Critical'),
        ('important', 'Important'),
        ('moderate', 'Moderate'),
        ('low', 'Low'),
    ], default='moderate')

    class Meta:
        verbose_name_plural = "Asset Categories"

    def __str__(self):
        return self.name
    
class WorkOrderType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    default_priority = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    requires_approval = models.BooleanField(default=False)
    approval_threshold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name