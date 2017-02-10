import glob
import os
import warnings
from os.path import join

import nibabel
import pandas as pd
from nilearn.datasets.utils import _fetch_file
from sklearn.datasets.base import Bunch

from .utils.s3 import download_from_s3_bucket

TASK_LIST = ['EMOTION', 'WM', 'MOTOR', 'RELATIONAL',
             'GAMBLING', 'SOCIAL', 'LANGUAGE']

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

contrasts_description = {'2BK': {'Cognitive Task': 'Two-Back Memory',
                                 'Instruction to participants': 'Indicate whether current stimulus is the same as two items earlier',
                                 'Stimulus material': 'Task Pictures'},
                         'BODY-AVG': {'Cognitive Task': 'View Bodies',
                                      'Instruction to participants': 'Passive watching',
                                      'Stimulus material': 'Pictures'},
                         'FACE-AVG': {'Cognitive Task': 'View Faces',
                                      'Instruction to participants': 'Passive watching',
                                      'Stimulus material': 'Pictures'},
                         'FACES': {'Cognitive Task': 'Shapes',
                                   'Instruction to participants': 'Decide which of two shapes matches another shape geometry-wise',
                                   'Stimulus material': 'Shape pictures'},
                         'SHAPES': {'Cognitive Task': 'Faces',
                                    'Instruction to participants': 'Decide which of two faces matches another face emotion-wise',
                                    'Stimulus material': 'Face pictures'},
                         'LF': {'Cognitive Task': 'Food movement',
                                'Instruction to participants': 'Squeezing of the left or right toe',
                                'Stimulus material': 'Visual cues'},
                         'LH': {'Cognitive Task': 'Hand movement',
                                'Instruction to participants': 'Tapping of the left or right finger',
                                'Stimulus material': 'Visual cues'},
                         'MATCH': {'Cognitive Task': 'Matching',
                                   'Instruction to participants': 'Decide whether two objects match in shape or texture',
                                   'Stimulus material': 'Pictures'},
                         'MATH': {'Cognitive Task': 'Mathematics',
                                  'Instruction to participants': 'Complete addition and subtraction problems',
                                  'Stimulus material': 'Spoken numbers'},
                         'PLACE-AVG': {'Cognitive Task': 'View Places',
                                       'Instruction to participants': 'Passive watching',
                                       'Stimulus material': 'Pictures'},
                         'PUNISH': {'Cognitive Task': 'Reward',
                                    'Instruction to participants': 'Guess the number of mystery card for gain/loss of money',
                                    'Stimulus material': 'Card game'},
                         'RANDOM': {'Cognitive Task': 'Random',
                                    'Instruction to participants': 'Decide whether the objects act randomly or intentionally',
                                    'Stimulus material': 'Videos with objects'},
                         'REL': {'Cognitive Task': 'Relations',
                                 'Instruction to participants': 'Decide whether object pairs differ both along either shapeor texture',
                                 'Stimulus material': 'Pictures'},
                         'REWARD': {'Cognitive Task': 'Punish',
                                    'Instruction to participants': 'Guess the number of mystery card for gain/loss of money',
                                    'Stimulus material': 'Card game'},
                         'STORY': {'Cognitive Task': 'Language',
                                   'Instruction to participants': 'Choose answer about the topic of the story',
                                   'Stimulus material': 'Auditory stories'},
                         'T': {'Cognitive Task': 'Tongue movement',
                               'Instruction to participants': 'Move tongue',
                               'Stimulus material': 'Visual cues'},
                         'TOM': {'Cognitive Task': 'Theory of mind',
                                 'Instruction to participants': 'Decide whether the objects act randomly or intentionally',
                                 'Stimulus material': 'Videos with objects'},
                         'TOOL-AVG': {'Cognitive Task': 'View Tools',
                                      'Instruction to participants': 'Passive watching',
                                      'Stimulus material': 'Pictures'}}


def fetch_behavioral_data(data_dir=None,
                          n_subjects=None,
                          restricted=False,
                          overwrite=False, ):
    _, _, username, password = get_credentials(data_dir=data_dir)
    data_dir = get_data_dirs(data_dir)[0]
    behavioral_dir = join(data_dir, 'behavioral')
    if not os.path.exists(behavioral_dir):
        os.makedirs(behavioral_dir)
    csv_unrestricted = join(behavioral_dir, 'hcp_unrestricted_data.csv')
    if not os.path.exists(csv_unrestricted) or overwrite:
        result = _fetch_file(data_dir=data_dir,
                             url='https://db.humanconnectome.org/REST/'
                                 'search/dict/Subject%20Information/results?'
                                 'format=csv&removeDelimitersFromFieldValues'
                                 '=true'
                                 '&restricted=0&project=HCP_900',
                             username=username, password=password)
        os.rename(result, csv_unrestricted)
    csv_restricted = join(behavioral_dir, 'hcp_restricted_data.csv')
    df_unrestricted = pd.read_csv(csv_unrestricted, nrows=n_subjects)
    df_unrestricted.set_index('Subject', inplace=True)
    if restricted and not os.path.exists(csv_restricted):
        warnings.warn("Cannot automatically retrieve restricted data. "
                      "Please create the file '%s' manually" %
                      csv_restricted)
        restricted = False
    if not restricted:
        df = df_unrestricted
    else:
        df_restricted = pd.read_csv(csv_restricted, nrows=n_subjects)
        df_restricted.set_index('Subject', inplace=True)
        df = df_unrestricted.join(df_restricted, how='outer')
    df.sort_index(ascending=True, inplace=True)
    df.index.names = ['subject']
    return df


def fetch_subject_list(data_dir=None, n_subjects=None,
                       overwrite=False):
    df = fetch_behavioral_data(data_dir=data_dir, n_subjects=n_subjects,
                               overwrite=overwrite)
    return df.index.get_level_values('subject').unique().tolist()


def _convert_to_s3_target(filename, data_dir=None):
    data_dir = get_data_dirs(data_dir)[0]
    if data_dir in filename:
        filename = filename.replace(data_dir, 'HCP_900')
    return filename


def _fetch_hcp(data_dir=None,
               subjects=None,
               n_subjects=None,
               data_type='rest',
               sessions=None,
               on_disk=True,
               tasks=None):
    """Utility to download from s3"""
    data_dir = get_data_dirs(data_dir)[0]

    if data_type not in ['task', 'rest']:
        raise ValueError("Wrong data type. Expected 'rest' or 'task', got"
                         "%s" % data_type)

    if subjects is None:
        subjects = fetch_subject_list(data_dir=data_dir,
                                      n_subjects=n_subjects)
    elif isinstance(subjects, int):
        subjects = [subjects]
    if not set(fetch_subject_list(data_dir=
                                  data_dir)).issuperset(set(subjects)):
        raise ValueError('Wrong subjects.')

    res = []
    for subject in subjects:
        subject = str(subject)
        subject_dir = join(data_dir, subject, 'MNINonLinear', 'Results')
        if data_type is 'task':
            if tasks is None:
                sessions = TASK_LIST
            elif isinstance(tasks, str):
                sessions = [tasks]
            if not set(TASK_LIST).issuperset(set(sessions)):
                raise ValueError('Wrong tasks.')
        else:
            if sessions is None:
                sessions = [1, 2]
            elif isinstance(sessions, int):
                sessions = [sessions]
            if not set([1, 2]).issuperset(set(sessions)):
                raise ValueError('Wrong rest sessions.')
        for session in sessions:
            for direction in ['LR', 'RL']:
                if data_type is 'task':
                    task = session
                    root_filename = 'tfMRI_%s_%s' % (task, direction)
                else:
                    root_filename = 'rfMRI_REST%i_%s' % (session,
                                                         direction)
                root_dir = join(subject_dir, root_filename)
                filename = join(root_dir, root_filename + '.nii.gz')
                mask = join(root_dir, root_filename + '_SBRef.nii.gz')
                confounds = ['Movement_AbsoluteRMS_mean.txt',
                             'Movement_AbsoluteRMS.txt',
                             'Movement_Regressors_dt.txt',
                             'Movement_Regressors.txt',
                             'Movement_RelativeRMS_mean.txt',
                             'Movement_RelativeRMS.txt']
                res_dict = {'subject': subject, 'direction': direction,
                            'filename': filename, 'mask': mask}
                for i, confound in enumerate(confounds):
                    res_dict['confound_%i' % i] = join(root_dir, confound)
                if data_type is 'rest':
                    res_dict['session'] = session
                else:
                    res_dict['task'] = tasks
                    feat_file = join(root_dir,
                                     "tfMRI_%s_%s_hp200_s4_level1.fsf"
                                     % (task, direction))
                    res_dict['feat_file'] = feat_file
                    for i, ev in enumerate(EVS[task]):
                        res_dict['ev_%i' % i] = join(root_dir, 'EVs', ev)
                requested_on_disk = all(os.path.exists(file) for file
                                        in res_dict.values())
                if not on_disk or requested_on_disk:
                    res.append(res_dict)

    if res:
        res = pd.DataFrame(res)
        if data_type is 'rest':
            res.set_index(['subject', 'session', 'direction'],
                          inplace=True)
        else:
            res.set_index(['subject', 'task', 'direction'],
                          inplace=True)
    else:
        res = pd.DataFrame([])
    return res


def fetch_files(subject,
                data_type='rest',
                tasks=None,
                sessions=None,
                overwrite=False,
                mock=False,
                verbose=0):
    root_path = get_data_dirs()[0]
    aws_key, aws_secret, _, _ = get_credentials()
    s3_keys = _fetch_hcp(subjects=subject,
                         data_type=data_type,
                         tasks=tasks,
                         on_disk=False,
                         sessions=sessions)
    s3_keys = s3_keys.applymap(_convert_to_s3_target).values.ravel().tolist()
    params = dict(
        bucket='hcp-openaccess',
        out_path=root_path,
        aws_key=aws_key,
        aws_secret=aws_secret,
        overwrite=overwrite,
        prefix='HCP_900')
    if verbose > 0:
        if data_type == 'task':
            print('Downloading files for subject %s,'
                  ' tasks %s' % (subject, tasks))
        else:
            print('Downloading files for subject %s,'
                  ' session %s' % (subject, sessions))
    filenames = download_from_s3_bucket(key_list=s3_keys, mock=mock,
                                        verbose=verbose - 1, **params)
    for filename in filenames:
        name, ext = os.path.splitext(filename)
        if ext == '.gz':
            try:
                _ = nibabel.load(filename).get_shape()
            except:
                raise ConnectionError('Some files were corrupted. Rerun.')


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


def fetch_hcp_task(data_dir=None, release='HCP900',
                   output='nistats',
                   n_subjects=788,
                   level=2):
    """Nilearn like fetcher"""
    data_dir = get_data_dirs(data_dir)[0]

    tasks = [["WM", 1, "2BK_BODY"],
             ["WM", 2, "2BK_FACE"],
             ["WM", 3, "2BK_PLACE"],
             ["WM", 4, "2BK_TOOL"],
             ["WM", 5, "0BK_BODY"],
             ["WM", 6, "0BK_FACE"],
             ["WM", 7, "0BK_PLACE"],
             ["WM", 8, "0BK_TOOL"],
             ["WM", 9, "2BK"],
             ["WM", 10, "0BK"],
             ["WM", 11, "2BK-0BK"],
             ["WM", 12, "neg_2BK"],
             ["WM", 13, "neg_0BK"],
             ["WM", 14, "0BK-2BK"],
             ["WM", 15, "BODY"],
             ["WM", 16, "FACE"],
             ["WM", 17, "PLACE"],
             ["WM", 18, "TOOL"],
             ["WM", 19, "BODY-AVG"],
             ["WM", 20, "FACE-AVG"],
             ["WM", 21, "PLACE-AVG"],
             ["WM", 22, "TOOL-AVG"],
             ["WM", 23, "neg_BODY"],
             ["WM", 24, "neg_FACE"],
             ["WM", 25, "neg_PLACE"],
             ["WM", 26, "neg_TOOL"],
             ["WM", 27, "AVG-BODY"],
             ["WM", 28, "AVG-FACE"],
             ["WM", 29, "AVG-PLACE"],
             ["WM", 30, "AVG-TOOL"],
             ["GAMBLING", 1, "PUNISH"],
             ["GAMBLING", 2, "REWARD"],
             ["GAMBLING", 3, "PUNISH-REWARD"],
             ["GAMBLING", 4, "neg_PUNISH"],
             ["GAMBLING", 5, "neg_REWARD"],
             ["GAMBLING", 6, "REWARD-PUNISH"],
             ["MOTOR", 1, "CUE"],
             ["MOTOR", 2, "LF"],
             ["MOTOR", 3, "LH"],
             ["MOTOR", 4, "RF"],
             ["MOTOR", 5, "RH"],
             ["MOTOR", 6, "T"],
             ["MOTOR", 7, "AVG"],
             ["MOTOR", 8, "CUE-AVG"],
             ["MOTOR", 9, "LF-AVG"],
             ["MOTOR", 10, "LH-AVG"],
             ["MOTOR", 11, "RF-AVG"],
             ["MOTOR", 12, "RH-AVG"],
             ["MOTOR", 13, "T-AVG"],
             ["MOTOR", 14, "neg_CUE"],
             ["MOTOR", 15, "neg_LF"],
             ["MOTOR", 16, "neg_LH"],
             ["MOTOR", 17, "neg_RF"],
             ["MOTOR", 18, "neg_RH"],
             ["MOTOR", 19, "neg_T"],
             ["MOTOR", 20, "neg_AVG"],
             ["MOTOR", 21, "AVG-CUE"],
             ["MOTOR", 22, "AVG-LF"],
             ["MOTOR", 23, "AVG-LH"],
             ["MOTOR", 24, "AVG-RF"],
             ["MOTOR", 25, "AVG-RH"],
             ["MOTOR", 26, "AVG-T"],
             ["LANGUAGE", 1, "MATH"],
             ["LANGUAGE", 2, "STORY"],
             ["LANGUAGE", 3, "MATH-STORY"],
             ["LANGUAGE", 4, "STORY-MATH"],
             ["LANGUAGE", 5, "neg_MATH"],
             ["LANGUAGE", 6, "neg_STORY"],
             ["SOCIAL", 1, "RANDOM"],
             ["SOCIAL", 2, "TOM"],
             ["SOCIAL", 3, "RANDOM-TOM"],
             ["SOCIAL", 4, "neg_RANDOM"],
             ["SOCIAL", 5, "neg_TOM"],
             ["SOCIAL", 6, "TOM-RANDOM"],
             ["RELATIONAL", 1, "MATCH"],
             ["RELATIONAL", 2, "REL"],
             ["RELATIONAL", 3, "MATCH-REL"],
             ["RELATIONAL", 4, "REL-MATCH"],
             ["RELATIONAL", 5, "neg_MATCH"],
             ["RELATIONAL", 6, "neg_REL"],
             ["EMOTION", 1, "FACES"],
             ["EMOTION", 2, "SHAPES"],
             ["EMOTION", 3, "FACES-SHAPES"],
             ["EMOTION", 4, "neg_FACES"],
             ["EMOTION", 5, "neg_SHAPES"],
             ["EMOTION", 6, "SHAPES-FACES"]]

    res = []
    if output == 'fsl':
        source_dir = join(data_dir, release)
        if not os.path.exists(source_dir):
            raise ValueError('Please make sure that a directory %s can '
                             'be found '
                             'in the $MODL_DATA directory' % release)
        if release == 'HCP500':
            list_dir = sorted(glob.glob(join(source_dir,
                                             '*/*/MNINonLinear/Results')))
        else:
            list_dir = sorted(glob.glob(join(source_dir,
                                             '*/MNINonLinear/Results')))
        for dirpath in list_dir[:n_subjects]:
            dirpath_split = dirpath.split(os.sep)
            subject_id = dirpath_split[-3]
            subject_id = int(subject_id)

            for i, task in enumerate(tasks):
                task_name = task[0]
                contrast_idx = task[1]
                this_contrast = task[2]
                if level == 2:
                    filename = join(dirpath, "tfMRI_%s/tfMRI_%s_hp200_s4_"
                                             "level2vol.feat/cope%i.feat/"
                                             "stats/zstat1.nii.gz" % (
                                        task_name, task_name,
                                        contrast_idx))
                    if os.path.exists(filename):
                        res.append({'filename': filename,
                                    'subject': subject_id,
                                    'task': task_name,
                                    'contrast': this_contrast,
                                    'direction': 'level2'
                                    })
                else:
                    raise ValueError('Can only output level 2 images'
                                     'for release %s with output %s'
                                     % (release, output))
    else:
        source_dir = join(data_dir, 'HCP900', 'glm')
        if not os.path.exists(source_dir):
            warnings.warn('No GLM directory was found.')
            return pd.DataFrame()
        if level == 2:
            directions = ['level2']
        elif level == 1:
            directions = ['LR', 'RL']
        else:
            raise ValueError('Level should be 1 or 2, got %s' % level)
        subject_ids = os.listdir(source_dir)
        for subject_id in subject_ids[:n_subjects]:
            tasks = os.listdir(join(source_dir, subject_id))
            for task in tasks:
                for direction in directions:
                    z_dir = join(source_dir, subject_id, task, direction,
                                 'z_maps')
                    if os.path.exists(z_dir):
                        z_maps = os.listdir(z_dir)
                        for z_map in z_maps:
                            filename = join(z_dir, z_map)
                            this_contrast = z_map[2:-7]
                            if os.path.exists(filename):
                                res.append({'filename': filename,
                                            'subject': int(subject_id),
                                            'task': task,
                                            'contrast': this_contrast,
                                            'direction': direction
                                            })
    z_maps = pd.DataFrame(res)
    z_maps.set_index(['subject', 'task', 'contrast', 'direction'],
                     inplace=True)
    z_maps.sort_index(ascending=True, inplace=True)
    return z_maps


def fetch_hcp_mask(data_dir=None, url=None, resume=True):
    data_dir = get_data_dirs(data_dir)[0]
    source_dir = join(data_dir, 'HCP900')
    if not os.path.exists(source_dir):
        os.makedirs(data_dir)
    data_dir = join(source_dir, 'extra')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    if url is None:
        url = 'http://amensch.fr/data/HCP_own/mask_img.nii.gz'
    _fetch_file(url, data_dir, resume=resume)
    return join(data_dir, 'mask_img.nii.gz')


def _get_root_hcp_dir(data_dir=None):
    data_dir = get_data_dirs(data_dir)[0]
    root = join(data_dir, 'HCP900')
    if not os.path.exists(root):
        os.makedirs(root)
    return root


def fetch_hcp_rest(data_dir=None, n_subjects=788):
    """Nilearn like fetcher"""
    root = _get_root_hcp_dir(data_dir)
    res = []
    list_dir = sorted(
        glob.glob(join(root, '*/MNINonLinear/Results')))
    for dirpath in list_dir[:n_subjects]:
        dirpath_split = dirpath.split(os.sep)
        subject_id = dirpath_split[-3]
        subject_id = int(subject_id)

        for filename in os.listdir(dirpath):
            name, ext = os.path.splitext(filename)
            if name in ('rfMRI_REST1_RL', 'rfMRI_REST1_LR', 'rfMRI_REST2_RL',
                        'rfMRI_REST2_LR'):
                filename = join(dirpath, filename, filename + '.nii.gz')
                if os.path.exists(filename):
                    res.append(
                        {'filename': filename,
                         'confounds': None,
                         'subject': int(subject_id),
                         'direction': name[-2:],
                         'series': int(name[-4])
                         })

    rest = pd.DataFrame(res)
    rest.set_index(['subject', 'series', 'direction'], inplace=True)
    rest.sort_index(ascending=True, inplace=True)
    return rest


def fetch_hcp(data_dir=None, n_subjects=None, subjects=None):
    rest = _fetch_hcp(data_dir, data_type='rest',
                      n_subjects=n_subjects, subjects=subjects)
    task = fetch_hcp_task(data_dir, output='nistats', n_subjects=n_subjects)
    root = join(get_data_dirs(data_dir)[0], 'HCP900')
    mask = fetch_hcp_mask(data_dir)
    behavioral = fetch_behavioral_data(data_dir)
    behavioral = behavioral.loc[subjects, :]
    return Bunch(rest=rest, task=task, behavioral=behavioral, mask=mask,
                 root=root)
