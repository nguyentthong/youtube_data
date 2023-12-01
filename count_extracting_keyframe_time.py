from pytube import YouTube
import os
from video_keyframe_detector.cli import keyframeDetection
import shutil
from tqdm import trange
import numpy as np
import multiprocessing as mp
from collections import defaultdict
import datetime

def main():
    num_frame_list = []
    url_num_frame_dict = {}
    with open("video_url_num_frames_list.txt", 'r') as f: 
        lines = f.readlines()
        for i in trange(len(lines)):
            elements = lines[i].strip().split('\t')
            num_frame_list.append(int(elements[1]))
            url_num_frame_dict[elements[0]] = num_frame_list[-1]

    url_list = list(url_num_frame_dict.keys())
    max_num_frames = max(num_frame_list)
    num_chunks = max_num_frames // 500 + 1

    num_frame_range_url_dict = defaultdict(list)
    for i in trange(len(url_list)):
        num_frames = url_num_frame_dict[url_list[i]]
        chunk_index = num_frames // 500
        num_frame_range_url_dict[chunk_index].append(url_list[i])

    num_processes = 32
    chunk_index_list = sorted(list(num_frame_range_url_dict.keys()))

    with open("frame_time_statistics.txt", 'w') as f:
        total_time = 0
        for index in chunk_index_list:
            time = (index+1) * 10
            num_videos = len(num_frame_range_url_dict[index])
            f.write("Chunk {} - {} seconds/video - {} videos: {} seconds\n".format(index, time, num_videos, time * num_videos // num_processes))
            total_time += time * num_videos // num_processes

        f.write("ETA: {}".format(datetime.timedelta(seconds=total_time)))


if __name__ == '__main__':
    main()