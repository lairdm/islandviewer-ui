from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from webui import views

urlpatterns = patterns('',
#    url(r'^$', views.index, name='index'),
    url(r'^demo/$', RedirectView.as_view(url="../accession/NC_004631.1/?&load=%%257B%%2522m%%2522%%253A%%257B%%2522s%%2522%%253A4493092.18200115%%252C%%2522e%%2522%%253A4526150.469091758%%252C%%2522id%%2522%%253A%%25222210%%2522%%252C%%2522c%%2522%%253A500%%252C%%2522x%%2522%%253A%%2522auto%%2522%%252C%%2522y%%2522%%253A%%2522auto%%2522%%252C%%2522l%%2522%%253A600%%257D%%252C%%2522un%%2522%%253A%%255B%%255D%%252C%%2522d%%2522%%253A%%257B%%2522v%%2522%%253Atrue%%252C%%2522t%%2522%%253A152.046875%%252C%%2522l%%2522%%253A836.234375%%257D%%257D?&load=%%257B%%2522m%%2522%%253A%%257B%%2522s%%2522%%253A4493298.565905276%%252C%%2522e%%2522%%253A4513493%%252C%%2522id%%2522%%253A%%25222210%%2522%%252C%%2522c%%2522%%253A500%%252C%%2522x%%2522%%253A%%2522auto%%2522%%252C%%2522y%%2522%%253A%%2522auto%%2522%%252C%%2522l%%2522%%253A600%%257D%%252C%%2522un%%2522%%253A%%255B%%255D%%252C%%2522d%%2522%%253A%%257B%%2522v%%2522%%253Atrue%%252C%%2522t%%2522%%253A185.09375%%252C%%2522l%%2522%%253A840.3125%%257D%%257D", permanent=False), name='demo'),
    url(r'^$', views.showgenomes, name='browse'),
#    url(r'^$', RedirectView.as_view(url='/islandviewer/query.php', permanent=False)),
    url(r'^results/(?P<aid>\d+)/$', views.results, name='results'),
    url(r'^accession/(?P<accnum>\w+)/$', views.resultsbyrootaccnum, name='resultsbyrootaccnum'),
    url(r'^accession/(?P<accnum>\w+\.\d+)/$', views.resultsbyaccnum, name='resultsbyaccnum'),
    url(r'^name/(?P<name>\w+)/$', views.resultsbyname, name='resultsbyname'),
    url(r'^islandpick/select/(?P<aid>\d+)/$', views.islandpick_select_genomes, name='islandpickselectgenomes'),
    url(r'^browse/$', views.showgenomes, name='browse'),
    url(r'^browse/json/$', views.showgenomesjson, name='browsejson'),
    url(r'^genomes/json/$', views.fetchgenomesjson, name='fetchgenomesjson'),
    url(r'^about/$', views.about, name='about'),
    url(r'^download/$', views.download, name='download'),
    url(r'^download/coordinates/$', views.downloadCoordinates, name='downloadcoordinates'),
    url(r'^download/annotations/$', views.downloadAnnotations, name='downloadannotations'),
    url(r'^download/sequences/$', views.downloadSequences, name='downloadsequences'),
    url(r'^resources/$', views.resources, name='resources'),
    url(r'^contactus/$', views.contactus, name='contactus'),
    url(r'^faq/$', views.faq, name='faq'),
    url(r'^getMauve/$', views.getMauveFile,name='mauve'),
    url(r'^islandpick/$', views.islandpick, name='islandpick'),
    url(r'acknowledgements', views.acknowledgements, name='acknowledgements'),
    url(r'^plot/(?P<aid>\d+)/$', views.circularplotjs, name='circularplotjs'),
    url(r'^json/gis/(?P<aid>\d+)/$', views.tablejson, name="tablejson"),
    url(r'^islands/$', views.fetchislands, name="fetchislands"),
    url(r'^islands/fasta/$', views.fetchislandsfasta, name="fetchislandsfasta"),
    url(r'^json/genes/(?P<gi_id>\d+)/$', views.genesjson, name="genesjson"),
    url(r'^json/genes/$', views.genesbybpjson, name="genesbybpjson"),
    url(r'^json/genes/search/(?P<ext_id>[\w\.]+)/$', views.search_genes, name="searchgenes"),
    url(r'^json/islandpick/(?P<aid>\d+)/$', views.islandpick_genomes, name="islandpick_genomes"),
    url(r'^notify/(?P<aid>\d+)/$', views.add_notify, name="add_notify"),
    url(r'^upload/$', views.uploadform, name="uploadform"),
    url(r'^ajax/upload/$', views.uploadcustomajax, name="uploadcustomajax"),
    url(r'^status/$', views.runstatus, name='runstatus'),
    url(r'^status/json/$', views.runstatusjson, name='runstatusjson'),
    url(r'^status/details/json/(?P<aid>\d+)/$', views.runstatusdetailsjson, name='runstatusdetailsjson'),
    url(r'^module/restart/(?P<aid>\d+)/$', views.restartmodule, name='restartmodule'),
    url(r'^module/logs/(?P<aid>\d+)/$', views.logsmodule, name='logsmodule'),
    url(r'^results/graph/(?P<aid>\d+)/$', views.graphanalysis, name='graphanalysis'),
    url(r'^results/graph/js/(?P<aid>\d+)/$', views.graphanalysisjs, name='graphanalysisjs'),
    url(r'^upload/(?P<upload_id>\d+)/$', views.uploadredirect, name='uploadredirect'),
)
