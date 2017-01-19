from hcp_builder.build import download, make_contrasts
from hcp_builder.files import get_subject_list
from hcp_builder.system import configure
from sklearn.externals.joblib import Parallel
from sklearn.externals.joblib import delayed


def download_and_make_contrasts(subject):
    try:
        download(subject)
        make_contrasts(subject)
    except:
        print('Failed for subject %s' % subject)

if __name__ == '__main__':
    configure()
    n_jobs = 24
    subjects = get_subject_list()[:24]
    Parallel(n_jobs=n_jobs)(delayed(
        download_and_make_contrasts)(subject) for subject in subjects)


