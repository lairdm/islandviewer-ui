from django.conf.urls import patterns, include, url
import settings.env

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

if settings.env.DEV_ENV:
    urlpatterns = patterns('',
        url(r'^islandviewer/', include('webui.urls'))
      
    # Examples:
    # url(r'^$', 'Islandviewer.views.home', name='home'),
    # url(r'^Islandviewer/', include('Islandviewer.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    )
else:
    urlpatterns = patterns('',
        url(r'^', include('webui.urls'))
    )
    
