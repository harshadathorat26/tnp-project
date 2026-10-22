from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    course = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, blank=True)
    college = models.CharField(max_length=100)
    previous_degree = models.CharField(max_length=100)
    graduation_percentage = models.CharField(max_length=100)
    skills = models.TextField(max_length = 500)
    github = models.TextField(max_length= 500)
    linkedin =models.TextField(max_length= 500)
    hackerrank = models.TextField(max_length= 500)
    codechef =models.TextField(max_length= 500)
    def __str__(self):
             return self.full_name
    
class Resume(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resume_file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class PlacementDrive(models.Model):
    company_name = models.CharField(max_length=100)
    job_role = models.CharField(max_length=100)
    package = models.CharField(max_length=50)
    eligibility = models.CharField(max_length=200)
    deadline = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.company_name + " - " + self.job_role


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
        ('Selected', 'Selected'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    drive = models.ForeignKey(PlacementDrive, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Applied'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'drive'],
                name='unique_student_drive_application'
            )
        ]

    def __str__(self):
        return f"{self.student.username} - {self.drive.company_name}"

class Notification(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title