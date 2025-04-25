from django.shortcuts import render, redirect
from .models import LabRoom
from django.contrib.auth.decorators import login_required

@login_required
def reservation(request):
    if request.user.is_authenticated:
        labrooms = LabRoom.objects.prefetch_related('computer_set').all()
        return render(request, 'reservations/pages/reservation.html', context={ 'labrooms': labrooms })
    return redirect('/')