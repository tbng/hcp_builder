from hcp_builder.dataset import fetch_hcp_single_subject, get_subject_list
from sklearn.externals.joblib import Parallel
from sklearn.externals.joblib import delayed

from hcp_builder.tasks import make_contrasts
from hcp_builder.utils import configure


def download_and_make_contrasts(subject):
    try:
        fetch_hcp_single_subject(subject, data_type='task')
        with open('%s_task_download_done' % subject, 'w+') as f:
            f.write('Done downloading.')
    except:
        with open('%s_task_download_failed' % subject, 'w+') as f:
            f.write('Failed downloading.')
    try:
        make_contrasts(subject)
        with open('%s_contrasts_done' % subject, 'w+') as f:
            f.write('Done making constrats.')
    except:
        with open('%s_contrasts_failed' % subject, 'w+') as f:
            f.write('Failed making constrats.')


if __name__ == '__main__':
    configure()
    n_jobs = 24
    subjects = get_subject_list()
    Parallel(n_jobs=n_jobs, verbose=10)(delayed(
        download_and_make_contrasts)(subject) for subject in subjects)


