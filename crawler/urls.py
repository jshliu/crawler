import os

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.static import serve


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^vendor/(?P<path>.*)$', serve, {'document_root': os.path.join(settings.BASE_DIR, 'vendor')}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
