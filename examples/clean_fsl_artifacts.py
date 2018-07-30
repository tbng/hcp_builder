from hcp_builder.dataset import fetch_subject_list
from hcp_builder.utils.fsl import clean_artifacts

subject_list = fetch_subject_list()
total = len(subject_list)
for i, subject in enumerate(subject_list):
    print('Clearning subject %s, %i / %i'% (subject, i, total))
    clean_artifacts(subject)
