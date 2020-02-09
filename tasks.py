import sys
import os
import subprocess
from invoke import task


OUTPUT_FILENAME_TEMPLATE = "{language}-{model}.txt"
SEARCH_MODELS = [
    ("bm25",),
    ("bm25.accurate",),
    ("bm25prf", "bm25"),
    ("qld",),
    ("rm3", "bm25"),
    ("rm3", "qld"),
    ("sdm", "bm25"),
    ("sdm", "qld"),
]


def check_language_arg(language):
    if language not in ('ja', 'en'):
        print('Error: language option must be either ja or en.')
        sys.exit(1)


@task
def submodule(c):
    c.run("git submodule update -i", pty=True)


@task(submodule)
def build(c, recompile=False):
    print("Trying to build anserini ...")
    if os.path.exists("anserini/target/anserini-0.6.1-SNAPSHOT.jar")\
            and not recompile:
        print()
        print("Already compiled anserini. Stopped building it again.\n"
              "Set --recompile option for enforcing the re-compilation.\n")
        return

    cmd = "cd anserini && mvn clean package appassembler:assemble"
    result = c.run(cmd, pty=True)
    if result.ok:
        print()
        print("Compiled anserini successfully.\n")


@task(build)
def preprocess(c, language, input_filepath, output_dirpath):
    check_language_arg(language)

    print("Start preprocessing {} collection '{}'\n"
          "and saving the results into {} ...\n"
          .format(language, input_filepath, output_dirpath))

    if language == 'ja':
        from baselines.preprocessor_ja import Preprocessor
        preprocessor = Preprocessor(output_dirpath)
    else:
        pass

    preprocessor.run(input_filepath)


@task(build)
def index(c, language, input_dirpath, output_dirpath, threads=4):
    check_language_arg(language)

    cmd = "anserini/target/appassembler/bin/IndexCollection "\
        "-collection JsonCollection -generator LuceneDocumentGenerator "\
        "-storePositions -storeDocvectors -storeRawDocs "\
        "-language {} -input {} -index {} -threads {}"\
        .format(language, input_dirpath, output_dirpath, threads)
    result = c.run(cmd, pty=True)
    if result.ok:
        print()
        print("Created the index successfully.\n")


@task(build)
def search(c, language, index_dirpath, topic_filepath, output_dirpath):
    check_language_arg(language)

    if not os.path.exists(output_dirpath):
        os.mkdir(output_dirpath)

    base_cmd = "anserini/target/appassembler/bin/SearchCollection "\
        "-topicreader TsvString "\
        "-language {} -index {} -topics {} ".format(
            language, index_dirpath, topic_filepath
        )

    for model in SEARCH_MODELS:
        model_name = "+".join(model)
        output_filename = OUTPUT_FILENAME_TEMPLATE.format(language=language,
                                                          model=model_name)
        output_filepath = os.path.join(output_dirpath, output_filename)
        cmd = base_cmd + "-{}  -output {}".format(" -".join(model),
                                                  output_filepath)
        result = c.run(cmd, pty=True)
        if result.ok:
            print()
            print("Retrieved datasets by {} and saved them into {}.\n"
                  .format(model_name, output_filepath))
