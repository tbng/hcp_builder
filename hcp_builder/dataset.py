import os
from os.path import join

from .s3 import download_from_s3_bucket
from .utils import get_data_dirs, get_credentials
from nilearn.datasets.utils import _fetch_file

evs = {'EMOTION': {'EMOTION_Stats.csv',
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


def fetch_hcp_single_subject(subject, data_type='all', tasks=None,
                             rest_sessions=None,
                             mock=False):
    root_path = get_data_dirs()[0]
    aws_key, aws_secret, _, _ = get_credentials()
    s3_keys = get_single_fmri_paths(subject, data_type=data_type,
                                    tasks=tasks,
                                    rest_sessions=rest_sessions)
    params = dict(
        bucket='hcp-openaccess',
        out_path=root_path,
        aws_key=aws_key,
        aws_secret=aws_secret,
        overwrite=False,
        prefix='HCP_900')
    download_from_s3_bucket(key_list=s3_keys, mock=mock, **params)


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


def get_single_fmri_paths(subject, data_type='all',
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
            tasks = ['EMOTION', 'WM', 'MOTOR', 'RELATIONAL', 'GAMBLING',
                     'SOCIAL', 'LANGUAGE']
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
                task_confounds = [join(task_dir, confound)
                                  for confound in task_confounds]
                out.append(task_func)
                out.append(mask_func)
                out += task_confounds
                # EVs
                subject_evs = [join(task_dir, 'EVs', ev) for ev in evs[task]]
                out += subject_evs
    return out


def get_subject_list(data_dir=None):
    import pandas as pd
    import numpy as np
    csv_file = fetch_unrestricted_behavioral_data(data_dir=data_dir)
    df = pd.read_csv(csv_file)

    indices = np.logical_and(df['3T_RS-fMRI_PctCompl'] == 100,
                             df['3T_tMRI_PctCompl'] == 100)
    return df.Subject[indices].tolist()