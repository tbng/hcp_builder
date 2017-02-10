# Author: Denis A. Engemann <denis.engemann@gmail.com>
# Adapted by Arthur Mensch
# License: BSD (3-clause)

# XXX This is much too complicated

import glob
import os
import os.path as op
import sys
import time
import traceback
from socket import gaierror as GaiError
from ssl import SSLError

import boto
import boto.s3.connection
from boto.s3.key import Key


def update_s3_file_tracking(df_unrel, key, secret, extensions=('.fif',),
                            bucket='mne-hcp-data'):

    # 1 get all files in bucket

    file_map = dict()
    for subject in df_unrel[df_unrel['unrelated_rs_source']].Subject.values:
        file_map[subject] = s3_glob(
            bucket=bucket,
            aws_key=key,
            aws_secret=secret,
            prefix='',
            key_pattern='*/%s/*' % subject)

    # 2 create unique interpretabler file names for csv columns and set them

    file_keys = {
        '{subject}' + op.split(val)[-1][6:] if val.endswith('trans.fif') else
        op.split(val)[-1] for val in sum(list(file_map.values()), []) if
        any(val.endswith(ee) for ee in extensions)}

    for key in file_keys:
        df_unrel[key] = False

    ###########################################################################
    # 2 create unique interpretable file names for csv columns and set them

    for subject, files in file_map.items():
        for this_file in files:
            if any(not this_file.endswith(ee) for ee in extensions):
                continue
            file_key = op.split(this_file)[-1]
            if file_key.endswith('trans.fif'):
                file_key = '{subject}' + file_key[6:]
            df_unrel.loc[df_unrel.Subject == subject, file_key] = True

    return df_unrel, file_keys


def download_from_s3(aws_key, aws_secret, bucket, fname,
                     key, dry_run=False,
                     host='s3.amazonaws.com'):
    """Download file from bucket
    """
    switch_validation = False
    if host is not None and not isinstance(
            host, boto.s3.connection.NoHostProvided):
        if 'eu-central' in host:
            switch_validation = True
            os.environ['S3_USE_SIGV4'] = 'True'
    com = boto.connect_s3(aws_key, aws_secret, host=host)
    bucket = com.get_bucket(bucket, validate=False)
    my_key = Key(bucket)
    my_key.key = key
    out = False
    if my_key.exists():
        if not dry_run:
            s3fid = bucket.get_key(key)
            s3fid.get_contents_to_filename(fname)
            out = True
        else:
            return True
    else:
        print('could not get %s : it does not exist' % key)
        out = False
    if switch_validation:
        del os.environ['S3_USE_SIGV4']
    return out


def s3_glob(key_pattern, bucket, prefix,
            aws_key, aws_secret,
            host='s3.amazonaws.com'):
    import boto
    switch_validation = False
    if host is not None and not isinstance(
            host, boto.s3.connection.NoHostProvided):
        if 'eu-central' in host:
            switch_validation = True
            os.environ['S3_USE_SIGV4'] = 'True'

    com = boto.connect_s3(aws_key, aws_secret, host=host)
    bucket = com.get_bucket(bucket, validate=False)
    file_names = [key.name for key in bucket.list(prefix=prefix)]
    if switch_validation:
        del os.environ['S3_USE_SIGV4']
    return [name for name in file_names if
            glob.fnmatch.fnmatch(name, key_pattern)]


def download_from_s3_bucket(bucket, out_path, key_list,
                            aws_key,
                            aws_secret,
                            prefix='', overwrite=False,
                            mock=False,
                            verbose=0,
                            **kwargs):
    n_retry = 3
    start_time = time.time()
    files_written = list()
    for key in key_list:
        if '?' in key or '*' in key:
            key = s3_glob(key_pattern=key,
                          bucket=bucket,
                          prefix=prefix,
                          aws_key=aws_key,
                          aws_secret=aws_secret)
        else:
            key = [key]
        for this_key in key:
            if prefix:
                key_path = this_key.split(prefix)[1]
            else:
                key_path = this_key
            fname = op.join(out_path, key_path.lstrip('/'))
            files_written.append(fname)
            if not (op.exists(op.split(fname)[0]) or
                    op.islink(op.split(fname)[0])):
                os.makedirs(op.split(fname)[0])
            if not (op.exists(fname) or op.islink(fname)) or overwrite:
                if verbose > 0:
                    print('Downloading %s from %s' % (fname, bucket))
                for ii_try in range(n_retry):
                    try:
                        download_from_s3(
                            aws_key=aws_key,
                            aws_secret=aws_secret,
                            fname=fname,
                            dry_run=mock,
                            bucket=bucket, key=this_key, **kwargs)
                        break
                    except (SSLError, GaiError):
                        # Actually fail on last pass through the loop
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        if ii_try == 2:
                            msg = '\n'.join(
                                traceback.format_exception(
                                    exc_type, exc_value, exc_traceback))
                            error_fname = list(op.splitext(fname))
                            error_fname.insert(1, '-ERROR')
                            error_fname = ''.join(error_fname)
                            with open(error_fname, 'w') as fid:
                                fid.write(msg)
            else:
                if verbose > 0:
                    print("%s exists. Doing nothing" % fname)
    elapsed_time = time.time() - start_time
    if verbose > 0:
        print('Elapsed time downloading {} from s3 {}'.format(
            bucket,
            time.strftime('%H:%M:%S', time.gmtime(elapsed_time))))
    return files_written


def delete_from_s3(aws_key, aws_secret, bucket,
                   key, dry_run=False,
                   host='s3.amazonaws.com'):
    """Download file from bucket
    """
    switch_validation = False
    if host is not None and not isinstance(
            host, boto.s3.connection.NoHostProvided):
        if 'eu-central' in host:
            switch_validation = True
            os.environ['S3_USE_SIGV4'] = 'True'

    com = boto.connect_s3(aws_key, aws_secret, host=host)
    bucket = com.get_bucket(bucket, validate=False)
    my_key = Key(bucket)
    my_key.key = key
    out = False
    if my_key.exists():
        if not dry_run:
            my_key.delete()
        else:
            out = True
    else:
        print('could not delete %s : it does not exist' % key)
        out = False
    if switch_validation:
        del os.environ['S3_USE_SIGV4']
    return out


def delete_from_s3_bucket(bucket, key_list,
                          aws_key,
                          aws_secret,
                          prefix='', dry_run=False):
    start_time = time.time()
    files_deleted = list()
    for key in key_list:
        if '?' in key or '*' in key:
            key = s3_glob(key_pattern=key,
                          bucket=bucket,
                          prefix=prefix,
                          aws_key=aws_key,
                          aws_secret=aws_secret)
        else:
            key = [key]
        for this_key in key:
            done = delete_from_s3(
                key=this_key,
                bucket=bucket,
                dry_run=dry_run,
                aws_key=aws_key,
                aws_secret=aws_secret)
            if done:
                files_deleted.append(this_key)
    elapsed_time = time.time() - start_time
    print('Elapsed time downloading {} from s3 {}'.format(
        bucket,
        time.strftime('%H:%M:%S', time.gmtime(elapsed_time))))
    return files_deleted


def list_s3(aws_key, aws_secret, bucket, key, dry_run=False,
            host='s3.amazonaws.com'):
    """Download file from bucket
    """
    switch_validation = False
    if host is not None and not isinstance(
            host, boto.s3.connection.NoHostProvided):
        if 'eu-central' in host:
            switch_validation = True
            os.environ['S3_USE_SIGV4'] = 'True'

    com = boto.connect_s3(aws_key, aws_secret, host=host)
    bucket = com.get_bucket(bucket, validate=False)
    my_key = Key(bucket)
    my_key.key = key
    out = False
    if my_key.exists():
        out = True
    else:
        print('could not find %s : it does not exist' % key)
        out = False
    if switch_validation:
        del os.environ['S3_USE_SIGV4']
    return out


def list_s3_bucket(bucket, key_list, aws_key, aws_secret,
                   prefix='', dry_run=False):
    start_time = time.time()
    files_listed = list()
    for key in key_list:
        if '?' in key or '*' in key:
            key = s3_glob(key_pattern=key,
                          bucket=bucket,
                          prefix=prefix,
                          aws_key=aws_key,
                          aws_secret=aws_secret)
        else:
            key = [key]
        for this_key in key:
            done = list_s3(
                key=this_key,
                bucket=bucket,
                dry_run=dry_run,
                aws_key=aws_key,
                aws_secret=aws_secret)
            if done:
                files_listed.append(this_key)
    elapsed_time = time.time() - start_time
    print('Elapsed time downloading {} from s3 {}'.format(
        bucket,
        time.strftime('%H:%M:%S', time.gmtime(elapsed_time))))
    return files_listed


def upload_to_s3(aws_key, aws_secret, fname, bucket, key,
                 callback=None, md5=None, reduced_redundancy=False,
                 content_type=None, host='s3.amazonaws.com'):
    """
    XXX copied from somewher on stackoverflow. Hope to find it again.

    Uploads the given file to the AWS S3
    bucket and key specified.

    callback is a function of the form:

    def callback(complete, total)

    The callback should accept two integer parameters,
    the first representing the number of bytes that
    have been successfully transmitted to S3 and the
    second representing the size of the to be transmitted
    object.

    Returns boolean indicating success/failure of upload.
    """
    switch_validation = False
    if host is not None:
        if 'eu-central' in host:
            switch_validation = True
            os.environ['S3_USE_SIGV4'] = 'True'
    # if 's3' in boto.config.sections():
    #     boto.config.remove_section('s3')
    com = boto.connect_s3(aws_access_key_id=aws_key,
                          aws_secret_access_key=aws_secret,
                          host=host)
    bucket = com.get_bucket(bucket, validate=True)
    s3_key = Key(bucket)
    s3_key.key = key
    if content_type:
        s3_key.set_metadata('Content-Type', content_type)

    with open(fname) as fid:
        try:
            size = os.fstat(fname.fileno()).st_size
        except:
            # Not all file objects implement fileno(),
            # so we fall back on this
            fid.seek(0, os.SEEK_END)
            size = fid.tell()
        sent = s3_key.set_contents_from_file(
            fid, cb=callback, md5=md5, reduced_redundancy=reduced_redundancy,
            rewind=True)
        # Rewind for later use
        fid.seek(0)

    if switch_validation:
        del os.environ['S3_USE_SIGV4']

    if sent == size:
        return True
    return False