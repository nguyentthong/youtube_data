from tqdm import trange

def main():
    with open("video_url_num_frames_list.txt", 'r') as f: lines = f.readlines()
    video_with_high_number_of_frames_line_list = []
    for i in trange(len(lines)):
        video, num_frames = lines[i].strip().split('\t')
        num_frames = int(num_frames)
        if num_frames <= 15000: continue
        video_with_high_number_of_frames_line_list.append(lines[i])
    with open("video_url_high_num_frames_list.txt", 'w') as f:
        for line in video_with_high_number_of_frames_line_list:
            f.write(line)

if __name__ == '__main__':
    main()
