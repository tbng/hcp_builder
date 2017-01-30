import os
import traceback
from os.path import join

from hcp_builder.dataset import fetch_single_subject, get_subject_list
from sklearn.externals.joblib import Parallel
from sklearn.externals.joblib import delayed

from hcp_builder.utils import configure, get_data_dirs


def download_single(subject):
    data_dir = get_data_dirs()[0]
    error_dir = join(data_dir, 'rest', 'failures')
    try:
        fetch_single_subject(subject, data_type='rest')
    except:
        print('Failed downloading subject %s resting-state' % subject)
        traceback.print_exc()
        with open(join(error_dir, '%s' % subject), 'w+') as f:
            f.write('Failed downloading.')


def download():
    configure()
    data_dir = get_data_dirs()[0]
    error_dir = join(data_dir, 'rest', 'failures')
    if not os.path.exists(error_dir):
        os.makedirs(error_dir)
    n_jobs = 24
    subjects = get_subject_list()
    Parallel(n_jobs=n_jobs, verbose=10)(delayed(
        download)(subject) for subject in subjects)


