from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import OuterRef, Subquery
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import RegistrationSerializer, AnnouncementCommentSerializer
from .models import Registration, Announcement, AnnouncementComment
from .forms import RegistrationForm
from .choices import COURSE_CHOICES, LEVEL_CHOICES

class CustomLoginView(LoginView):
    template_name = 'backend/pages/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            registration = Registration.objects.get(username=request.user)
            if registration.sessions > 0:
                return redirect('user-home')
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
            messages.success(request, f"Account created for {user.username}")
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
                'profilepicture': reg.profilepicture,
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
                'profilepicture': 'profiles/default.jpg',
            }

    if not request.user.is_authenticated:
        return redirect('/')
    return render(request, 'backend/pages/home.html', context={ 'username': username, 'registration': registration })

@login_required
def profile(request):
    registration = {}

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
                'profilepicture': reg.profilepicture,
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
                'profilepicture': 'profiles/default.jpg',
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

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        if 'profilepicture' in request.FILES:
            instance.profilepicture = request.FILES['profilepicture']
            instance.save()
            return Response({"message": "Profile picture updated!", "profilepicture": instance.profilepicture.url}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@login_required
def announcements(request):    
    if request.user.is_authenticated:
        announcements = Announcement.objects.all()
        announcementcomments = {}
        
        for announcement in announcements:
            comment = list(AnnouncementComment.objects.filter(announcement=announcement).order_by('-updated_at')[:5])
            announcementcomments[announcement.id] = comment
        
        try:
            register = Registration.objects.get(username=request.user)
        except Registration.DoesNotExist:
            register = request.user
        return render(request, 'backend/pages/announcements.html', context={'announcements': announcements, 'announcementcomments': announcementcomments, 'register': register} )
    return redirect('/')
    
class AnnouncementCommentView(generics.ListCreateAPIView):
    queryset = AnnouncementComment.objects.all()
    serializer_class = AnnouncementCommentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@login_required
def reservation(request):
    if request.user.is_authenticated:
        return render(request, 'backend/pages/reservation.html')
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