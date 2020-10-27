from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'catalog'
urlpatterns = [
    path('', views.VideoUploadView.as_view(), name='index'),
    path('videos/<str:folder_name>/<str:video_action>', views.VideoListView.as_view(), name='videos'),
    # parameter at video detail <str:video_title>, it WORKS EVEN for invalid video string title
    # video_title parameter can be invoked in corresponding VIEW later then 
    path('video/<str:folder_name>/<str:video_type>/<str:video_title>', views.VideoDetailView.as_view(), name='video-detail'),
    path('video-upload', views.VideoUploadView.as_view(), name='video-upload'),
    path('delete-videos', views.DeleteVideoView.as_view(), name='delete-videos'),
    path('progress', views.progress_view, name='progress'),
]