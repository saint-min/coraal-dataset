import json
import os
from more_itertools import windowed
import datasets

_CITATION = """\
"""

_DESCRIPTION = """\
coraalを音声認識した誤り訂正用データセット
"""
_HOMEPAGE = ""
_LICENSE = ""

class coraal_asr_config(datasets.BuilderConfig):
    def __init__(self, n_fronts=0, n_bodies=1, n_rears=0,
                 front_prefix='front:\n', body_prefix='body:\n', rear_prefix='rear:\n',
                 oracle=False,
                 **kwargs):
        super(coraal_asr_config, self).__init__(**kwargs)
        self.n_fronts = n_fronts
        self.n_bodies = n_bodies
        self.n_rears = n_rears
        self.front_prefix = front_prefix
        self.body_prefix = body_prefix
        self.rear_prefix = rear_prefix
        self.oracle = oracle


class coraal_asr(datasets.GeneratorBasedBuilder):
    VERSION = datasets.Version("0.2.0")
    BUILDER_CONFIGS = [
        coraal_asr_config(name="v1", version=VERSION),
    ]
    DEFAULT_CONFIG_NAME = "v1"

    def _info(self):
        feature_dict = {
            "text": datasets.Value("string"),
            "text_asr": datasets.Value("string"),
            "src": datasets.Value("string"),
            "tgt": datasets.Value("string"),
            "id": datasets.Value("string")
        }

        features = datasets.Features(feature_dict)
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=features,
            supervised_keys=None,
            homepage=_HOMEPAGE,
            license=_LICENSE,
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        """Split data into train, validation, and test sets."""
        # data_dir 경로를 가져오기
        data_dir = dl_manager.manual_dir  # data_dir에서 설정된 경로를 가져옵니다.

        # JSONL 파일 경로 설정
        train_path = os.path.join(data_dir, "train.jsonl")
        val_path = os.path.join(data_dir, "val.jsonl")
        test_path = os.path.join(data_dir, "test.jsonl")

        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={"filepath": train_path, "split": "train"},
            ),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION,
                gen_kwargs={"filepath": val_path, "split": "validation"},
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={"filepath": test_path, "split": "test"},
            ),
        ]

    def _generate_examples(self, filepath, split):
        """Yields examples."""
        id_ = 0
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                doc = json.loads(line)
                utterances = doc['utterances']
                # divide text and asr
                texts_asr = [utt['asr'] for utt in utterances]
                texts = [utt['text'] for utt in utterances]
                # window considering front and rear contexts
                if split == "train":
                    windowed_texts_asr = windowed([''] * self.config.n_fronts + texts_asr + [''] * self.config.n_rears, self.config.n_bodies + self.config.n_fronts + self.config.n_rears)
                    windowed_oracles = windowed([''] * self.config.n_fronts + texts + [''] * self.config.n_rears, self.config.n_bodies + self.config.n_fronts + self.config.n_rears)
                    windowed_texts = windowed(texts, self.config.n_bodies)
                else:
                    windowed_texts_asr = windowed([''] * self.config.n_fronts + texts_asr + [''] * self.config.n_rears, self.config.n_bodies + self.config.n_fronts + self.config.n_rears, fillvalue='', step=self.config.n_bodies)
                    windowed_oracles = windowed([''] * self.config.n_fronts + texts + [''] * self.config.n_rears, self.config.n_bodies + self.config.n_fronts + self.config.n_rears, fillvalue='', step=self.config.n_bodies)
                    windowed_texts = windowed(texts, self.config.n_bodies, fillvalue='', step=self.config.n_bodies)
                
                for text_asr, text, oracle, utt in zip(windowed_texts_asr, windowed_texts, windowed_oracles, utterances):
                    src = ''
                    if self.config.n_fronts > 0:
                        src += self.config.front_prefix
                        if self.config.oracle:
                            src += '\n'.join(oracle[:self.config.n_fronts])
                        else:
                            src += '\n'.join(text_asr[:self.config.n_fronts])
                        src += '\n'
                    src += self.config.body_prefix
                    src += '\n'.join(text_asr[self.config.n_fronts:self.config.n_fronts + self.config.n_bodies])
                    if self.config.n_rears > 0:
                        src += '\n' + self.config.rear_prefix
                        if self.config.oracle:
                            src += '\n'.join(oracle[self.config.n_fronts + self.config.n_bodies:])
                        else:
                            src += '\n'.join(text_asr[self.config.n_fronts + self.config.n_bodies:])
                    tgt = '\n'.join(text)
                    
                    data = {
                        "text": utt["text"],
                        "text_asr": utt["asr"],
                        'src': src,
                        'tgt': tgt,
                        'id': doc["id"],
                    }
                    
                    yield id_, data
                    
                    id_ += 1