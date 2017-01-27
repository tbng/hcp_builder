import time
from hcp_builder.glm import run_glm
from hcp_builder.dataset import fetch_single_subject

from modl.utils.nifti import monkey_patch_nifti_image

monkey_patch_nifti_image()
t0 = time.time()
fetch_single_subject(100307, data_type='task', tasks='EMOTION')
download_time = time.time() - t0
t0 = time.time()
run_glm(100307, backend='nistats', tasks='EMOTION')
glm_time = time.time() - t0
print('Download time %.2f, GLM time %.2f' % (download_time, glm_time))
