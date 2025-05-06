from django.forms import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from backend.choices import SITIN_PURPOSE_CHOICES, PROGRAMMING_LANGUAGE_CHOICES
from .models import LabRoom, SitinRequest, Computer
from .serializers import SitinRequestSerializer, SitinSerializer

@login_required
def reservation(request):
    if request.user.is_authenticated:
        labrooms = LabRoom.objects.prefetch_related('computer_set').all()
        sitinrequests = SitinRequest.objects.select_related(
            'sitin',
            'pc',
            'lab_room'
        ).filter(sitin__user=request.user)
        user_has_approved_sitin = request.user.sitin_set.filter(status='approved').exists()
        return render(
            request, 
            'reservations/pages/reservation.html', 
            context={ 
                'labrooms': labrooms, 
                'sitinrequests': sitinrequests, 
                'user_has_approved_sitin': user_has_approved_sitin,
                'SITIN_PURPOSE_CHOICES': SITIN_PURPOSE_CHOICES, 
                'PROGRAMMING_LANGUAGE_CHOICES': PROGRAMMING_LANGUAGE_CHOICES })
    return redirect('/')

class SitinRequestCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SitinRequest.objects.all()
    serializer_class = SitinRequestSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        '''
        What I learned:
        1. Using form submissions, I cannot send a response back to client like how I've been 
        using with ajax request. If I use form (such as the case with this view), I cannot return
        a response that I can use to feed to my custom alert and display an alert on reload.
        2. Using ajax, I could. I don't really understand why. I could rerender the reservation view 
        above and at the same time receive the Response returned from this view.
        '''
        # return Response({'Sitin Request': 'Successfully submitted!'}, status=status.HTTP_200_OK)
        if request.accepted_media_type == 'text/html' or 'text/html' in request.headers.get('Accept', ''):
            # For form submissions - redirect back to reservation page
            return redirect('/reservations' + '?success=true')
    
    def perform_create(self, serializer):
        data = self.request.data
        print('sitin date', data.get('sitin_date'))
        print('data', data)
        sitin_data = {
            'programming_language': data.get('programming_language'),
            'purpose': data.get('purpose'),
            'lab_room': data.get('lab-room'),
            'sitin_details': data.get('sitin_details'),
            'request_date': timezone.now(),
            'sitin_date': data.get('sitin_date'),
            'user': self.request.user.id,
        }
        print('labroom', data.get('lab-room'))
        print('lab_id', data.get('room'))
        
        sitin_serializer = SitinSerializer(data=sitin_data)
        sitin_serializer.is_valid(raise_exception=True)
        sitin = sitin_serializer.save()
        
        try:
            serializer.save(
                sitin=sitin,
                lab_room=LabRoom.objects.get(id=int(data.get('room'))),
                pc=Computer.objects.get(id=int(data.get('pc')))
            )
        except ObjectDoesNotExist as e:
            error_detail = {}
            if not LabRoom.objects.filter(id=int(data.get('room'))).exists():
                error_detail['lab_room'] = f"LabRoom with id {data.get('room')} does not exist"
            if not Computer.objects.filter(id=int(data.get('pc'))).exists():
                error_detail['pc'] = f"Computer with id {data.get('pc')} does not exist"
            raise ValidationError(error_detail)
        except ValueError as e:
            raise ValidationError({
                'error': 'Invalid ID format',
                'details': str(e)
            })
        except Exception as e:
            raise ValidationError({
                'error': 'Failed to create SitinRequest',
                'details': str(e)
            })