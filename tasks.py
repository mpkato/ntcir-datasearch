import sys
import os
import subprocess
from invoke import task


@task
def submodule(c):
    c.run("git submodule update -i", pty=True)


@task(submodule)
def build(c, recompile=False):
    if os.path.exists("anserini/target/anserini-0.6.1-SNAPSHOT.jar")\
          and not recompile:
        print("Already compiled anserini. Stopped building it again.\n"
              "Set --recompile option for enforcing the re-compilation.")
        return

    cmd = "cd anserini && mvn clean package appassembler:assemble"
    result = c.run(cmd, pty=True)
    if result.ok:
        print()
        print("Compiled anserini successfully")
