from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
from django.views import View
from django.conf import settings
from django.core import files
from django.utils.text import slugify
import time
# A view function, or view for short, 
# is simply a Python function that takes a Web request and returns a Web response. 
# This response can be the HTML contents of a Web page, or a redirect, or a 404 error,
# or an XML document, or an image . . . or anything, really.
from django.views import generic
from .models import Video
from .forms import VideoForm
from .tasks import extract_feature, my_task

import os
import json
import glob
import urllib.request
import tempfile
from pytube import YouTube

from fe_c3d.extract_feature import load_npy, extract_feature_video
from fe_c3d.configuration import weight_default_path, weight32_path, weight64_path
from catalog.utils.utils import load_annotation, format_filesize, url_downloadable, write_file, get_basename

def index(request):
    """View function for home page of site."""

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1

    # Render the HTML template index.html with the data in the context variable.
    print(request.path)
    
    return render(
        request,
        'index.html',
        context={
            'num_visits': num_visits,
            }
    )

class VideoListView(generic.TemplateView):
    template_name = 'catalog/video_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        action = context['video_action']
        print("action: ",action)
        folder_name = context['folder_name']
        # print("folder_name: ",folder_name)
        # print("path: ","/media/output/"+folder_name+"/"+action+"/*.png")
        gifs = sorted(glob.glob("media/output/"+folder_name+"/"+action+"/*.png"))
        # gifs = sorted(glob.glob('media/gifs/{}/*.gif'.format(action)))
        # print("gifs: ",gifs)
        for i, value in enumerate(gifs):
            value = "/"+value
            title = value.split("/")[-1].split(".")[0]#os.path.basename(value)[:-4]
            # print("path: {},\ntitle: {}".format(value,title))
            video = {'url': '/catalog/video/{}/{}/'.format(folder_name,action) + title,'basename': title, 'title': title,'src':value,"action":action}
            gifs[i] = video

        # update context
        context['gifs'] = gifs
        context['action'] = action
        return context
        
class VideoDetailView(generic.TemplateView):
    template_name = 'catalog/video_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder_name = context['folder_name']
        action = context['video_type']
        title = context['video_title'] # title from URL

        video_path = '/media/output/{}/{}/{}.mp4'.format(folder_name,action, title)
        context['video'] = {'url': '/media/output/{}/{}/{}.mp4'.format(folder_name,action, title), 'title': title, 'video_path': video_path}
        context["vid_det"] = {'video_id':title,"action":action,'location':"Hyderabad","incident_time":"time"}
        return context        

class VideoUploadView(View):
    def get(self, request):
        # Order by descent of uploaded time
        videos_list = Video.objects.order_by('-uploaded_at')
        print(">>>>>>>>>>>>>>>>> In Get <<<<<<<<<<<<<<")
        print("videos_list: ",videos_list)
        return render(self.request, 'catalog/video_upload.html', {'videos': videos_list})

    def post(self, request):
        """
        Post from form blue-upload or url.
        """
        #time.sleep(1)  # You don't need this line. This is just to delay the process so you can see the progress bar testing locally.
        url = request.POST.get('url')
        filename = request.POST.get('filename')

        response = {'is_valid': False}

        form = VideoForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            print(">>> In form")
            video = form.save()
            video.filesize = format_filesize(video.file.size)
            video.title = get_basename(video.file.name)
            video.row_id = video.__class__.objects.count()
            video.save()

            print(f"row_id:{video.row_id}, name: {video.file.name}, url: {video.file.url}, filesize: {video.filesize},title: {video.title}, status: {video.status}")
            # response = {'is_valid': True, 'name': video.file.name, 'url': video.file.url, 'id': video.id, 'filesize': video.filesize, 'title': video.title}
            response = {'is_valid': True, 'row_id':video.row_id,'name': video.file.name, 'url': video.file.url, 'filesize': video.filesize, 'title': video.title,'status':video.status}
        elif url:
            print("In URL")
            url_response = urllib.request.urlopen(url)
            url_info = url_response.info()
            
            if 'video' in url_info.get_content_type():
                print("In Video")
                temp_video = tempfile.NamedTemporaryFile()
                write_file(temp_video, url_response)

                video = Video()
                objects_count = video.objects.count()
                print("Video Table Objects Count: ",objects_count)
                video.file.save(filename, files.File(temp_video))
                video.filesize = format_filesize(video.file.size)
                video.title = get_basename(video.file.name)
                video.save()
                response = {'is_valid': True, 'name': video.file.name, 'url': video.file.url, 'filesize': video.filesize, 'title': video.title,'status':video.status}

        # Extract Feature in Celery
        if response['is_valid'] == True:
            # video = Video()
            # print(video.id)
            # video_id = video.row_id+1
            task = extract_feature(response["row_id"])
            # assert(False)
            video.status = "registered"
            # video.task_id = task.task_id
            video.save()
            # response['task_id'] = task.task_id

        return JsonResponse(response)

class DeleteVideoView(View):
    def post(self, request):
        response = {'success': False}
        print(request.POST)
        if request.POST.get('delete_all'):
            videos = Video.objects.all()
            for video in videos:
                video.file.delete()
                video.file_score32.delete()
                video.file_score64.delete()
                video.delete()
            videos.delete()
            response = {'success': True}
        else:
            # file_names = request.POST.getlist('files[]')
            ids = request.POST.getlist('ids[]')
            for id in ids:
                video = Video.objects.get(id = id)
                video.file.delete()
                video.file_score32.delete()
                video.file_score64.delete()
                video.delete()
            response = {'success': True}
            
        return JsonResponse(response)

from celery.result import AsyncResult
from .tasks import add 
def progress_view(request):
    result = my_task.delay(100)
    return render(request, 'catalog/progress.html', context={'task_id': result.task_id})