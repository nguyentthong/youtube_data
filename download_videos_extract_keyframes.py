from pytube import YouTube
import os
from video_keyframe_detector.cli import keyframeDetection
import shutil
from tqdm import trange
import numpy as np
import multiprocessing as mp
from collections import defaultdict

downloaded_video_set = set()
if os.path.exists("checked_to_download_video_list.txt"):
    with open("checked_to_download_video_list.txt", 'r') as f: checked_to_download_video_list = f.readlines()
    downloaded_video_set = set([checked_to_download_video.strip() for checked_to_download_video in checked_to_download_video_list])


if os.path.exists("downloaded_videos"):
    downloaded_video_list = os.listdir("downloaded_videos")
    with open("checked_to_download_video_list.txt", 'a') as f:
        for video in downloaded_video_list:
            if video not in downloaded_video_set:
                f.write(video + '\n')
                downloaded_video_set.add(video)

checked_to_extract_keyframe_video_list = []
if os.path.exists("checked_to_extract_keyframe_video_list.txt"):
    with open("checked_to_extract_keyframe_video_list.txt", 'r') as f: checked_to_extract_keyframe_video_list = f.readlines()
processed_video_set = set([video.strip() for video in checked_to_extract_keyframe_video_list])


if os.path.exists("video_frames"):
    video_frames = os.listdir("video_frames")
    with open("checked_to_extract_keyframe_video_list.txt", 'a') as f:
        for video in video_frames:
            if video + ".mp4" not in processed_video_set:
                f.write(video + ".mp4" + '\n')
                processed_video_set.add(video + ".mp4")


def download_video(url):
    try:
        filename = os.path.join("downloaded_videos", url.split('=')[-1] + '.mp4')
        if url.split('=')[-1] + '.mp4' in downloaded_video_set: return url    

        print("Downloading video {}...".format(url))
        video = YouTube(url)
        video.streams.filter(file_extension='mp4')
        video.streams.get_by_itag(18).download(filename=filename)
        with open("checked_to_download_video_list.txt", 'a') as f:
            f.write(url.split('=')[-1] + '.mp4')
            f.write("\n")
            f.flush()
        return url
    except:
        with open("checked_to_download_video_list.txt", 'a') as f:
            f.write(url.split('=')[-1] + '.mp4')
            f.write("\n")
            f.flush()
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
            pass
        else:
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
    with open("checked_to_extract_keyframe_video_list.txt", 'a') as f: 
        f.write(video_id + ".mp4\n")
        f.flush()


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
    os.makedirs("video_frames", exist_ok=True)

    num_frame_range_url_dict = defaultdict(list)
    for i in trange(len(url_list)):
        if url_list[i].split('=')[-1] + ".mp4" in processed_video_set:
            video_id = url_list[i].split('=')[-1]
            shutil.rmtree(os.path.join("temp", video_id), ignore_errors=True)
            filename = os.path.join("downloaded_videos", video_id + '.mp4')
            try:
                os.remove(filename)
            except:
                pass
            continue
        num_frames = url_num_frame_dict[url_list[i]]
        chunk_index = num_frames // 500
        num_frame_range_url_dict[chunk_index].append(url_list[i])

    chunk_index_list = sorted(list(num_frame_range_url_dict.keys()))
    for i in trange(len(chunk_index_list)):
        chunk_index = chunk_index_list[i]
        current_to_process_url_list = num_frame_range_url_dict[chunk_index]

        to_download_video_list = []
        for url in current_to_process_url_list:
            if url.split('=')[1] + '.mp4' not in downloaded_video_set: to_download_video_list.append(url)

        print("Chunk {}: To download {} videos".format(i, len(to_download_video_list)))
        download_pool = mp.Pool(processes=32)
        outputs = download_pool.map(download_video, to_download_video_list)
        extract_pool = mp.Pool(processes=32)
        outputs = extract_pool.map(extract_keyframes, current_to_process_url_list)

        shutil.rmtree("downloaded_videos")
        os.makedirs("downloaded_videos")


if __name__ == '__main__':
    main()
