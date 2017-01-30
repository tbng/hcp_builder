import inspect
import os
import subprocess
import subprocess as sp
import sys
from os.path import dirname
from os.path import join

import shutil


def configure():
    pathname = inspect.getfile(inspect.currentframe())
    pathname = join(dirname(dirname(pathname)), 'glm_scripts')
    os.environ['HCPPIPEDIR'] = join(pathname, 'HCP-pipeline-scripts')
    os.environ['HCPPIPEDIR_tfMRIAnalysis'] = join(
        os.environ['HCPPIPEDIR'],
        'TaskfMRIAnalysis', 'scripts')
    command = 'env -i bash -c "source /etc/fsl/5.0/fsl.sh && env"'
    for line in subprocess.getoutput(command).split("\n"):
        key, value = line.split("=")
        os.environ[key] = value


def get_data_dirs(data_dir=None):
    """ Returns the directories in which modl looks for data.

    This is typically useful for the end-user to check where the data is
    downloaded and stored.

    Parameters
    ----------
    data_dir: string, optional
        Path of the data directory. Used to force data storage in a specified
        location. Default: None

    Returns
    -------
    paths: list of strings
        Paths of the dataset directories.

    Notes
    -----
    This function retrieves the datasets directories using the following
    priority :
    1. the keyword argument data_dir
    2. the global environment variable MODL_SHARED_DATA
    3. the user environment variable MODL_DATA
    4. modl_data in the user home folder
    """

    paths = []

    # Check data_dir which force storage in a specific location
    if data_dir is not None:
        paths.extend(data_dir.split(os.pathsep))

    # If data_dir has not been specified, then we crawl default locations
    if data_dir is None:
        global_data = os.getenv('HCP_SHARED_DATA')
        if global_data is not None:
            paths.extend(global_data.split(os.pathsep))

        local_data = os.getenv('HCP_DATA')
        if local_data is not None:
            paths.extend(local_data.split(os.pathsep))

        paths.append(os.path.expanduser('~/HCP'))
    return paths


def get_credentials(filename=None, data_dir=None):
    """Retrieve credentials for COnnectomeDB and S3 bucket access.

    First try to look whether

    Parameters
    ----------
    filename: str,
        Filename of
    """
    try:
        if filename is None:
            filename = 'credentials.txt'
        if not os.path.exists(filename):
            data_dir = get_data_dirs(data_dir)[0]
            filename = join(data_dir, filename)
            if not os.path.exists(filename):
                if ('HCP_AWS_KEY' in os.environ
                        and 'HCP_AWS_SECRET_KEY' in os.environ
                        and 'CDB_USERNAME' in os.environ
                        and 'CDB_PASSWORD' in os.environ):
                    aws_key = os.environ['HCP_AWS_KEY']
                    aws_secret = os.environ['HCP_AWS_SECRET_KEY']
                    cdb_username = os.environ['CDB_USERNAME']
                    cdb_password = os.environ['CDB_PASSWORD']
                    return aws_key, aws_secret, cdb_username, cdb_password
                else:
                    raise KeyError('Could not find environment variables.')
        file = open(filename, 'r')
        return file.readline()[:-1].split(',')
    except (KeyError, FileNotFoundError):
        raise ValueError("Cannot find credentials. Provide them"
                         "in a file credentials.txt where the script is "
                         "executed, or in the HCP directory, or in"
                         "environment variables.")


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
    from ..dataset import get_single_fmri_paths

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