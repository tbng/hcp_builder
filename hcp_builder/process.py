import inspect
import os
import subprocess
from subprocess import Popen, PIPE, CalledProcessError
from os.path import join, dirname

import sys

from hcp_builder.system import get_aws_credentials

from .files import get_fmri_path
from .s3 import download_from_s3_bucket
from .system import get_data_dirs


def download(subject, data_type='all', mock=False):
    root_path = get_data_dirs()[0]
    aws_key, aws_secret = get_aws_credentials()
    s3_keys = get_fmri_path(subject, data_type=data_type)
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
    try:
        subprocess.call(['bash', prepare_script, root_path, str(subject)])
    except CalledProcessError:
        raise ValueError('HCP Pipeline script failed')
    compute_script = join(script_dir, 'compute_stats.sh')
    for task in ['EMOTION', 'WM', 'MOTOR', 'RELATIONAL', 'GAMBLING', 'SOCIAL', 'LANGUAGE']:
        try:
            process = Popen(['bash', compute_script,
                             root_path, str(subject), task],
                            stdout=PIPE, stderr=PIPE
                            )
            while True:
                out = process.stdout.read(1)
                if process.poll() is not None:
                    break
                if out != '':
                    sys.stdout.write(out.decode('utf-8'))
                    sys.stdout.flush()
        except CalledProcessError:
            raise ValueError('HCP Pipeline script failed for task %s' % task)


def clean_artifacts(subject):
    root_path = get_data_dirs()[0]
    s3_keys = get_fmri_path(subject)
    for dirpath, dirnames, filenames in os.walk(join(root_path, str(subject))):
        for name in filenames:
            name = join(dirpath, name)
            target_name = name.replace(root_path, 'HCP_900')
            if target_name not in s3_keys:
                print('rm %s' % name)
                os.unlink(name)
    for dirpath, dirnames, filenames in os.walk(join(root_path, str(subject)),
                                                topdown=False):
        for dirname in dirnames:
            dir = join(dirpath, dirname)
            try:
                os.rmdir(dir)
            except OSError:
                pass


def run(command):
    process = Popen(command, stdout=PIPE, stderr=PIPE)
