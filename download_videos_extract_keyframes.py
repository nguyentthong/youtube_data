from pytube import YouTube
import os
from video_keyframe_detector.cli import keyframeDetection
import shutil
from tqdm import trange
import numpy as np
import multiprocessing as mp
from collections import defaultdict

downloaded_video_set = set()
if os.path.exists("downloaded_videos"):
    downloaded_video_set = set(os.listdir("downloaded_videos"))


def download_video(url):
    try:
        filename = os.path.join("downloaded_videos", url.split('=')[-1] + '.mp4')
        if url.split('=')[-1] + '.mp4' in downloaded_video_set: return url    

        print("Downloading video {}...".format(url))
        video = YouTube(url)
        video.streams.filter(file_extension='mp4')
        video.streams.get_by_itag(18).download(filename=filename)
        return url
    except:
        return url


def extract_keyframes(url):
    try:
        video_id = url.split('=')[-1]
        n = 12
        print("Extracting keyframes for video {}".format(video_id))
        source_file = os.path.join("downloaded_videos", video_id + ".mp4")
        temp_folder = os.path.join("temp", video_id)
        os.makedirs(temp_folder, exist_ok=True)
        keyframeDetection(source_file, temp_folder, 0.6)

        video_frame_list = sorted(os.listdir(os.path.join("temp", video_id)), key=lambda x: int(x.split('.')[0].split('_')[1]))
        if len(video_frame_list) < n:
            shutil.rmtree(os.path.join("temp", video_id))
            return video_id

        os.makedirs(os.path.join("video_frames", video_id), exist_ok=True)
        selected_frame_idx_set = set(np.linspace(1, len(video_frame_list)-1, n).astype(int))
        cnt = 0
        for i in range(len(video_frame_list)):
            if i in selected_frame_idx_set:
                source_file = os.path.join("temp", video_id, video_frame_list[i])
                target_file = os.path.join("video_frames", video_id, "frame_{}.jpg".format(cnt))
                shutil.copyfile(source_file, target_file)
                cnt += 1
    except:
        pass

    shutil.rmtree(os.path.join("temp", video_id))
    filename = os.path.join("downloaded_videos", video_id + '.mp4')
    os.remove(filename)


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

    os.makedirs("downloaded_videos", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    video_frame_list = []
    if os.path.exists("video_frames"):
        video_frame_list = os.listdir("video_frames")
    processed_video_set = set([file.split('.')[0] for file in video_frame_list])

    num_frame_range_url_dict = defaultdict(list)
    for i in trange(len(url_list)):
        if url_list[i].split('=')[-1] in processed_video_set: continue
        num_frames = url_num_frame_dict[url_list[i]]
        chunk_index = num_frames // 500
        num_frame_range_url_dict[chunk_index].append(url_list[i])

    chunk_index_list = sorted(list(num_frame_range_url_dict.keys()))

    for i in trange(len(chunk_index_list)):
        current_to_process_url_list = num_frame_range_url_dict[i]
        download_pool = mp.Pool(processes=32)
        outputs = download_pool.map(download_video, current_to_process_url_list)
        extract_pool = mp.Pool(processes=32)
        outputs = extract_pool.map(extract_keyframes, current_to_process_url_list)

        shutil.rmtree("downloaded_videos")
        os.makedirs("downloaded_videos")


if __name__ == '__main__':
    main()