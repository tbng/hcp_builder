from hcp_builder.dataset import fetch_hcp_single_subject, get_subject_list
from sklearn.externals.joblib import Parallel
from sklearn.externals.joblib import delayed

from hcp_builder.utils import configure


def download(subject):
    try:
        fetch_hcp_single_subject(subject, data_type='rest')
        with open('%s_rest_download_done' % subject, 'w+') as f:
            f.write('Done downloading.')
    except:
        with open('%s_rest_download_failed' % subject, 'w+') as f:
            f.write('Failed downloading.')

if __name__ == '__main__':
    configure()
    n_jobs = 24
    subjects = get_subject_list()
    Parallel(n_jobs=n_jobs, verbose=10)(delayed(
        download)(subject) for subject in subjects)


