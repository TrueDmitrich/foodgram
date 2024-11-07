from django.contrib import admin
from django.urls import path, include

from recipes.views import redirect_short_link

urlpatterns = [
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('s/<int:id>', redirect_short_link),
]
