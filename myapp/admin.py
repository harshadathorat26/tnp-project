from django.contrib import admin
from .models import StudentProfile
from .models import Resume
from .models import PlacementDrive, JobApplication
from .models import Notification

admin.site.register(StudentProfile)
admin.site.register(Resume)
admin.site.register(PlacementDrive)
admin.site.register(JobApplication)
admin.site.register(Notification)
# Register your models here