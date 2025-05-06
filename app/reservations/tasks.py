from datetime import datetime, timedelta
import time
import threading
from django.shortcuts import get_object_or_404
from notifications.notifications import send_notification
from .models import SitinRequest


def send_reservation_reminder(reservation_id):
    try:
        reservation = get_object_or_404(
            SitinRequest.objects.select_related(
                    'sitin',
                    'lab_room',
                    'pc'
                ), 
            id=reservation_id)
        
        if not hasattr(reservation, 'sitin'):
            raise AttributeError("Sitinrequest no related 'sitin'")
        
        user = reservation.sitin.user 
        
        if not hasattr(reservation, 'lab_room') or not hasattr(reservation, 'pc'):
            raise AttributeError("Sitinrequest not related lab_room or pc")
        
        message = f"In 30 minutes, your reservation (ID/{reservation.id}) for Lab{reservation.lab_room.room_number}, PC{reservation.pc.pc_number} will soon be coming up."
        url = f"/reservations/#sitin-request-id-{reservation.id}"
        badge_type = 'sitin'
        
        send_notification(user, message, url, badge_type)
    except Exception as e:
        # Handle any exceptions that might occur during the reminder sending
        print(f"Failed to send reminder for reservation {reservation_id}: {str(e)}")

# Send a notif to user that their reservation will be 30 minutes later
def send_reservation_reminder(reservation_id):
    try:
        print(f"[DEBUG] Attempting to send reminder for reservation {reservation_id}")

        reservation = get_object_or_404(
            SitinRequest.objects.select_related('sitin', 'lab_room', 'pc'),
            id=reservation_id
        )

        if not hasattr(reservation, 'sitin'):
            raise AttributeError("SitinRequest has no related 'sitin'")

        user = reservation.sitin.user

        if not hasattr(reservation, 'lab_room') or not hasattr(reservation, 'pc'):
            raise AttributeError("SitinRequest not related to lab_room or pc")

        message = (
            f"In 30 minutes, your reservation (ID/{reservation.id}) for "
            f"Lab{reservation.lab_room.room_number}, PC{reservation.pc.pc_number} "
            "will soon be coming up."
        )
        url = f"/reservations/#sitinrequest-id-{reservation.id}"
        badge_type = 'sitin'

        print(f"[DEBUG] About to send notification to user {user.id}")
        send_notification(user, message, url, badge_type)
        print(f"[DEBUG] Notification sent successfully for reservation {reservation.id}")

    except Exception as e:
        print(f"[ERROR] Failed to send reminder for reservation {reservation_id}: {str(e)}")

def schedule_reservation_reminder(reservation_id):
    try:
        # Fetch the reservation
        reservation = get_object_or_404(
            SitinRequest.objects.select_related('sitin'),
            id=reservation_id
        )

        if not hasattr(reservation, 'sitin'):
            raise AttributeError("SitinRequest has no related 'sitin'")

        sitin_date = reservation.sitin.sitin_date  # Changed from request_date to sitin_date
        if not sitin_date:
            raise ValueError("No sitin_date found for this reservation")

        now = datetime.now(sitin_date.tzinfo)
        thirty_min_before = sitin_date - timedelta(minutes=30)
        
        print(f"[TIME DEBUG] Now: {now}")
        print(f"[TIME DEBUG] Sitin Date: {sitin_date}")  # Updated label
        print(f"[TIME DEBUG] 30-min Before: {thirty_min_before}")

        # Case 1: Current time is after sitin date (completely missed)
        if now >= sitin_date:
            print(f"[SKIPPED] Reservation {reservation_id} has already passed")
            return

        # Case 2: Current time is within 30-minute window
        if now >= thirty_min_before:
            print(f"[IMMEDIATE] Reservation {reservation_id} is within 30 minutes - notifying now")
            send_reservation_reminder(reservation_id)
            return

        # Case 3: Future reservation (more than 30 minutes away)
        delay_seconds = (thirty_min_before - now).total_seconds()
        print(f"[SCHEDULED] Will remind for reservation {reservation_id} in {delay_seconds:.0f} seconds")

        def reminder_wrapper():
            print(f"[TIMER STARTED] Waiting {delay_seconds:.0f}s for reservation {reservation_id}")
            time.sleep(delay_seconds)
            print(f"[TIMER COMPLETE] Sending reminder for {reservation_id}")
            send_reservation_reminder(reservation_id)

        thread = threading.Thread(target=reminder_wrapper)
        thread.daemon = True
        thread.start()

    except Exception as e:
        print(f"[ERROR] Failed to schedule reminder for reservation {reservation_id}: {str(e)}")