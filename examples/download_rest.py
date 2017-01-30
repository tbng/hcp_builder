import os
import traceback
from os.path import join

from hcp_builder.dataset import download_single_subject, fetch_subject_list
from sklearn.externals.joblib import Parallel, delayed

from hcp_builder.dataset import get_data_dirs


def download_single(subject):
    data_dir = get_data_dirs()[0]
    error_dir = join(data_dir, 'failures')
    try:
        download_single_subject(subject, data_type='rest')
    except:
        print('Failed downloading subject %s resting-state' % subject)
        traceback.print_exc()
        with open(join(error_dir, 'rest_%s' % subject), 'w+') as f:
            f.write('Failed downloading.')


def download():
    data_dir = get_data_dirs()[0]
    error_dir = join(data_dir, 'failures')
    if not os.path.exists(error_dir):
        os.makedirs(error_dir)
    n_jobs = 24
    subjects = fetch_subject_list()
    Parallel(n_jobs=n_jobs, verbose=10)(delayed(
        download)(subject) for subject in subjects)


