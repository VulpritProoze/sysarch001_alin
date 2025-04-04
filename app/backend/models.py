from django.db import models
from django.contrib.auth.models import User, AbstractUser
from .choices import COURSE_CHOICES, LEVEL_CHOICES, PROGRAMMING_LANGUAGE_CHOICES, LAB_ROOM_CHOICES, SITIN_PURPOSE_CHOICES, SITIN_STATUS_CHOICES, RATING_CHOICES, QUESTION_CHOICES, SURVEY_STATUS_CHOICES

class Registration(models.Model):
    idno = models.IntegerField(primary_key=True)
    lastname = models.CharField(max_length=80, null=True, blank=True)
    firstname = models.CharField(max_length=80, null=True, blank=True)
    middlename = models.CharField(max_length=80, null=True, blank=True)
    course = models.CharField(max_length=80, choices=COURSE_CHOICES, null=True, blank=True)
    level = models.IntegerField(null=True, choices=LEVEL_CHOICES, blank=True)
    email = models.EmailField(max_length=80, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    sessions = models.IntegerField(default=30, null=True, blank=True)
    points = models.IntegerField(default=0, null=True, blank=True)
    sitins_count = models.IntegerField(default=0, null=True, blank=True)
    profilepicture_og = models.ImageField(upload_to="profiles/", default="profiles/default.jpg", blank=True, null=True)
    profilepicture_lg = models.ImageField(upload_to="profiles/", default="profiles/default_lg.jpg", blank=True, null=True)
    profilepicture_md = models.ImageField(upload_to="profiles/", default="profiles/default_md.jpg", blank=True, null=True)
    profilepicture_sm = models.ImageField(upload_to="profiles/", default="profiles/default_sm.jpg", blank=True, null=True)
    profiledescription = models.TextField(blank=True, null=True)
    username = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"ID #: {self.idno}, Fullname: {self.firstname} {self.lastname}"

class Announcement(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="announcements/", default="announcements/announcement.jpg", blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    superuser = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_superuser': True})

    def __str__(self):
        return f"\"{self.title}\", by {self.superuser.username}"
    
class AnnouncementComment(models.Model):
    comment = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Commented on \"{self.announcement.title}\", by {self.user.username}"
    
# Make survey questions for each survey (so that we can query results per survey question)
''' 
    I shall use signals such that when a sitinsurvey is
    created (or submitted by user), 5 survey responses is 
    generated along side it which all has blank rating,
    but each response should have different questions. 
'''
class SitinSurvey(models.Model):
    status = models.CharField(max_length=50, choices=SURVEY_STATUS_CHOICES, default='not taken')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Survey results for {self.created_by.username}, at {self.created_at}"

# Store rating for each question
class SurveyResponse(models.Model):
    question_choices = QUESTION_CHOICES
    
    survey = models.ForeignKey(SitinSurvey, on_delete=models.CASCADE)
    question_order = models.IntegerField(null=True, blank=True)
    question_text = models.TextField(null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"#{self.question_order}"

class Sitin(models.Model):
    purpose = models.CharField(max_length=255, choices=SITIN_PURPOSE_CHOICES, blank=True, null=True)
    programming_language = models.CharField(max_length=255, choices=PROGRAMMING_LANGUAGE_CHOICES, blank=True, null=True)
    lab_room = models.CharField(max_length=50, choices=LAB_ROOM_CHOICES, blank=True, null=True)
    sitin_details = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=SITIN_STATUS_CHOICES, default="none") # none, approved, denied
    sitin_date = models.DateTimeField(auto_now_add=True)
    logout_date = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"By {self.user.username}, at {self.lab_room}, status: {self.status}"

# Not implemented yet
class LabResource(models.Model):
    url = models.URLField(blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"\"{self.title}\" by {self.created_by}"



