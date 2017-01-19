import inspect
from os.path import join, dirname

import sys

from .s3 import download_from_s3_bucket
from hcp_builder.system import get_aws_credentials
from .system import get_data_dirs
from .files import get_fmri_path
import subprocess


def download(subject, mock=False):
    root_path = get_data_dirs()[0]
    aws_key, aws_secret = get_aws_credentials()
    s3_keys = get_fmri_path(subject)
    params = dict(
        bucket='hcp-openaccess',
        out_path=root_path,
        aws_key=aws_key,
        aws_secret=aws_secret,
        overwrite=False,
        prefix='HCP_900')
    download_from_s3_bucket(key_list=s3_keys, mock=mock, **params)


def make_contrasts(subject):
    root_path = get_data_dirs()[0]
    pathname = inspect.getfile(inspect.currentframe())
    script_dir = join(dirname(dirname(pathname)), 'glm_scripts')
    prepare_script = join(script_dir, 'prepare.sh')
    proc = subprocess.check_output(
        ['bash', prepare_script, root_path, str(subject)],
        bufsize=0,  # 0=unbuffered, 1=line-buffered, else buffer-size
        stderr=subprocess.PIPE)
    print(proc)
    compute_script = join(script_dir, 'compute_stats.sh')
    for task in ['EMOTION']:
        process = subprocess.Popen(['bash', compute_script,
                                    root_path, str(subject), task],
                                   bufsize=0,
                                   stderr=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        rc = process.poll()
