import sys
import os
import subprocess
from invoke import task


@task
def submodule(c):
    c.run("git submodule update -i", pty=True)


@task(submodule)
def build(c):
    cmd = "cd anserini && mvn clean package appassembler:assemble"
    result = c.run(cmd, pty=True)
    if result.ok:
        print()
        print("Compiled anserini successfully")
