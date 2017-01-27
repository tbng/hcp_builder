from hcp_builder.glm import make_contrasts
from hcp_builder.dataset import fetch_hcp_single_subject

fetch_hcp_single_subject(100307, data_type='task', tasks='EMOTION')
make_contrasts(100307, tasks='EMOTION', backend='nistats')
