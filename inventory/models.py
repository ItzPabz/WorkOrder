from django.db import models
from maintenance.models import WorkOrder

class InventoryItem(models.Model):
    """Spare parts and supplies inventory"""
    UNIT_CHOICES = [
        ('each', 'Each'),
        ('ft', 'Feet'),
        ('lb', 'Pounds'),
        ('gal', 'Gallons'),
        ('set', 'Set'),
        ('box', 'Box'),
        ('roll', 'Roll'),
    ]
    
    part_number = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100, blank=True)
    supplier = models.CharField(max_length=100, blank=True)
    
    unit_of_measure = models.CharField(max_length=20, choices=UNIT_CHOICES, default='each')
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_on_hand = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_stock = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    location_in_warehouse = models.CharField(max_length=50, blank=True)
    is_critical = models.BooleanField(default=False)
    lead_time_days = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['part_number']
    
    def __str__(self):
        return f"{self.part_number} - {self.description}"
    
    @property
    def is_low_stock(self):
        return self.quantity_on_hand <= self.minimum_stock

class WorkOrderPart(models.Model):
    """Parts used in work orders"""
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='parts_used')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT)
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def total_cost(self):
        return self.quantity_used * self.unit_cost
