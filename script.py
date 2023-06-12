import io
import os
import selectors
import subprocess
import sys


CMD = (
    "OPENAI_API_KEY=############################################"
    "PYTHONPATH=${PYTHONPATH}:/Users/sukiyaki/PycharmProjects/auto-gpt-ui/backend/src "
    "python "
    "/Users/sukiyaki/PycharmProjects/auto-gpt-ui/backend/src/app/auto_gpt/cli.py "
    "-w workspaces/user_1 "
    "-C workspaces/user_1/ai_settings.yaml "
    "--skip-news "
    "--skip-reprompt"
)


def run_command(subprocess_args):
    p = subprocess.Popen(
        subprocess_args,
        shell=isinstance(subprocess_args, str),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=False,
    )  # \r goes through

    nice_stdout = open(os.dup(p.stdout.fileno()), newline="")  # re-open to get \r recognized as new line
    for line in nice_stdout:
        yield line, p.poll()

    yield "", p.wait()


def run():
    with open("out.txt", "a+") as w:
        w.flush()
        for line, rc in run_command(CMD):
            print(line, end="", flush=True)
            w.write(line)
            w.flush()


if __name__ == "__main__":
    run()
