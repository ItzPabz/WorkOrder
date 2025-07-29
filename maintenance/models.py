from django.db import models
from core.models import AssetCategory, Location, WorkOrderType, CustomUser
from django.utils import timezone

class Asset(models.Model):
    """Equipment and assets in the bottling plant"""
    CRITICALITY_CHOICES = [
        ('critical', 'Critical - Production Stopping'),
        ('important', 'Important - Production Impact'),
        ('moderate', 'Moderate - Minor Impact'),
        ('low', 'Low - No Production Impact'),
    ]
    
    STATUS_CHOICES = [
        ('operational', 'Operational'),
        ('maintenance', 'Under Maintenance'),
        ('breakdown', 'Breakdown'),
        ('retired', 'Retired'),
    ]
    
    asset_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    parent_asset = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    # Technical specifications
    manufacturer = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    year_installed = models.IntegerField(null=True, blank=True)
    
    # Operational data
    criticality = models.CharField(max_length=20, choices=CRITICALITY_CHOICES, default='moderate')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='operational')
    production_line = models.CharField(max_length=50, blank=True)
    rated_capacity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    capacity_unit = models.CharField(max_length=20, blank=True)
    
    # Maintenance tracking
    runtime_hours = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cycle_count = models.BigIntegerField(default=0)
    last_pm_date = models.DateTimeField(null=True, blank=True)
    next_pm_date = models.DateTimeField(null=True, blank=True)
    pm_interval_hours = models.IntegerField(null=True, blank=True)
    
    # Financial
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    replacement_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['asset_id']
    
    def __str__(self):
        return f"{self.asset_id} - {self.name}"

class WorkOrder(models.Model):
    """Main work order model"""
    PRIORITY_CHOICES = [
        (1, 'Emergency - Immediate'),
        (2, 'Urgent - Same Day'),
        (3, 'High - 1-2 Days'),
        (4, 'Normal - 3-7 Days'),
        (5, 'Low - When Convenient'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]
    
    FAILURE_TYPE_CHOICES = [
        ('mechanical', 'Mechanical'),
        ('electrical', 'Electrical'),
        ('pneumatic', 'Pneumatic/Hydraulic'),
        ('process', 'Process Related'),
        ('software', 'Software/Controls'),
        ('preventive', 'Preventive Maintenance'),
        ('safety', 'Safety Related'),
        ('quality', 'Quality Issue'),
        ('other', 'Other'),
    ]
    
    # Identification
    work_order_id = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    work_order_type = models.ForeignKey(WorkOrderType, on_delete=models.PROTECT)
    
    # Assignment and workflow
    requester = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='requested_work_orders')
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_work_orders')
    supervisor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_work_orders')
    
    # Asset and location
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name='work_orders')
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    
    # Classification
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    failure_type = models.CharField(max_length=20, choices=FAILURE_TYPE_CHOICES, blank=True)
    
    # Production impact
    production_line_affected = models.CharField(max_length=50, blank=True)
    production_stopped = models.BooleanField(default=False)
    estimated_downtime_hours = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    actual_downtime_hours = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    estimated_production_loss = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    product_being_run = models.CharField(max_length=100, blank=True)
    
    # Environmental conditions
    temperature_at_failure = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    pressure_at_failure = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    environmental_notes = models.TextField(blank=True)
    
    # Timing
    requested_date = models.DateTimeField(default=timezone.now)
    target_completion_date = models.DateTimeField(null=True, blank=True)
    actual_start_date = models.DateTimeField(null=True, blank=True)
    actual_completion_date = models.DateTimeField(null=True, blank=True)
    
    # Cost tracking
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_labor_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actual_parts_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    contractor_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Completion details
    completion_notes = models.TextField(blank=True)
    root_cause = models.TextField(blank=True)
    corrective_action = models.TextField(blank=True)
    preventive_recommendations = models.TextField(blank=True)
    
    # Quality and safety
    safety_requirements = models.TextField(blank=True)
    lockout_required = models.BooleanField(default=False)
    permit_required = models.BooleanField(default=False)
    quality_check_required = models.BooleanField(default=False)
    sanitation_required = models.BooleanField(default=False)
    
    # Approval workflow
    requires_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_work_orders')
    approved_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.work_order_id:
            # Generate work order ID: WO-YYYY-NNNNNN
            year = timezone.now().year
            last_wo = WorkOrder.objects.filter(
                work_order_id__startswith=f'WO-{year}-'
            ).order_by('-work_order_id').first()
            
            if last_wo:
                last_num = int(last_wo.work_order_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.work_order_id = f'WO-{year}-{new_num:06d}'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.work_order_id} - {self.title}"
    
    @property
    def total_cost(self):
        return (self.actual_labor_cost or 0) + (self.actual_parts_cost or 0) + (self.contractor_cost or 0)

class WorkOrderAttachment(models.Model):
    """File attachments for work orders"""
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='workorder_attachments/%Y/%m/')
    filename = models.CharField(max_length=255)
    description = models.CharField(max_length=500, blank=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.work_order.work_order_id} - {self.filename}"

class WorkOrderComment(models.Model):
    """Comments and updates on work orders"""
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    comment = models.TextField()
    is_internal = models.BooleanField(default=False)  # Internal notes vs. public updates
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.work_order.work_order_id} - {self.author.username}"

class LaborLog(models.Model):
    """Track labor hours spent on work orders"""
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='labor_logs')
    technician = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['start_time']
    
    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            self.hours = duration.total_seconds() / 3600
        super().save(*args, **kwargs)
    
    @property
    def total_cost(self):
        return self.hours * self.hourly_rate
    
class DowntimeEvent(models.Model):
    """Track production downtime events"""
    DOWNTIME_REASON_CHOICES = [
        ('mechanical_failure', 'Mechanical Failure'),
        ('electrical_failure', 'Electrical Failure'),
        ('changeover', 'Product Changeover'),
        ('planned_maintenance', 'Planned Maintenance'),
        ('unplanned_maintenance', 'Unplanned Maintenance'),
        ('quality_issue', 'Quality Issue'),
        ('material_shortage', 'Material Shortage'),
        ('operator_issue', 'Operator Issue'),
        ('other', 'Other'),
    ]
    
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='downtime_events', null=True, blank=True)
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)
    production_line = models.CharField(max_length=50)
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    
    reason_code = models.CharField(max_length=30, choices=DOWNTIME_REASON_CHOICES)
    description = models.TextField()
    product_affected = models.CharField(max_length=100, blank=True)
    production_rate_loss = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    reported_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_time']
    
    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            self.duration_minutes = duration.total_seconds() / 60
        super().save(*args, **kwargs)