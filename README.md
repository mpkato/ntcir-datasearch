# ntcir-datasearch
Baselines for NTCIR Data Search

## Setup



### Installation of Poetry (skip this step if Poetry has already been installed)

```bash
$ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```

### Installation of required Python packages

```bash
$ source ~/.bash_profile
$ poetry install
```

### Installation of Java 

Since this package uses [Anserini](https://github.com/castorini/anserini),
Java 11 and Maven 3.3+ are also required.


### Downloading Data Search files

Please visit https://ntcir.datasearch.jp/ and download the test collection,
which includes

- `data_search_j_collection.jsonl.bz2`
- `data_search_e_collection.jsonl.bz2`
- `data_search_j_train_topics.tsv`
- `data_search_e_train_topics.tsv`

These files are expected to be in `data` directory.


## Build

Please run the command below for compiling Java codes of [Anserini](https://github.com/castorini/anserini):

```bash
$ poetry run invoke build
```

If the build successes, you will see a message that looks like

```bash
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  37.788 s
[INFO] Finished at: 2020-03-06T10:58:14+09:00
[INFO] ------------------------------------------------------------------------

Compiled anserini successfully.
```

## Indexing


Let's index the collection of Japanese statistical data. 

`preprocess` task reads contents from `data/data_search_j_collection.jsonl`,
and produces multiple files in JSONL format.

```bash
$ poetry run invoke preprocess ja data/data_search_j_collection.jsonl collections/ja
```

You can see the generated files by

```bash
$ ls collections/ja
collection.00000000.jsonl collection.00000003.jsonl collection.00000006.jsonl collection.00000009.jsonl collection.00000012.jsonl
collection.00000001.jsonl collection.00000004.jsonl collection.00000007.jsonl collection.00000010.jsonl collection.00000013.jsonl
collection.00000002.jsonl collection.00000005.jsonl collection.00000008.jsonl collection.00000011.jsonl
```

When you process the English statistical data `data_search_e_collection.jsonl`, `ja` should be replaced with `en`.

Then, `index` task indexes the collection as follows:
```bash
$ poetry run invoke index ja collections/ja indices/ja
...
2020-03-06 13:22:53,100 INFO  [main] index.IndexCollection (IndexCollection.java:841) - Total 1,338,402 documents indexed in 00:02:27

Created the index successfully.
```

You can find the index files at `indices/ja`.

## Search

After the index has been built,
`search` task can produce ranked lists by several search models such as BM25 and LMIR.

```bash
$ poetry run invoke search ja indices/ja data/data_search_j_train_topics.tsv results
```

This will read queries from `data/data_search_j_train_topics.tsv`,
retrieve results from `indices/ja`, and output them into `results` directory.


```bash
$ ls results/
ja-bm25.accurate.txt ja-bm25.txt          ja-bm25prf+bm25.txt  ja-qld.txt           ja-rm3+bm25.txt      ja-rm3+qld.txt       ja-sdm+bm25.txt      ja-sdm+qld.txt
```

The output file name is `<language>-<search_model>.txt`,
where 

- bm25                             : BM25 scoring model
- bm25.accurate                    : BM25 scoring model
- bm25prf                          : bm25PRF query expansion model
- qld                              : query likelihood Dirichlet scoring model
- rm3                              : RM3 query expansion model
- sdm                              : Sequential Dependence Model

Please refer to [Anserini](https://github.com/castorini/anserini) for details on search models.

Note that these results are in the TREC format, not the NTCIR format required in the NTCIR-15 Data Search task.
You can transform a TREC file into an NTCIR file by `ntcirify` command,
e.g. `poetry run invoke ntcirify trec_file.txt ntcir_file.txt`.
