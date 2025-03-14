import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

def create_excel_report(queryset, title, description):
    """
    Create an Excel report with the given queryset, title, and description.
    """
    # Create a new workbook and add a worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Sit-in History"

    # Add title and description
    ws.append([title])
    ws.append([description])
    ws.append([])  # Empty row for spacing

    # Add headers
    headers = [
        "Student ID",
        "Full Name",
        "Purpose",
        "Lab Room",
        "Status",
        "Sessions",
        "Request Date",
        "Time-in",
        "Time-out",
    ]
    ws.append(headers)

    # Add data rows
    for sitin in queryset:
        fullname = sitin.user.registration.firstname + " " + sitin.user.registration.lastname
        student_id = sitin.user.registration.idno

        # Convert timezone-aware datetimes to timezone-naive
        request_date = sitin.date.replace(tzinfo=None) if sitin.date else None
        time_in = sitin.sitin_date.replace(tzinfo=None) if sitin.sitin_date else None
        time_out = sitin.logout_date.replace(tzinfo=None) if sitin.logout_date else None

        ws.append([
            student_id,
            fullname,
            sitin.purpose,
            sitin.lab_room,
            sitin.status,
            sitin.user.registration.sessions if hasattr(sitin.user, "registration") else "",
            request_date,
            time_in,
            time_out,
        ])

    # Apply formatting to the title and description
    title_cell = ws['A1']
    title_cell.font = Font(size=14, bold=True)
    title_cell.alignment = Alignment(horizontal='center')

    description_cell = ws['A2']
    description_cell.font = Font(size=12, italic=True)

    # Merge cells for the title and description
    ws.merge_cells('A1:I1')  # Merge cells for the title
    ws.merge_cells('A2:I2')  # Merge cells for the description

    # Set column widths
    column_widths = {
        'A': 15,  # Student ID
        'B': 25,  # Full Name
        'C': 20,  # Purpose
        'D': 15,  # Lab Room
        'E': 15,  # Status
        'F': 15,  # Sessions
        'G': 20,  # Request Date
        'H': 20,  # Time-in
        'I': 20,  # Time-out
    }

    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    return wb