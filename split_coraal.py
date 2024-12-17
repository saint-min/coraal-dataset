from pathlib import Path
from glob import glob
from tqdm.auto import tqdm
import re
import subprocess
import argparse
import jsonlines

def normalize(s):
    s = s.lower()
    s = re.sub('/rd-(.*?)/', '', s)
    s = re.sub('/inaudible/', '', s)
    s = re.sub('/unintelligible/', '', s)
    s = re.sub(r'\b(hm|hmm|mm|mhm|mmm|uh|um|huh)\b', '', s)
    s = re.sub(r'<(.*?)>', '', s)
    s = re.sub(r'\((.*?)\)', '', s)
    s = re.sub(r'[,.?!\":;/\[\]]', '', s)
    s = re.sub('-- ', '', s)
    s = re.sub('-', ' ', s)
    s = re.sub('[ ]{2,}', ' ', s)
    s = re.sub(r'^\s', '', s)
    s = re.sub(r'\s$', '', s)
    return s

def main(input_dir, output_dir):
    with open('./dataset_ids/train_ids.txt', 'r') as f:
        train_ids = f.read().splitlines()
    with open('./dataset_ids/val_ids.txt', 'r') as f:
        val_ids = f.read().splitlines()
    with open('./dataset_ids/test_ids.txt', 'r') as f:
        test_ids = f.read().splitlines()
    
    trains = []
    vals = []
    tests = []
    reference_files = glob(f"{input_dir}/*.txt")

    for reference_file in tqdm(reference_files):
        reference_file = Path(reference_file)
        input_wav = reference_file.with_suffix('.wav')
        file_output_dir = Path(output_dir) / reference_file.stem
        file_output_dir.mkdir(parents=True, exist_ok=True)

        file_texts = []
        file_wavs = []
        with open(reference_file) as f:
            next(f)  # Skip the first line
            i = 0
            for line in f:
                line_list = line.split('\t')
                reference = normalize(line_list[3])
                start_time = float(line_list[2])
                end_time = float(line_list[4])
                subprocess.run(['sox', str(input_wav), str(file_output_dir / f"{i:04}.wav"), "trim", str(start_time), "=" + str(end_time)])
                file_texts.append(reference)
                file_wavs.append(file_output_dir / f"{i:04}.wav")
                i += 1

        file_id = reference_file.stem
        file_utts = []

        for text, wav in zip(file_texts, file_wavs):
            if len(text) > 0:
                file_utts.append({'text': text, 'asr': '', 'audio': str(wav), 'start_time': start_time, 'end_time': end_time})

        file_dict = {'id': file_id, 'utterances': file_utts}

        if file_id in train_ids:
            trains.append(file_dict)
        elif file_id in val_ids:
            vals.append(file_dict)
        elif file_id in test_ids:
            tests.append(file_dict)
    

    with jsonlines.open(f"./train.jsonl", "w") as writer:
        writer.write_all(trains)
    with jsonlines.open(f"./val.jsonl", "w") as writer:
        writer.write_all(vals)
    with jsonlines.open(f"./test.jsonl", "w") as writer:
        writer.write_all(tests)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Normalize and split audio files based on timestamps in text files.")
    parser.add_argument("input_dir", type=str, help="Directory containing input .txt files.")
    parser.add_argument("output_dir", type=str, help="Output Directory.")
    args = parser.parse_args()

    main(args.input_dir, args.output_dir)
