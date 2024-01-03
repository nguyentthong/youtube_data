import cv2
import os
from tqdm import tqdm

def main():
    video_id_list = os.listdir("./video_frames")
    os.makedirs("concatenated_frames", exist_ok=True)

    for i, video_id in enumerate(tqdm(video_id_list)):
        try:
            image_frame_dir = os.path.join("video_frames", video_id)
            image_frame_file_list = sorted(os.listdir(image_frame_dir), key=lambda x: int(x.split('.')[0].split('_')[1]))
            img_list = []
            for image_frame_file in image_frame_file_list:
                img_frame = cv2.imread(os.path.join(image_frame_dir, image_frame_file))
                img_list.append(img_frame)
            
            img_row1 = cv2.hconcat(img_list[:4])
            img_row2 = cv2.hconcat(img_list[4:8])
            img_row3 = cv2.hconcat(img_list[8:12])
            img_v = cv2.vconcat([img_row1, img_row2, img_row3])
            cv2.imwrite(os.path.join("concatenated_frames", video_id + ".jpg"), img_v)
        except:
            continue


if __name__ == '__main__':
    main()
