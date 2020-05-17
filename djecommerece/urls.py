from django.conf import settings
# from django.contrib.staticfiles.templatetags.staticfiles import static as staticfiles
from django.conf.urls.static import static
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin, staticfiles
from django.urls import path, include
from material.admin.sites import site

site.site_header = _('Tiko Administration')
site.site_title = _('Tiko Administration')
# site.favicon = staticfiles('path/to/favicon')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls', namespace='core'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
