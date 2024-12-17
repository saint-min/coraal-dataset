# Can Noisy Cross-Utterance Contexts Help Speech-Recognition Error Correction? (IWSDS 2024)

This is the code to reproduce the CORAAL dataset that we processed and used in our paper.

## Usage

Prerequisites: sox, wget installed

```shell
# Download and extract the CORAAL dataset
./download_coraal.sh coraal_download_list.txt .

# Truncate the dataset by utterance
python split_coraal.py ./extracted ./split
```

This will generate train / val / test jsonl files like below.

```json
{
  "id": "ATL_se0_ag1_f_02_1",
  "utterances": [
    {
      "text": "okay",
      "asr": "",
      "audio": "split/ATL_se0_ag1_f_02_1/0000.wav",
      "start_time": 2210.787,
      "end_time": 2211.325
    },
    {
      "text": "my name is and",
      "asr": "",
      "audio": "split/ATL_se0_ag1_f_02_1/0004.wav",
      "start_time": 2210.787,
      "end_time": 2211.325
    },
    ...
  ],
  ...
}
```

You can use this splited utterances directly, or you can substitute all of your speech recognition results into the asr value of each utterance and use it as a Huggingface dataset like below.

```python
import datasets

ds = datasets.load_dataset("../coraal", data_dir="../coraal", n_fronts=5, n_bodies=1, n_rears=5, oracle=True)
```

If oracle is true, the front and rear context becomes ground_truth.