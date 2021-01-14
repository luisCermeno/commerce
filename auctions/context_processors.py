from .models import *

def get_categories(request):
    return {
        'categories': Category.objects.all()
    }