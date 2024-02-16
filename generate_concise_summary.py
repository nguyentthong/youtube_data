import transformers
from tqdm import trange
import torch
import os


def main():
    input_path = "filtered_image_captions_for_videos.txt"
    output_path = "concise_summaries_for_videos.txt"
    model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    pipeline = transformers.pipeline("text-generation", model=model, model_kwargs={"torch_dtype": torch.float16, "load_in_4bit": True})

    summarized_video_id_set = set()
    if os.path.exists(output_path):
        with open(output_path, 'r') as f: output_lines = f.readlines()
        for line in output_lines:
            video_id = line.split('\t')[0]
            summarized_video_id_set.add(video_id)

    with open(input_path, 'r') as f: input_lines = f.readlines()

    with open(output_path, 'a') as f:
        for i in trange(len(input_lines)):
            video_id, input = input_lines[i].strip().split('\t')
            if video_id in summarized_video_id_set: continue
            
            prompt = "Write a concise summary for this paragraph: {}".format(input)
            messages = [{"role": "user", "content": prompt}]

            prompt = pipeline.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            outputs = pipeline(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)

            f.write(video_id + '\t' + outputs[0]['generated_text'].split('[/INST]')[1].strip())
            f.write('\n')
            f.flush()


if __name__ == '__main__':
    main()
