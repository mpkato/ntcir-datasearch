import json
import os
from tqdm import tqdm


class Preprocessor(object):

    FILENAME = "collection.{:08d}.jsonl"
    MAX_LINE_NUM = 100000

    def __init__(self, output_dirpath):
        self.file_writer = None
        self.index = 0
        self.counter = 0
        self.output_dirpath = output_dirpath

        if not os.path.exists(self.output_dirpath):
            os.mkdir(self.output_dirpath)

    def run(self, input_filepath):
        self._open()

        with open(input_filepath) as fr:
            for line in tqdm(fr):
                doc = json.loads(line)
                contents = "\n".join([doc["title"], doc["description"]]
                                     + list(doc["data_fields"].values()))
                newdoc = dict(
                    id=doc['id'],
                    contents=contents
                )
                self._write(json.dumps(newdoc) + '\n')

        self._close()

    def _open(self):
        self._update()

    def _close(self):
        if self.file_writer:
            self.file_writer.close()

    def _write(self, content):
        if self.counter >= self.MAX_LINE_NUM:
            self.index += 1
            self._update()
        self.file_writer.write(content)
        self.counter += 1

    def _update(self):
        if self.file_writer:
            self.file_writer.close()
        self.counter = 0

        output_filepath = os.path.join(self.output_dirpath,
                                       self.FILENAME.format(self.index))
        self.file_writer = open(output_filepath, 'w')
