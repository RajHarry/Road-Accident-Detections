import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from fe_c3d.utils.video_util import *
from fe_c3d.utils.video_util import get_video_frames
import numpy as np
from PIL import Image
import cv2,os

def image_to_video(img_array,directory,out_path,start,end):
    print("from: {},to: {}".format(start,end))
    height,width,layers=img_array[1].shape
    out_temp_path,out_path = out_path+"_temp.mp4",out_path+".mp4"
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video=cv2.VideoWriter(out_temp_path,0x7634706d,30,(width,height))
    
    cv2.imwrite(directory+f"/{start}-{end}.png",img_array[start])
    for j in range(start,end):
        img = cv2.cvtColor(img_array[j], cv2.COLOR_RGB2BGR)
        video.write(img)

    cv2.destroyAllWindows()
    video.release()
    print("done with temp_video writing")
    os.system(f"ffmpeg -i {out_temp_path} -vcodec libx264 {out_path}")
    print("done with orig_video writing")
    os.remove(out_temp_path)

def visualize_predictions(video_path, predictions):
    video_name = video_path.split("/")[-1].split(".")[0]
    frames = get_video_frames(video_path)
    # print("entered!")
    assert len(frames) == len(predictions)

    exit_val,count = 0,0
    for i in range(10,len(frames),10):
        # frame = frames[i]
        isAnomaly = sum(predictions[i-10:i])>=0.2
        if(isAnomaly==True):
            count+=1
            if(count == 3):
                if((i-100) >= 0):
                    start = i-100
                elif((i-80) >= 0):
                    start = i-80
                elif((i-50) >= 0):
                    start = i-50
                else:
                    start = i-30
            exit_val=0
        elif(count>3):
            exit_val+=1
            if(exit_val==3):
                end = i
                count,exit_val=0,0
                directory = "media/output/"+video_name+"/"
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    os.makedirs(directory+"abnormal/")
                    os.makedirs(directory+"normal/")
                out_path = "media/output/"+video_name+f"/abnormal/{start}-{end}"
                image_to_video(frames,directory+"abnormal",out_path,start,end)
    
    return