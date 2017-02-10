import os
import traceback
from os.path import join

from hcp_builder.dataset import fetch_files, fetch_subject_list
from sklearn.externals.joblib import Parallel, delayed

from hcp_builder.dataset import get_data_dirs


def download_single(subject, verbose=0):
    data_dir = get_data_dirs()[0]
    error_dir = join(data_dir, 'failures')
    try:
        fetch_files(subject, data_type='rest', overwrite=True, verbose=verbose)
    except:
        print('Failed downloading subject %s resting-state' % subject)
        traceback.print_exc()
        with open(join(error_dir, 'rest_%s' % subject), 'w+') as f:
            f.write('Failed downloading.')


def restart_failed():
    restarts = []
    n_jobs = 16
    names = ['failure_173940_1_RL',
             'failure_285345_2_LR', 'failure_820745_1_RL',
             'failure_176037_2_RL', 'failure_330324_1_RL']

    for name in names:
        _, subject, session, _ = name.split('_')
        restarts.append((subject, session))
    Parallel(n_jobs=n_jobs, verbose=10)(delayed(
        fetch_files)(int(subject), data_type='rest',
                     rest_sessions=int(session), verbose=1,
                     overwrite=True) for subject, session
                                        in restarts)


def download():
    data_dir = get_data_dirs()[0]
    error_dir = join(data_dir, 'failures')
    if not os.path.exists(error_dir):
        os.makedirs(error_dir)
    n_jobs = 24
    subjects = fetch_subject_list()
    Parallel(n_jobs=n_jobs, verbose=10)(delayed(
        download_single)(subject) for subject in subjects)


def download_subset():
    data_dir = get_data_dirs()[0]
    error_dir = join(data_dir, 'failures')
    if not os.path.exists(error_dir):
        os.makedirs(error_dir)
    n_jobs = 4
    subjects = fetch_subject_list()[:4]
    Parallel(n_jobs=n_jobs, verbose=10)(delayed(
        download_single)(subject, verbose=2) for subject in subjects)

if __name__ == '__main__':
    download()
