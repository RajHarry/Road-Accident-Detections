import os
from fe_c3d.c3d import c3d_feature_extractor,preprocess_input
from fe_c3d.classifier import build_classifier_model
from fe_c3d.utils.visualization_util import get_video_clips,visualize_predictions
import fe_c3d.parameters as params
import fe_c3d.configuration as cfg
from fe_c3d.plot_controller import savitzky_golay
from fe_c3d.utils.array_util import interpolate,extrapolate
from keras import backend as K 
import keras
import numpy as np

def extract_feature_video(video_path, features_per_bag = params.features_per_bag):
    if keras.backend.backend() == 'tensorflow':
        K.clear_session()

    # read video
    video_clips, num_frames = get_video_clips(video_path)

    print("Number of clips in the video : ", len(video_clips))

    # build models
    feature_extractor = c3d_feature_extractor()
    classifier_model = build_classifier_model()

    print("Models initialized")

    # extract features
    rgb_features = []
    for i, clip in enumerate(video_clips):
        clip = np.array(clip)
        if len(clip) < params.frame_count:
            continue

        clip = preprocess_input(clip)
        rgb_feature = feature_extractor.predict(clip)[0]
        rgb_features.append(rgb_feature)

        print("Processed clip : ", i)
        # break
    rgb_features = np.array(rgb_features)
    
    # bag features
    rgb_feature_bag = interpolate(rgb_features, features_per_bag)

    # classify using the trained classifier model
    predictions = classifier_model.predict(rgb_feature_bag)
    # assert(False)
    predictions = np.array(predictions).squeeze()
    predictions = extrapolate(predictions, num_frames)

    predictions = savitzky_golay(predictions, 101, 3)
    video_name = video_path.split("/")[-1].split(".")[0]
    # print("video_name(before_save): ",video_name)
    # np.save('media/features/{}'.format(video_name), predictions)

    visualize_predictions(video_path, predictions)
    return predictions

def load_npy(file_path):
    return np.load(file_path)
