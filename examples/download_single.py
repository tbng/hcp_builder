import time
from hcp_builder.glm import run_glm
from hcp_builder.dataset import fetch_files


def download_single():
    t0 = time.time()
    fetch_files(100206, data_type='task', tasks='EMOTION', verbose=10,
                overwrite=True)
    download_time = time.time() - t0
    t0 = time.time()
    run_glm(100206, backend='nistats', tasks='EMOTION')
    glm_time = time.time() - t0
    print('Download time %.2f, GLM time %.2f' % (download_time, glm_time))

if __name__ == '__main__':
    download_single()