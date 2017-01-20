import inspect
import os
import subprocess
import sys
from os.path import join, dirname
from subprocess import Popen, PIPE, CalledProcessError

import shutil

from .dataset import get_single_fmri_paths
from .utils import get_data_dirs


def make_contrasts(subject, tasks=None):
    root_path = get_data_dirs()[0]
    pathname = inspect.getfile(inspect.currentframe())
    script_dir = join(dirname(dirname(pathname)), 'glm_scripts')
    subject = str(subject)
    prepare_script = join(script_dir, 'prepare.sh')
    compute_script = join(script_dir, 'compute_stats.sh')
    if tasks is None:
        tasks = ['EMOTION', 'WM', 'MOTOR', 'RELATIONAL',
                 'GAMBLING', 'SOCIAL', 'LANGUAGE']
    elif isinstance(tasks, str):
        tasks = [tasks]
    for task in tasks:
        try:
            subprocess.call(['bash', prepare_script, root_path, subject, task])
            process = Popen(['bash', compute_script,
                             root_path, subject, task],
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
            raise ValueError('HCP Pipeline script failed for task %s.' % task)


def clean_artifacts(subject, tasks=None):
    root_path = get_data_dirs()[0]
    subject = str(subject)
    s3_keys = get_single_fmri_paths(subject)
    subject_dir = join(root_path, subject, 'MNINonLinear', 'Results')
    if tasks is None:
        tasks = ['EMOTION', 'WM', 'MOTOR', 'RELATIONAL',
                 'GAMBLING', 'SOCIAL', 'LANGUAGE']
    elif isinstance(tasks, str):
        tasks = [tasks]
    for task in tasks:
        for run_direction in ['LR', 'RL']:
            filename = 'tfMRI_%s_%s' % (task, run_direction)
            task_dir = join(subject_dir, filename)
            if os.path.exists(task_dir):
                for dirpath, dirnames, filenames in os.walk(task_dir):
                    for name in filenames:
                        name = join(dirpath, name)
                        target_name = name.replace(root_path, 'HCP_900')
                        if target_name not in s3_keys:
                            print('Delete %s' % name)
                            os.unlink(name)
                for dirpath, dirnames, filenames in os.walk(task_dir,
                                                            topdown=False):
                    for dirname in dirnames:
                        dir = join(dirpath, dirname)
                        try:
                            os.rmdir(dir)
                        except OSError:
                            pass
            lvl2_task_dir = join(subject_dir, 'tfMRI_%s' % task)
            if os.path.exists(lvl2_task_dir):
                shutil.rmtree(lvl2_task_dir)