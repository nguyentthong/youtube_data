from youtube_transcript_api import YouTubeTranscriptApi
from multiprocessing import pool
import time
import multiprocessing as mp
import os
from tqdm import trange
from pytube import YouTube
import argparse

def check_audio(url):
    print("Checking video {}...".format(url.strip()))

    youtube = YouTube(url.strip())
    try:
        if youtube.views < 10000 or youtube.length < 600:
            with open("to_remove_video_url_with_transcript_list.txt", 'a') as f: f.write(url)
            return url
    except:
        with open("to_remove_video_url_with_transcript_list.txt", 'a') as f: f.write(url)
        return url
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(url.split("=")[1])
        transcript_list = list(transcript_list._manually_created_transcripts.values()) + list(transcript_list._generated_transcripts.values())
        if len(transcript_list) > 0:
            with open("to_remove_video_url_with_transcript_list.txt", 'a') as f: f.write(url)
        elif len(transcript_list) == 0:
            with open("to_keep_video_url_with_transcript_list.txt", 'a') as f: f.write(url)
        else:
            with open("to_remove_video_url_with_transcript_list.txt", 'a') as f: f.write(url)
    except:
        video = YouTube(url.strip())
        if len(video.captions) == 0:
            with open("to_keep_video_url_with_transcript_list.txt", 'a') as f: f.write(url)
        else:
            with open("to_remove_video_url_with_transcript_list.txt", 'a') as f: f.write(url)

    return url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url-file", type=str)
    args = parser.parse_args()

    pool = mp.Pool(processes=32)
    with open(args.url_file, 'r') as f: url_list = f.readlines()

    to_remove_video_url_with_transcript_list = []
    if os.path.exists("to_remove_video_url_with_transcript_list.txt"):
        with open("to_remove_video_url_with_transcript_list.txt", 'r') as f: to_remove_video_url_with_transcript_list = f.readlines()
    
    to_keep_video_url_with_transcript_list = []
    if os.path.exists("to_keep_video_url_with_transcript_list.txt"):
        with open("to_keep_video_url_with_transcript_list.txt", 'r') as f: to_keep_video_url_with_transcript_list = f.readlines()

    checked_url_set = set(to_remove_video_url_with_transcript_list + to_keep_video_url_with_transcript_list)

    to_check_url_list = []
    for i in trange(len(url_list)):
        if url_list[i] not in checked_url_set: to_check_url_list.append(url_list[i])


    start_time = time.time()
    outputs = pool.map(check_audio, to_check_url_list)
    print("Elapsed time: {}".format(time.time() - start_time))



if __name__ == '__main__':
    main()
