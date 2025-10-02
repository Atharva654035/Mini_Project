from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .encryption import EncryptedCharField, EncryptedTextField

# Create your models here.

class ComplaintCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Complaint Categories"

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Custom ID field starting from 100
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    name = EncryptedCharField(max_length=500)  # Encrypted name field (larger for encrypted data)
    division = models.CharField(max_length=100)  # Division can remain unencrypted
    complaint = EncryptedTextField()  # Encrypted complaint field
    complaint_img = models.FileField(upload_to='complaints/', blank=True, null=True)
    category = models.ForeignKey(ComplaintCategory, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    complaint_date = models.DateTimeField(default=timezone.now)
    resolved_date = models.DateTimeField(null=True, blank=True)
    admin_response = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new objects
            # Get the highest existing ID
            last_complaint = Complaint.objects.order_by('-id').first()
            if last_complaint:
                # If there are existing complaints, use the next ID
                next_id = max(last_complaint.id + 1, 100)
            else:
                # If no complaints exist, start from 100
                next_id = 100
            
            # Set the ID manually
            self.id = next_id
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Complaint #{self.id} by {self.name}"
    
    class Meta:
        ordering = ['-complaint_date']
        verbose_name = "Complaint"
        verbose_name_plural = "Complaints"

class ComplaintUpdate(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='updates')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    update_message = models.TextField(blank=True)
    updated_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Update for Complaint #{self.complaint.id}"
    
    class Meta:
        ordering = ['-updated_at']
