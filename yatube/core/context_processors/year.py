from django.utils import timezone


def year(request):
    this_year = timezone.now().year
    return {
        'year': this_year
    }
