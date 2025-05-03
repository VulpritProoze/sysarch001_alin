from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils import timezone
from .models import Registration, SitinSurvey, SurveyResponse, Announcement
from notifications.notifications import send_notification

@receiver(post_save, sender=User)
def create_superuser_registration(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        Registration.objects.create(username=instance, email=instance.email)
        
@receiver(post_save, sender=Announcement)
def notif_on_announcement_create(sender, instance, created, **kwargs):
    if created:
        for user in User.objects.filter(is_active=True):
            send_notification(user, instance.title, f"/announcements/{instance.id}/", 'announcement')
        
        # channel_layer = get_channel_layer()
        
        # # Create notif for all active users
        # for user in User.objects.filter(is_active=True):
        #     notification = Notification.objects.create(
        #         user=user,
        #         message = f"Announcement: {instance.title}",
        #         url = f"/announcements/{instance.id}/"
        #     )
            
        #     async_to_sync(channel_layer.group_send)(
        #         f'user_{user.id}',
        #         {
        #             'type': 'notification.message',
        #             'notification_type': 'notification',
        #             'id': notification.id,
        #             'message': notification.message,
        #             'url': notification.url,
        #             'timestamp': timezone.now(),
        #             'is_read': False
        #         }
        #     )

# I have a feeling this slows down program really bad
# Ideal: since survey creation is only called few times. set-up the this change on those endpoints instead of signals
# Create an instance of SitinSurvey once user's session reaches 10
@receiver(post_save, sender=Registration)
def create_survey_on_session_threshold(sender, instance, created, **kwargs):
    if instance.sessions <= 10:
        user = instance.username 
        # Ensure there is only one SitinSurvey per user
        if not SitinSurvey.objects.filter(created_by=user).exists():
            SitinSurvey.objects.create(created_by=user)

@receiver(post_save, sender=SitinSurvey)
def create_questions_on_create(sender, instance, created, **kwargs):
    # If survey is created, create set questions on it
    if created:
        # Create questions for new survey
        for value, text in SurveyResponse.question_choices:
            SurveyResponse.objects.create(survey=instance, question_order=value, question_text=text)
        
@receiver(post_save, sender=SurveyResponse)
def update_survey_status_on_response_change(sender, instance, **kwargs):
    """Update survey status whenever a response is saved/changed"""
    survey = instance.survey
    has_unanswered = survey.surveyresponse_set.filter(rating__isnull=True).exists()
    SitinSurvey.objects.filter(pk=survey.pk).update(
        status='taken' if not has_unanswered else 'not taken'
    )
