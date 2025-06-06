from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
# from rest_framework.exceptions import ValidationError
from .serializers import RegistrationSerializer, AnnouncementCommentSerializer, SitinSurveySerializer
from .models import Registration, Announcement, AnnouncementComment, SitinSurvey, LabResource
from .forms import RegistrationForm, StudyLoadUploadForm
from .choices import COURSE_CHOICES, LEVEL_CHOICES, LAB_ROOM_CHOICES, QUESTION_CHOICES
# Pillow Image Compression
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os
class CustomLoginView(LoginView):
    template_name = 'backend/pages/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            registration = Registration.objects.get(username=request.user)
            if registration.sessions > 0:
                return redirect('user-home')
            else:
                messages.error('You have ran out of sessions. Please contact the lab admin for more details.')
                return redirect('login')
        return super().dispatch(request, *args, **kwargs)

class CustomLogoutView(LogoutView):
    template_name = 'backend/pages/logout.html'
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Registration.objects.create(
                username=user,
                idno=request.POST['idno'],
                lastname=request.POST['lastname'],
                firstname=request.POST['firstname'],
                middlename=request.POST['middlename'],
                course=request.POST['course'],
                level=request.POST['level'],
                email=request.POST['email'],
                address=request.POST['address'],
            )
            messages.success(request, f'Account: You have succesfully created an account, {user.username}!')
            return redirect('/')
        else:
            return render(request, 'backend/pages/register.html', {'form': form, 'error': 'Please correct the errors below' })
    else: 
        form = RegistrationForm()
    return render(request, 'backend/pages/register.html', {'form': form})    

@login_required
def home(request):
    if request.user.is_authenticated:
        reg = Registration.objects.get(username=request.user)
        announcements = Announcement.objects.all().order_by('-date')[:5]
        students_leaderboard = Registration.objects.all().select_related('username').order_by('-points', '-sitins_count')
        # client-side filter
        is_top_performing = request.GET.get('is_top_performing')
        if is_top_performing == 'False':
            students_leaderboard = students_leaderboard.order_by('-sitins_count', '-points')
        # Pagination
        paginator = Paginator(students_leaderboard, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'backend/pages/home.html', context={ 'registration': reg, 'announcements': announcements, 'students_leaderboard': page_obj })
    return redirect('/')

@login_required
def profile(request):
    if request.user.is_authenticated:
        context = {
            'course_choices': COURSE_CHOICES, 
            'level_choices': LEVEL_CHOICES    
        }
        if request.method == 'POST':
            user = Registration.objects.get(idno=request.user.registration.idno)
            if user.points > 0:
                added_points = int(user.points / 3)
                user.sessions += added_points
                context['message'] = f'{user.points} points converted into {added_points} sessions.'
                context['message_type'] = 'success'
                user.points = 0
                user.save()
            else:
                context['message'] = 'You have no points left.'
                context['message_type'] = 'error'
        reg = Registration.objects.get(username=request.user)
        context['registration'] = reg
        return render(request, 'backend/pages/profile.html', context)
    return redirect('/')

class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    lookup_field = 'idno'
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def compress_image(self, uploaded_file, max_size, quality=80):
        img = Image.open(uploaded_file)
        # Convert RGB from alpha channel image
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail(max_size, Image.LANCZOS)
        img_io = BytesIO()
        img.save(img_io, format="JPEG", quality=quality, optimize=True)
        return ContentFile(img_io.getvalue(), name=uploaded_file.name)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Currently no feature to delete old images

        if 'profilepicture' in request.FILES:
            uploaded_file = request.FILES.get('profilepicture')
            instance.profilepicture_og = uploaded_file
            instance.profilepicture_lg = self.compress_image(uploaded_file, (1200, 1200), quality=85)
            instance.profilepicture_md = self.compress_image(uploaded_file, (600, 600), quality=75)
            instance.profilepicture_sm = self.compress_image(uploaded_file, (150, 150), quality=40)
            instance.save()
            return Response({'Profile': 'Profile picture successfully updated.'})   # Separate saving of profile picture and profile details

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'Profile': 'Profile details updated successfully.'}, status=status.HTTP_200_OK)

@login_required
def announcements(request):    
    if request.user.is_authenticated:
        # Optimize queries for announcements joining announcementcomments
        # and related announcementcomments joining user_registration
        announcements = Announcement.objects.all().prefetch_related(
            Prefetch(
                'announcementcomment_set',
                queryset=AnnouncementComment.objects.select_related(
                    'user',
                    'user__registration'
                ).order_by('-date')
            )
        ).order_by('-updated_at')
        # Pagination (uses Paginator)
        paginator = Paginator(announcements, 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        try:
            register = Registration.objects.get(username=request.user)
        except Registration.DoesNotExist:
            register = request.user
        return render(request, 'backend/pages/announcements.html', context={'announcements': page_obj, 'register': register} )
    return redirect('/')

@login_required 
def announcement(request, announcement_id):
    if request.user.is_authenticated:
        announcement = get_object_or_404(Announcement, pk=announcement_id)
        comments = AnnouncementComment.objects.filter(
            announcement=announcement
        ).select_related(
            'user',  # Fetches the related User in the same query
            'user__registration'  # Fetches the related Registration in the same query
        ).order_by('-updated_at')

        # Pagination (uses Paginator)
        paginator = Paginator(comments, 30)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'backend/pages/announcement.html', context={ 'announcement': announcement, 'announcementcomments': page_obj })
    return redirect('/')
    
class AnnouncementCommentCreateView(generics.CreateAPIView):
    serializer_class = AnnouncementCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        announcement = self.kwargs.get('announcement_id')
        return AnnouncementComment.objects.filter(user=self.request.user, announcement=announcement)
    
    # Have to manually pass user and announcement foreign keys
    def perform_create(self, serializer):
        # serializer.save only accepts actual instance of the model object
        announcement = get_object_or_404(Announcement, id=self.kwargs.get('announcement_id'))
        serializer.save(user=self.request.user, announcement=announcement)

class AnnouncementCommentUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AnnouncementComment.objects.all()
    serializer_class = AnnouncementCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        announcement_id = self.kwargs.get('announcement_id')
        comment_id = self.kwargs.get('pk')
        obj = AnnouncementComment.objects.filter(announcement=announcement_id, id=comment_id)
        return obj

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'Comment': 'Updated successfully.'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'Deleted': 'Comment successfully deleted.'}, status=status.HTTP_200_OK)
    
@login_required
def survey(request):
    if request.user.is_authenticated:
        sitinsurvey = SitinSurvey.objects.filter(
            created_by=request.user
        ).prefetch_related('surveyresponse_set').first()
        
        if sitinsurvey and sitinsurvey.status == 'not taken':
            # Pair questions with their responses
            questions_with_responses = []
            for i, question in enumerate(QUESTION_CHOICES):
                try:
                    response = sitinsurvey.surveyresponse_set.all()[i]
                except IndexError:
                    response = None
                questions_with_responses.append({
                    'question': question,
                    'response': response
                })
            
            context = {
                'questions_with_responses': questions_with_responses,
                'sitinsurvey': sitinsurvey
            }
            return render(request, 'backend/pages/survey.html', context)
    return redirect('/')

class SitinSurveyUpdateView(generics.RetrieveUpdateAPIView):
    queryset = SitinSurvey.objects.all()
    serializer_class = SitinSurveySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        id = self.kwargs.get('pk')
        user = self.request.user
        return SitinSurvey.objects.filter(id=id, created_by=user)
    
    def update_survey_status(self, survey):
        has_unanswered = survey.surveyresponse_set.filter(rating__isnull=True).exists()
        new_status = 'taken' if not has_unanswered else 'not taken'
        
        # Only update if status actually changed
        if survey.status != new_status:
            survey.status = new_status
            survey.save(update_fields=['status'])

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        responses = request.data.get('responses', {})
        
        # Update responses
        for question_id, rating in responses.items():
            try:
                survey_response = instance.surveyresponse_set.filter(
                    id=question_id
                ).first()
                if survey_response:
                    survey_response.rating = rating
                    survey_response.save()
            except (ValueError, TypeError):
                continue
                
        # Update survey status
        self.update_survey_status(instance)

        return Response({'Survey': 'Successfully submitted.'}, status=status.HTTP_200_OK)

@login_required
def resources(request):
    if request.user.is_authenticated:
        # Using Django's forms to update image
        if request.method == 'POST':
            try:
                registration = request.user.registration 
            except Registration.DoesNotExist:
                print('Registration not found')
                return redirect('/resources')
            
            old_image = registration.study_load
            form = StudyLoadUploadForm(request.POST, request.FILES, instance=registration)
            if form.is_valid():
                print('\nold_image', old_image)
                print(type(old_image))
                print('path -> ', old_image.path, old_image.name)
                
                # delete old image
                if old_image:
                    try:
                        if os.path.exists(old_image.path):
                            os.remove(old_image.path)
                    except Exception as e:
                        print("Couldn't delete old image", str(e))
                        
                form.save()
                return redirect('/resources')
            
        lab_resources = LabResource.objects.all().filter(is_enabled=True)
        schedule = Registration.objects.only('study_load').get(idno=request.user.registration.idno)
        return render(request, 'backend/pages/resources.html', context={ 'lab_resources': lab_resources, 'schedule': schedule })
    return redirect('/')

@login_required
def sessions(request):
    if request.user.is_authenticated:
        return render(request, 'backend/pages/sessions.html')
    return redirect('/')
    
def error_404_view(request, exception):
    return render(request, 'backend/pages/404.html')