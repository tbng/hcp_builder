from hcp_builder.tasks import make_contrasts
from hcp_builder.dataset import fetch_hcp_single_subject
from hcp_builder.utils import configure

configure()
fetch_hcp_single_subject(310621, data_type='task', tasks='EMOTION')
make_contrasts(310621, tasks='EMOTION')
