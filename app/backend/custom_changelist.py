from django.contrib.admin.views.main import ChangeList
from django.utils.translation import gettext_lazy as _

class CustomChangeList(ChangeList):
    def get_results(self, request):
        # Call the parent method to ensure the queryset is processed
        super().get_results(request)

        # Remove the action checkbox header
        self.result_headers = self._generate_result_headers()

    def _generate_result_headers(self):
        headers = []
        for i, field in enumerate(self.list_display):
            header = {
                'text': self.get_header_text(field),  # Get the display name for the field
                'sortable': self.is_sortable(field),  # Check if the field is sortable
                'url_primary': self.get_sort_url(field, i + 1),  # Generate the sorting URL
                'ascending': self.is_ascending(field),  # Check if the field is sorted ascending
                'class_attrib': self.get_class_attrib(field),  # Add CSS classes
            }
            headers.append(header)
        return headers

    def get_header_text(self, field):
        """
        Get the display name for the field.
        """
        if hasattr(self.model_admin, field):
            # If the field is a method, use its short_description
            method = getattr(self.model_admin, field)
            return getattr(method, 'short_description', field.replace('_', ' ').title())
        else:
            # If the field is a model field, use its verbose_name
            return self.model._meta.get_field(field).verbose_name.title()

    def is_sortable(self, field):
        """
        Check if the field is sortable.
        """
        if hasattr(self.model_admin, field):
            # If the field is a method, check if it has admin_order_field
            method = getattr(self.model_admin, field)
            return hasattr(method, 'admin_order_field')
        else:
            # If the field is a model field, it is sortable
            return True

    def get_sort_url(self, field, order):
        """
        Generate the sorting URL for the field.
        """
        if self.is_sortable(field):
            return f"?o={order}"
        return None

    def is_ascending(self, field):
        """
        Check if the field is sorted in ascending order.
        """
        if self.is_sortable(field):
            # Check if the field is in the current ordering
            ordering_field = self.get_ordering_field(field)
            if ordering_field:
                return not ordering_field.startswith('-')
        return False

    def get_ordering_field(self, field):
        """
        Get the ordering field for the given field.
        """
        if hasattr(self.model_admin, field):
            # If the field is a method, use its admin_order_field
            method = getattr(self.model_admin, field)
            return getattr(method, 'admin_order_field', None)
        else:
            # If the field is a model field, use the field name
            return field

    def get_class_attrib(self, field):
        """
        Get CSS classes for the header.
        """
        classes = []
        if self.is_sortable(field):
            classes.append('sortable')
            if self.is_ascending(field):
                classes.append('ascending')
            else:
                classes.append('descending')
        return ' '.join(classes) if classes else ''