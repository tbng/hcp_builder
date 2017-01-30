Download HCP rest + task data from the S3 repo, and runs the nistats/FSL GLM on time series.

# Usage

```python
python setup.py install
cd examples
python download_tasks.py
python download_rest.py
```

# Environment variables
```
HCP_data: root of the HCP dataset, where it will be downloaded
HCP_AWS_KEY: for S3 bucket access
HCP_AWS_SECRET_KEY: for S3 bucket access
CDB_USERNAME: for behavioral access
CDB_PASSWORD: for behavioral_access
```

# TODO:
- write tests
- automate restart when failures
- download non-completed subjects
- write functions to copy resources in the HCP_DATA dir
- move nilearn like fetchers from modl into the package
- merge downloaders and fetchers as in nilearn (?)