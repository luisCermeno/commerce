# The context processor file describes variables used globally for the 
# whole web application, in this case its used to have the categories list
# available in the layout.html file so that it can be included in the navbar

from .models import *

def get_categories(request):
    return {
        'categories': Category.objects.all()
    }