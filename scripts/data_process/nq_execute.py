# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Preprocess the nq dataset to parquet format
"""

import re
import os
import datasets
import json

from verl.utils.hdfs_io import copy, makedirs
import argparse
import pdb

def make_prefix(dp, template_type):
    question = dp['question']
    tests = dp['test_list']

    if template_type == 'base':
        """This works for any base model"""
        prefix = f"""Answer the given programming question. \
You must conduct reasoning inside <think> and </think> at the beginning of generation and every time you get new execution output. \
After reasoning, you should write your best answer, the entire python file to solve the programming question. Write ONLY the Python code of your answer in between <execute> and </execute> and it will return the python execution information between <output> and </output>. \
You can execute new files as many times as you want. \
If you find no further execution testing is needed, you can directly provide the full code solution inside <answer> and </answer>.""" + """ For example, for a question on writing a function to find the similar elements from the given two tuple lists, the answer would be <answer> def similar_elements(test_tup1, test_tup2):\r\n  res = tuple(set(test_tup1) & set(test_tup2))\r\n  return (res)  </answer>.""" + f""" Question: {question}\r\n Your code should pass these tests: <tests> {tests} </tests> """
    else:
        raise NotImplementedError
    return prefix


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--local_dir', default='./data/nq_execute')
    parser.add_argument('--hdfs_dir', default=None)
    parser.add_argument('--template_type', type=str, default='base')

    args = parser.parse_args()

    data_source = 'mbpp'

    dataset = []
    with open('mbpp_data.jsonl', 'r') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                dataset.append(data)
    pdb.set_trace()

    train_size = int(0.8 * len(dataset))
    train_dataset = dataset[:train_size]
    test_dataset = dataset[train_size:]

    def make_map_fn(split):
        def process_fn(example, idx):
            question = example['text'].strip()
            test_list = example['test_list'].strip()
            # if question[-1] != '?':
            #     question += '?'
            
            question_data = {'question': question, 'test_list': test_list}
            prompt = make_prefix(question_data, template_type=args.template_type)
            
            solution = {
                "target": example['code'],
            }

            data = {
                "data_source": data_source,
                "prompt": [{
                    "role": "user",
                    "content": prompt,
                }],
                "ability": "code-generation",
                "reward_model": {
                    "style": "rule",
                    "ground_truth": solution
                },
                "extra_info": {
                    'split': split,
                    'index': idx,
                    'task_id': example['task_id']
                }
            }
            return data

        return process_fn

    processed_train = [make_map_fn('train')(ex, idx) for idx, ex in enumerate(train_dataset)]
    processed_test = [make_map_fn('test')(ex, idx) for idx, ex in enumerate(test_dataset)]

    train_dataset = datasets.Dataset.from_list(processed_train)
    test_dataset = datasets.Dataset.from_list(processed_test)

    local_dir = args.local_dir
    hdfs_dir = args.hdfs_dir

    train_dataset.to_parquet(os.path.join(local_dir, 'train_execute.parquet'))
    test_dataset.to_parquet(os.path.join(local_dir, 'test_execute.parquet'))

    if hdfs_dir is not None:
        makedirs(hdfs_dir)

        copy(src=local_dir, dst=hdfs_dir)
