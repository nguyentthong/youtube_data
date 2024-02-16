import transformers
from tqdm import trange
import torch
import os


def main():
    input_path = "filtered_image_captions_for_videos.txt"
    output_dir = "videos_with_question_answer_pairs"
    model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    pipeline = transformers.pipeline("text-generation", model=model, model_kwargs={"torch_dtype": torch.float16, "load_in_4bit": True})

    os.makedirs(output_dir, exist_ok=True)
    generated_video_id_set = set(os.listdir(output_dir))

    with open(input_path, 'r') as f: input_lines = f.readlines()

    for i in trange(len(input_lines)):
        video_id, input = input_lines[i].strip().split('\t')
        if video_id in generated_video_id_set: continue

        with open("{}/{}.txt".format(output_dir, video_id), 'w') as f:
            
            prompt = "write three questions and answers from this paragraph:: {}".format(input)
            messages = [{"role": "user", "content": prompt}]

            prompt = pipeline.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            outputs = pipeline(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)

            f.write(outputs[0]['generated_text'].split('[/INST]')[1].strip())
            f.flush()


if __name__ == '__main__':
    main()
