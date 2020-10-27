
from keras.regularizers import l2
import numpy as np
import numpy.matlib
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.regularizers import l2
import os, sys
from os import listdir
from keras import backend as K # to clear session each time reloading

import cv2

from fe_c3d.classifier import conv_dict, load_weights
from fe_c3d.configuration import weight_default_path, feature32_alias, no_segment, feature64_alias, feature32_alias # all config variables (weight, segment, other options, ...)

import scipy.io
from math import factorial
from scipy.io import loadmat, savemat

seed = 7
np.random.seed(seed)


def classifier_model():
    model = Sequential()
    model.add(Dense(512, input_dim=4096, kernel_initializer='glorot_normal', kernel_regularizer=l2(0.001), activation='relu'))
    model.add(Dropout(0.6))
    model.add(Dense(32, kernel_initializer='glorot_normal', kernel_regularizer=l2(0.001)))
    model.add(Dropout(0.6))
    model.add(Dense(1, kernel_initializer='glorot_normal', kernel_regularizer=l2(0.001), activation='sigmoid'))
    return model

def load_model():
    model = classifier_model()
    return model

def load_one_video_features(Test_Video_Path):
    
    VideoPath =Test_Video_Path
    f = open(VideoPath, "r")
    words = f.read().split()
    num_feat = len(words) / 4096
    # Number of features per video to be loaded. In our case num_feat=32, as we divide the video into 32 segments. Npte that
    # we have already computed C3D features for the whole video and divide the video features into 32 segments.

    count = -1
    VideoFeatues = []
    for feat in range(0, int(num_feat)):
        feat_row1 = np.float32(words[feat * 4096:feat * 4096 + 4096])
        count = count + 1
        if count == 0:
            VideoFeatues = feat_row1
        if count > 0:
            VideoFeatues = np.vstack((VideoFeatues, feat_row1))
    AllFeatures = VideoFeatues

    return  AllFeatures

def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    """
    Savitzky Golay filter for smoothing the score
    """
    window_size = np.abs(np.int(window_size))
    order = np.abs(np.int(order))
    #except ValueError, msg:
    #    raise ValueError("window_size and order have to be of type int")

    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")

    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")

    order_range = range(order + 1)

    half_window = (window_size - 1) // 2
    b = np.mat([[k ** i for i in order_range] for k in range(-half_window, half_window + 1)])
    m = np.linalg.pinv(b).A[deriv] * rate ** deriv * factorial(deriv)
    firstvals = y[0] - np.abs(y[1:half_window + 1][::-1] - y[0])
    lastvals = y[-1] + np.abs(y[-half_window - 1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve(m[::-1], y, mode='valid')
