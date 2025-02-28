from django.db import models
from django.contrib.auth.models import User

class Registration(models.Model):
    idno = models.IntegerField(primary_key=True)
    lastname = models.CharField(max_length=80, null=True, blank=True)
    firstname = models.CharField(max_length=80, null=True, blank=True)
    middlename = models.CharField(max_length=80, null=True, blank=True)
    course = models.CharField(max_length=80, null=True, blank=True)
    level = models.IntegerField(null=True, blank=True)
    email = models.EmailField(max_length=80, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    sessions = models.IntegerField(default=30, null=True, blank=True)
    profilepicture_og = models.ImageField(upload_to="profiles/", default="profiles/default.jpg", blank=True, null=True)
    profilepicture_lg = models.ImageField(upload_to="profiles/", default="profiles/default_lg.jpg", blank=True, null=True)
    profilepicture_md = models.ImageField(upload_to="profiles/", default="profiles/default_md.jpg", blank=True, null=True)
    profilepicture_sm = models.ImageField(upload_to="profiles/", default="profiles/default_sm.jpg", blank=True, null=True)
    profiledescription = models.TextField(blank=True, null=True)
    username = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.idno}, {self.username}, {self.firstname} {self.lastname}"

class Announcement(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="announcements/", default="announcements/announcement.jpg", blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    superuser = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_superuser': True})

    def __str__(self):
        return f"{self.title}, {self.superuser.username}"
    
class AnnouncementComment(models.Model):
    comment = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.comment}, {self.user.username}"
    
class Sitin(models.Model):
    purpose = models.CharField(max_length=255, blank=True, null=True)
    programming_language = models.CharField(max_length=255, blank=True, null=True)
    lab_room = models.CharField(max_length=50, blank=True, null=True)
    sitin_details = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True) # pending, approved, denied
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.username}, {self.lab_room}, {self.status}"





