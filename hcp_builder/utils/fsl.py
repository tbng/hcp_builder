import inspect
import os
import shutil
import subprocess
import subprocess as sp
import sys
from os.path import dirname
from os.path import join

from hcp_builder.dataset import get_data_dirs


def configure():
    pathname = inspect.getfile(inspect.currentframe())
    pathname = join(dirname(dirname(pathname)), 'hcp_scripts')
    os.environ['HCPPIPEDIR'] = join(pathname, 'HCP-pipeline-scripts')
    os.environ['HCPPIPEDIR_tfMRIAnalysis'] = join(
        os.environ['HCPPIPEDIR'],
        'TaskfMRIAnalysis', 'scripts')
    command = 'env -i bash -c "source /etc/fsl/5.0/fsl.sh && env"'
    for line in subprocess.getoutput(command).split("\n"):
        key, value = line.split("=")
        os.environ[key] = value


def run_cmd(lst_cmd, verbose=False):
    process = sp.Popen(lst_cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)

    s_cmd = ' '.join(lst_cmd)
    print("Command: '%s'\n" % s_cmd)
    if verbose:
        while True:
            out = process.stdout.read(1)
            if process.poll() is not None:
                break
            if out != '':
                sys.stdout.write(out.decode('utf-8'))
                sys.stdout.flush()
    else:
        process.communicate()
    if 0 != process.returncode:
        print(process.stderr.read().decode('utf-8'))
        raise sp.CalledProcessError(process.returncode,
                                    s_cmd, output=process.stdout,
                                    stderr=process.stderr)
    else:
        print("Command succeeded!")


def clean_artifacts(subject, tasks=None, verbose=0):
    from ..dataset import _get_single_fmri_paths

    root_path = get_data_dirs()[0]
    subject = str(subject)
    s3_keys = _get_single_fmri_paths(subject)
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
                            if verbose > 0:
                                print('Delete %s' % name)
                            try:
                                os.unlink(name)
                            except (IOError, OSError):
                                print('IO ERROR')
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
                try:
                    shutil.rmtree(lvl2_task_dir)
                except (IOError, OSError):
                    print('IO ERROR')