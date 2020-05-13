""" Utilities for working with an s3-compatible object store like Digital Ocean spaces

Thin wrapper for boto3: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
Configured to use a client accoring to DO docs: https://www.digitalocean.com/docs/spaces/resources/s3-sdk-examples/
"""
import os

import boto3

try:
    from qary.contansts import DO_ACCESS_KEY, DO_ACCESS_SECRET
except ImportError:
    DO_ACCESS_KEY = os.environ.get('DO_ACCESS_KEY')
    DO_ACCESS_SECRET = os.environ.get('DO_ACCESS_SECRET')


def gen_buckets():
    """ WIP: TODO: convert to client.list_buckets() """
    s3 = boto3.resource('s3')
    for bucket in s3.buckets.all():
        yield bucket.name


def connect(
        access_key_id=DO_ACCESS_KEY,
        secret_access_key=DO_ACCESS_SECRET,
        region_name='sfo2',
        spaces_name='tan',
        url=None):

    url = url or f'https://{spaces_name}.{region_name}.digitaloceanspaces.com'
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='sfo2',
                            endpoint_url=url,
                            aws_access_key_id=access_key_id,
                            aws_secret_access_key=secret_access_key)
    connect.client = client
    return client


def ls():
    # need to have setup boto.cfg
    s3 = boto3.resource('s3')
    b = s3.Bucket('some/path/')
    # return list(b.objects.all())
    return list(b.objects.filter(Prefix='some/path'))


def upload_file(
        source='scripts/docs/*.pkl',
        dest=None,
        access_key_id=os.getenv('DO_ACCESS_KEY'),
        secret_access_key=os.getenv('DO_ACCESS_SECRET'),
        region_name='sfo2',
        spaces_name='tan',
        url=None):

    client = connect(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        region_name=region_name,
        spaces_name=spaces_name,
        url=url)

    dest = dest or source
    retval = client.upload_file(source, spaces_name, dest)
    return retval
