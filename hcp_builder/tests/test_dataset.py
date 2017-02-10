from hcp_builder.dataset import fetch_behavioral_data, fetch_subject_list, \
    fetch_hcp, _convert_to_s3_target, _fetch_hcp


def test_fetch_behavioral_data():
    res = fetch_behavioral_data()
    assert res.shape[0] >= 970
    assert res.shape[1] >= 549
    res = fetch_behavioral_data(restricted=True)
    assert res.shape[0] >= 970
    assert res.shape[1] >= 549


def test_fetch_subject_list():
    list = fetch_subject_list()
    assert len(list) >= 970
    list = fetch_subject_list(n_subjects=2)
    assert len(list) == 2


def test_fetch_hcp():
    res = fetch_hcp(on_disk=False)
    assert res.shape[0] >= 970
    res = _fetch_hcp(n_subjects=1)
    res = _fetch_hcp(n_subjects=1, data_type='rest')
    res = _fetch_hcp(on_disk=True, data_type='task')
    res = _fetch_hcp(on_disk=True, data_type='task', tasks='EMOTION')
    res = _fetch_hcp(on_disk=True, data_type='rest')
    res = _fetch_hcp(on_disk=False, data_type='rest')

def test_fetch_hcp():
    res = fetch_hcp()
    print(res)