from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls.conf import include

from klozit import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('boards/', include('boards.urls')),
    path('products/', include('products.urls')),
]

urlpatterns = urlpatterns + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
