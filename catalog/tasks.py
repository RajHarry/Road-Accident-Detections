# Create your tasks here
from __future__ import absolute_import, unicode_literals
from django.conf import settings

import numpy as np
from .models import Video
from fe_c3d.extract_feature import load_npy, extract_feature_video
from catalog.utils.utils import get_basename
import time
from fe_c3d.configuration import *

def add(x, y):
    return x + y

def mul(x, y):
    return x * y

def xsum(numbers):
    return sum(numbers)

def extract_feature(video_id):
    print("passed row id: ",video_id)
    try:
        video = Video.objects.get(row_id = int(video_id))
    except:
        video = None
    video.status = "Processing..."
    video.save()
    video_path =  settings.MEDIA_ROOT + video.file.name
    score32 = extract_feature_video(video_path, 32)
    file_score32 = 'media/features/' + get_basename(video.file.name) + '_32.npy'
    np.save(file_score32, score32)
    video.file_score32.name = file_score32[6:]
    video.status = "Completed"
    video.save()
    return 'done'

def my_task(self, seconds):
    for i in range(seconds):
        time.sleep(1)
    return 'done'