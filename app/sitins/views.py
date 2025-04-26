from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Sitin
from .serializers import SitinFeedbackSerializer
from .report_styles import create_excel_report, create_csv_report, create_pdf_report
from backend.choices import LAB_ROOM_CHOICES

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
def sitin_history(request):
    if request.user.is_authenticated:
        sitin_history = Sitin.objects.filter(
            status='finished', 
            user=request.user
        ).select_related(
            'user',
            'user__registration'    
        ).order_by('-logout_date')
        # Pagination (uses Paginator)
        paginator = Paginator(sitin_history, 25)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'sitins/sitin_history.html', {'sitin_history': page_obj})
    return redirect('/')

@user_passes_test(lambda u: u.is_superuser)
def export_sitins(request, file_type):
    """
    Export all finished sit-ins to an Excel file.
    """
    # Fetch all finished sit-ins
    if request.method == 'GET':
        lab_room = request.GET.get('lab_room')
        purpose = request.GET.get('purpose')
        level = request.GET.get('level')
        queryset = Sitin.objects.filter(status="finished")
        description = "This report contains details of all finished sit-ins"
        print(lab_room, purpose, level)
        
        if lab_room:
            queryset = queryset.filter(lab_room=lab_room)
            description += f" at Lab room {lab_room}"
        if purpose:
            queryset = queryset.filter(purpose=purpose)
            description += f" for the purpose of {purpose.lower()}"
        if level:
            queryset = queryset.filter(user__registration__level=level)
            description += f" of students at year level {level}"
        description += ". Generated on " + datetime.now().strftime("%b %d, %Y, %I:%M %p")
        
        if queryset.exists():
            if lab_room in [choice[0] for choice in LAB_ROOM_CHOICES] or file_type in ['xlsx', 'csv', 'pdf']:
                # Create the Excel report
                title = "Sit-in History Report"
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