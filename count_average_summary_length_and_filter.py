from tqdm import trange
from transformers import BertTokenizer
import numpy as np

def main():
    with open("image_captions_for_videos.txt", 'r') as f: image_caption_lines = f.readlines()
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

    length_list = []
    filtered_summary_list = []
    for i in trange(len(image_caption_lines)):
        try:
            video_id, summary = image_caption_lines[i].strip().split('\t')
            filtered_summary_list.append([video_id, summary])
            summary_tokens = tokenizer(summary)
            length_list.append(len(summary_tokens['input_ids']))
        except:
            continue

    min_length = np.min(length_list)
    mean_length = np.mean(length_list)
    max_length = np.max(length_list)
    median_length = np.median(length_list)
    print("Length statistics - Min: {}, Median: {}, Max: {}, Mean: {}".format(min_length, median_length, max_length, mean_length))

    with open("filtered_image_captions_for_videos.txt", 'w') as f:
        for i in trange(len(filtered_summary_list)):
            video_id, summary = filtered_summary_list[i]
            f.write("{}\t{}\n".format(video_id, summary))
 
if __name__ == '__main__':
    main()
