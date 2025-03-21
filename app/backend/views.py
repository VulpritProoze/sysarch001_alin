from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
# from rest_framework.exceptions import ValidationError
from .serializers import RegistrationSerializer, AnnouncementCommentSerializer, SitinSerializer, SitinFeedbackSerializer
from .models import Registration, Announcement, AnnouncementComment, Sitin
from .forms import RegistrationForm
from .choices import COURSE_CHOICES, LEVEL_CHOICES, PROGRAMMING_LANGUAGE_CHOICES, SITIN_PURPOSE_CHOICES, LAB_ROOM_CHOICES
# Pillow Image Compression
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
# Excel File Exporting
from django.http import HttpResponse
from .report_styles import create_excel_report, create_csv_report, create_pdf_report

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
        print(reg.lastname)
        return render(request, 'backend/pages/home.html', context={ 'registration': reg, 'announcements': announcements })
    return redirect('/')

@login_required
def profile(request):
    if request.user.is_authenticated:
        reg = Registration.objects.get(username=request.user)
        return render(request, 'backend/pages/profile.html', context={ 'registration': reg, 'course_choices': COURSE_CHOICES, 'level_choices': LEVEL_CHOICES })
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
        announcementcomment_id = self.kwargs.get('pk')
        user = self.request.user
        return AnnouncementComment.objects.filter(announcement=announcement_id, announcementcomment=announcementcomment_id, user=user)

    def perform_create(self, serializer):
        announcement_id = self.kwargs.get('announcement_id')
        announcement = Announcement.objects.get(id=announcement_id)
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
def reservation(request):
    if request.user.is_authenticated:
        return render(request, 'backend/pages/reservation.html')
    return redirect('/')

class SitinHybridView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'backend/pages/sitin.html'
    
    def get(self, request, *args, **kwargs):
        sitins = Sitin.objects.filter(user=request.user, status="pending").order_by('-date')
        context = {
            'purpose_choices': SITIN_PURPOSE_CHOICES,
            'language_choices': PROGRAMMING_LANGUAGE_CHOICES,
            'room_choices': LAB_ROOM_CHOICES, 
            'sitins': sitins
        }
        if request.accepted_renderer.format == 'html':
            return Response(context, template_name=self.template_name)
        serializer = SitinSerializer(sitins, many=True)
        print(serializer.data)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        request.accepted_renderer = JSONRenderer()
        request.accepted_media_type = "application/json"    # For some reason, this worked
        
        serializer = SitinSerializer(data=request.data)
        if serializer.is_valid():
            # print(serializer.validated_data)
            serializer.save(user=request.user, status="pending")
            return Response({'Sitin': 'Successfully submitted sit-in request'}, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SitinDeleteView(generics.RetrieveDestroyAPIView):
    queryset = Sitin.objects.all()
    serializer_class = SitinSerializer
    permission_classes = [IsAuthenticated]
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'Sitin Request': 'Sitin request deleted successfully.'}, status=status.HTTP_200_OK)
    
@login_required
def sitin_history(request):
    if request.user.is_authenticated:
        sitin_history = Sitin.objects.filter(status='finished', user=request.user, feedback=None)
        return render(request, 'backend/pages/sitin_history.html', {'sitin_history': sitin_history})
    return redirect('/')

class SitinHistoryUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Sitin.objects.all()
    serializer_class = SitinFeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        sitin_id = self.kwargs.get('pk')
        obj = Sitin.objects.filter(id=sitin_id, status='finished')
        print(obj)
        return obj

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        print(request.data)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'Feedback': 'Successfully submitted.'}, status=status.HTTP_200_OK)

@login_required
def sessions(request):
    if request.user.is_authenticated:
        return render(request, 'backend/pages/sessions.html')
    return redirect('/')

# Custom admin views
def approve_sitin(request):
    if request.method == "POST":
        sitin_id = request.POST.get("sitin_id")
        try:
            sitin = Sitin.objects.get(id=sitin_id)
            sitin.status = "approved"
            sitin.sitin_date = timezone.now()
            sitin.save()
            return JsonResponse({"success": True})
        except Sitin.DoesNotExist:
            return JsonResponse({"success": False, "error": "Sitin not found"})
    return JsonResponse({"success": False, "error": "Invalid request method"})

def logout_sitin(request):
    if request.method == "POST":
        sitin_id = request.POST.get("sitin_id")
        try:
            sitin = Sitin.objects.get(id=sitin_id)
            sitin.status = "finished"  # Ensure this field exists in your model
            sitin.logout_date = timezone.now()
            if hasattr(sitin.user, "registration"):
                registration = sitin.user.registration
                if registration.sessions > 0:
                    registration.sessions -= 1
                    registration.save(update_fields=["sessions"])
            sitin.save()
            return JsonResponse({"success": True, "message": "Student logged out successfully."})
        except Sitin.DoesNotExist:
            return JsonResponse({"success": False, "message": "Sit-in record not found."}, status=404)
    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

def export_sitins(request, lab_room, file_type):
    """
    Export all finished sit-ins to an Excel file.
    """
    # Fetch all finished sit-ins
    if request.method == 'GET':
        queryset = Sitin.objects.filter(status="finished", lab_room=lab_room)
        if queryset.exists():
            if lab_room in [choice[0] for choice in LAB_ROOM_CHOICES] or file_type in ['xlsx', 'csv', 'pdf']:
                # Create the Excel report
                title = "Sit-in History Report"
                description = f"This report contains details of all finished sit-ins in Lab room {lab_room}"
                if file_type == 'xlsx':
                    # Create an in-memory response.
                    wb = create_excel_report(queryset, title, description)
                    print('1')
                    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    response["Content-Disposition"] = f'attachment; filename="sit_in_history-{lab_room}.xlsx"'
                    # Save the workbook directly to the response (NO FILESYSTEM SAVE NEEDED)
                    wb.save(response)
                    return response
                elif file_type == 'csv':
                    csv_data = create_csv_report(queryset, title, description)
                    response = HttpResponse(csv_data, content_type="text/csv")
                    response["Content-Disposition"] = f'attachment; filename="sit_in_history-{lab_room}.csv"'
                    return response
                elif file_type == 'pdf':
                    pdf_data = create_pdf_report(queryset, title, description)
                    response = HttpResponse(pdf_data, content_type="application/pdf")
                    response["Content-Disposition"] = f'attachment; filename="sit_in_history-{lab_room}.pdf'
                    return response
                    
            return JsonResponse({"error": "There are no such lab rooms and/or file types"}, status=404)
        return JsonResponse({"error": "Sit-in not found"}, status=404)
    return JsonResponse({"error": "Bad Request"}, status=400)

def error_404_view(request, exception):
    return render(request, 'backend/pages/404.html')