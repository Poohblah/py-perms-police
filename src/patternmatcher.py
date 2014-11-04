import os
import subprocess

def matches(path, pattern):
    cmd = os.path.dirname(os.path.realpath(__file__)) + '/matches.bash'
    return not subprocess.call([cmd, path, pattern])
