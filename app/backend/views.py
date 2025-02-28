from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import ValidationError
from .serializers import RegistrationSerializer, AnnouncementCommentSerializer
from .models import Registration, Announcement, AnnouncementComment, Sitin
from .forms import RegistrationForm
from .choices import COURSE_CHOICES, LEVEL_CHOICES, PROGRAMMING_LANGUAGE_CHOICES, SITIN_PURPOSE_CHOICES, LAB_ROOM_CHOICES
# Pillow Image Compression
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


class CustomLoginView(LoginView):
    template_name = 'backend/pages/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            registration = Registration.objects.get(username=request.user)
            if registration.sessions > 0:
                return redirect('user-home')
            else:
                pass # Logic handle for when user session runs out
        return super().dispatch(request, *args, **kwargs)

class CustomLogoutView(LogoutView):
    template_name = 'backend/pages/logout.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                registration = Registration.objects.get(username=request.user)
                if registration.sessions > 0:
                    registration.sessions -= 1
                    registration.save()
            except Registration.DoesNotExist:
                return redirect('login')
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
    username = request.user.username if request.user.is_authenticated else 'Guest'
    registration = {}
    announcements = Announcement.objects.all().order_by('-date')[:5]

    if request.user.is_authenticated:
        try:
            reg = Registration.objects.get(username=request.user)
            registration = {
                'idno': reg.idno,
                'fullname': ", ".join(filter(None, [reg.lastname, " ".join(filter(None, [reg.firstname, reg.middlename]))])),
                'fname': reg.firstname,
                'lname': reg.lastname,
                'mname': reg.middlename,
                'course': reg.course,
                'level': reg.level,
                'email': reg.email,
                'address': reg.address,
                'sessions': reg.sessions,
                'profilepicture': reg.profilepicture_md,
            }
        except Registration.DoesNotExist:
            registration = {
                'idno': '',
                'fullname': '',
                'fname': '',
                'lname': '',
                'mname': '',
                'course': '',
                'level': '',
                'email': '',
                'address': '',
                'sessions': '',
                'profilepicture': 'profiles/default_lg.jpg',
            }

    if not request.user.is_authenticated:
        return redirect('/')
    return render(request, 'backend/pages/home.html', context={ 'username': username, 'registration': registration, 'announcements': announcements })

@login_required
def profile(request):
    if request.user.is_authenticated:
        try:
            reg = Registration.objects.get(username=request.user)
            registration = {
                'idno': reg.idno,
                'fullname': ", ".join(filter(None, [reg.lastname, " ".join(filter(None, [reg.firstname, reg.middlename]))])),
                'fname': reg.firstname,
                'lname': reg.lastname,
                'mname': reg.middlename,
                'course': reg.course,
                'level': reg.level,
                'email': reg.email,
                'address': reg.address,
                'sessions': reg.sessions,
                'profilepicture': reg.profilepicture_md,    # I wanna use the medium photo
                'profiledescription': reg.profiledescription,
            }
        except Registration.DoesNotExist:
            registration = {
                'idno': '',
                'fullname': '',
                'fname': '',
                'lname': '',
                'mname': '',
                'course': '',
                'level': '',
                'email': '',
                'address': '',
                'sessions': '',
                'profilepicture': 'profiles/default_md.jpg',
                'profiledescription': '',
            }
        return render(request, 'backend/pages/profile.html', context={ 'registration': registration, 'course_choices': COURSE_CHOICES, 'level_choices': LEVEL_CHOICES })
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

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

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
        announcements = Announcement.objects.all().order_by('-updated_at')
        announcementcomments = {}
        
        for announcement in announcements:
            comment = list(AnnouncementComment.objects.filter(announcement=announcement).order_by('-updated_at')[:5])
            announcementcomments[announcement.id] = comment
            
        # Pagination (uses Paginator)
        paginator = Paginator(announcements, 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        try:
            register = Registration.objects.get(username=request.user)
        except Registration.DoesNotExist:
            register = request.user
        return render(request, 'backend/pages/announcements.html', context={'announcements': page_obj, 'announcementcomments': announcementcomments, 'register': register} )
    return redirect('/')

@login_required 
def announcement(request, announcement_id):
    if request.user.is_authenticated:
        announcement = get_object_or_404(Announcement, pk=announcement_id)
        comments = AnnouncementComment.objects.filter(announcement=announcement).order_by('-updated_at')

        # Pagination (uses Paginator)
        paginator = Paginator(comments, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'backend/pages/announcement.html', context={ 'announcement': announcement, 'announcementcomments': page_obj })
    return redirect('/')
    
class AnnouncementCommentCreateView(generics.ListCreateAPIView):
    queryset = AnnouncementComment.objects.all()
    serializer_class = AnnouncementCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        announcement_id = self.kwargs.get('announcement_id')
        user = self.request.user
        return AnnouncementComment.objects.filter(announcement=announcement_id, user=user)

    def perform_create(self, serializer):
        if self.request.data.get('comment') == '':
            raise ValidationError({'Comment': 'Empty comments are not allowed.'})
        announcement_id = self.kwargs.get('announcement_id')
        announcement = get_object_or_404(Announcement, id=announcement_id)
        serializer.save(user=self.request.user, announcement=announcement)
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'Created': 'Comment succesfully submitted.'}, status=status.HTTP_201_CREATED)

class AnnouncementCommentUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AnnouncementComment.objects.all()
    serializer_class = AnnouncementCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        announcement_id = self.kwargs.get('announcement_id')
        comment_id = self.kwargs.get('pk')
        obj = AnnouncementComment.objects.filter(announcement=announcement_id, id=comment_id)
        return obj
    
    def perform_update(self, serializer):
        if self.request.data.get('comment') == '':
            raise ValidationError({'Comment': 'Empty comments are not allowed.'})
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'Comment': 'Updated successfully.'}, status=status.HTTP_200_OK)
    
    def perform_destroy(self, instance):
        logged_user = self.request.user
        destroying_user = instance.user  # user stored within queryset
        if logged_user != destroying_user:
            raise ValidationError({'Not Allowed': 'Only the logged user can delete this comment!'})
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'Deleted': 'Comment successfully deleted.'}, status=status.HTTP_200_OK)

@login_required
def reservation(request):
    if request.user.is_authenticated:
        return render(request, 'backend/pages/reservation.html')
    return redirect('/')

@login_required
def sitin(request):
    if request.user.is_authenticated:
        try:    
            sitin = Sitin.objects.filter(user=request.user, status="pending")
        except Sitin.DoesNotExist:
            sitin = {}
        return render(request, 'backend/pages/sitin.html', 
        context={ 
            'purpose_choices': SITIN_PURPOSE_CHOICES, 
            'language_choices': PROGRAMMING_LANGUAGE_CHOICES, 
            'room_choices': LAB_ROOM_CHOICES, 
            'sitins': sitin})
    return redirect('/')

@login_required
def sitin_history(request):
    if request.user.is_authenticated:
        return render(request, 'backend/pages/sitin_history.html')
    return redirect('/')

@login_required
def sessions(request):
    if request.user.is_authenticated:
        return render(request, 'backend/pages/sessions.html')
    return redirect('/')

def error_404_view(request, exception):
    return render(request, 'backend/pages/404.html')