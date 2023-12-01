import multiprocessing as mp
from pytube import YouTube
import os
from tqdm import trange

def count_num_frames(url):
    try:
        print("Counting for video {}".format(url))
        youtube = YouTube(url)
        stream_list = youtube.streams.filter(file_extension='mp4')
        fps = stream_list[0].fps
        length = youtube.length
        with open("video_url_num_frames_list.txt", 'a') as f:
            f.write(url + '\t' + str(fps * length))
            f.write('\n')
            f.flush()
    except:
        pass
    return url


def main():
    with open("to_keep_video_url_with_transcript_list.txt", 'r') as f: to_keep_video_url_with_transcript_list = f.readlines()
    if os.path.exists("video_url_num_frames_list.txt"):
        with open("video_url_num_frames_list.txt", 'r') as f: video_url_num_frames_list = f.readlines()
    else: video_url_num_frames_list = []
    video_url_num_frames_set = set([url.strip().split('\t')[0] for url in video_url_num_frames_list])

    to_proceed_url_list = []
    for i in trange(len(to_keep_video_url_with_transcript_list)):
        if to_keep_video_url_with_transcript_list[i].strip() not in video_url_num_frames_set:
            to_proceed_url_list.append(to_keep_video_url_with_transcript_list[i].strip())

    print("Counting number of frames for {} urls".format(len(to_proceed_url_list)))
    pool = mp.Pool(processes=16)
    outputs = pool.map(count_num_frames, to_proceed_url_list)


if __name__ == '__main__':
    main()