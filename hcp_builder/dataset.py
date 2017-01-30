import os
from os.path import join

import nibabel

from .utils.s3 import download_from_s3_bucket
from nilearn.datasets.utils import _fetch_file

TASK_LIST = ['EMOTION', 'WM', 'MOTOR', 'RELATIONAL', 'GAMBLING', 'SOCIAL', 'LANGUAGE']

EVS = {'EMOTION': {'EMOTION_Stats.csv',
                   'Sync.txt',
                   'fear.txt',
                   'neut.txt'},
       'GAMBLING': {
           'GAMBLING_Stats.csv',
           'Sync.txt',
           'loss.txt',
           'loss_event.txt',
           'neut_event.txt',
           'win.txt',
           'win_event.txt',
       },
       'LANGUAGE': {
           'LANGUAGE_Stats.csv',
           'Sync.txt',
           'cue.txt',
           'math.txt',
           'present_math.txt',
           'present_story.txt',
           'question_math.txt',
           'question_story.txt',
           'response_math.txt',
           'response_story.txt',
           'story.txt',
       },
       'MOTOR': {
           'Sync.txt',
           'cue.txt',
           'lf.txt',
           'lh.txt',
           'rf.txt',
           'rh.txt',
           't.txt',
       },
       'RELATIONAL': {
           'RELATIONAL_Stats.csv',
           'Sync.txt',
           'error.txt',
           'match.txt',
           'relation.txt',
       },
       'SOCIAL': {
           'SOCIAL_Stats.csv',
           'Sync.txt',
           'mental.txt',
           'mental_resp.txt',
           'other_resp.txt',
           'rnd.txt',
       },
       'WM': {
           '0bk_body.txt',
           '0bk_cor.txt',
           '0bk_err.txt',
           '0bk_faces.txt',
           '0bk_nlr.txt',
           '0bk_places.txt',
           '0bk_tools.txt',
           '2bk_body.txt',
           '2bk_cor.txt',
           '2bk_err.txt',
           '2bk_faces.txt',
           '2bk_nlr.txt',
           '2bk_places.txt',
           '2bk_tools.txt',
           'Sync.txt',
           'WM_Stats.csv',
           'all_bk_cor.txt',
           'all_bk_err.txt'}
       }


def download_single_subject(subject, data_type='all', tasks=None,
                            rest_sessions=None,
                            overwrite=False,
                            mock=False,
                            verbose=0):
    root_path = get_data_dirs()[0]
    aws_key, aws_secret, _, _ = get_credentials()
    s3_keys = _get_single_fmri_paths(subject, data_type=data_type,
                                     tasks=tasks,
                                     rest_sessions=rest_sessions)
    params = dict(
        bucket='hcp-openaccess',
        out_path=root_path,
        aws_key=aws_key,
        aws_secret=aws_secret,
        overwrite=overwrite,
        prefix='HCP_900')
    if verbose > 0:
        print('Downloading files for subject %s, task %s' % (subject, tasks))
    filenames = download_from_s3_bucket(key_list=s3_keys, mock=mock,
                                        verbose=verbose-1, **params)
    for filename in filenames:
        name, ext = os.path.splitext(filename)
        if ext == '.gz':
            try:
                _ = nibabel.load(filename).get_shape()
            except:
                raise ConnectionError('Some files were corrupted. Rerun.')


def fetch_unrestricted_behavioral_data(data_dir=None, overwrite=False,
                                       username=None,
                                       password=None):
    if username is None or password is None:
        _, _, username, password = get_credentials(data_dir=data_dir)
    data_dir = get_data_dirs(data_dir)[0]
    csv_file = join(data_dir, 'hcp_unrestricted_data.csv')
    if not os.path.exists(csv_file) or overwrite:
        result = _fetch_file(data_dir=data_dir,
                             url='https://db.humanconnectome.org/REST/'
                                 'search/dict/Subject%20Information/results?'
                                 'format=csv&removeDelimitersFromFieldValues'
                                 '=true'
                                 '&restricted=0&project=HCP_900',
                             username=username, password=password)
        os.rename(result, csv_file)
    return csv_file


def fetch_subject_list(data_dir=None):
    import pandas as pd
    import numpy as np
    csv_file = fetch_unrestricted_behavioral_data(data_dir=data_dir)
    df = pd.read_csv(csv_file)

    indices = np.logical_and(df['3T_RS-fMRI_PctCompl'] == 100,
                             df['3T_tMRI_PctCompl'] == 100)
    return df.Subject[indices].tolist()


def _get_single_fmri_paths(subject, data_type='all',
                           rest_sessions=None, tasks=None):
    """Utility to download from s3"""
    subject = str(subject)
    out = []
    subject_dir = join('HCP_900', subject, 'MNINonLinear', 'Results')

    if data_type not in ['all', 'rest', 'task']:
        raise ValueError("Wrong data type. Expected ['rest', 'type'], got"
                         "%s" % data_type)

    if data_type in ['all', 'rest']:
        if rest_sessions is None:
            rest_sessions = [1, 2]
        elif isinstance(rest_sessions, int):
            rest_sessions = [rest_sessions]
        for session in rest_sessions:
            for run_direction in ['LR', 'RL']:
                filename = 'rfMRI_REST%i_%s' % (session, run_direction)
                rest_dir = join(subject_dir, filename)
                rest_func = join(rest_dir, filename + '.nii.gz')
                mask_func = join(rest_dir, filename + '_SBRef.nii.gz')
                rest_confounds = ['Movement_AbsoluteRMS_mean.txt',
                                  'Movement_AbsoluteRMS.txt',
                                  'Movement_Regressors_dt.txt',
                                  'Movement_Regressors.txt',
                                  'Movement_RelativeRMS_mean.txt',
                                  'Movement_RelativeRMS.txt']
                rest_confounds = [join(rest_dir, confound)
                                  for confound in rest_confounds]
                out.append(rest_func)
                out.append(mask_func)
                out += rest_confounds
    # Tasks
    if data_type in ['all', 'task']:
        if tasks is None:
            tasks = TASK_LIST
        elif isinstance(tasks, str):
            tasks = [tasks]
        for task in tasks:
            for run_direction in ['LR', 'RL']:
                filename = 'tfMRI_%s_%s' % (task, run_direction)
                task_dir = join(subject_dir, filename)
                task_func = join(task_dir, filename + '.nii.gz')
                mask_func = join(task_dir, filename + '_SBRef.nii.gz')
                task_confounds = ['Movement_AbsoluteRMS_mean.txt',
                                  'Movement_AbsoluteRMS.txt',
                                  'Movement_Regressors_dt.txt',
                                  'Movement_Regressors.txt',
                                  'Movement_RelativeRMS_mean.txt',
                                  'Movement_RelativeRMS.txt']
                task_fsf = join(task_dir, "tfMRI_%s_%s_hp200_s4_level1.fsf" % (task, run_direction))
                task_confounds = [join(task_dir, confound)
                                  for confound in task_confounds]
                out.append(task_func)
                out.append(mask_func)
                out.append(task_fsf)
                out += task_confounds
                # EVs
                subject_evs = [join(task_dir, 'EVs', ev) for ev in EVS[task]]
                out += subject_evs
    return out


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