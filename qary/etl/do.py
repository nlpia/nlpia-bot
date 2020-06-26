""" Digital Ocean Spaces (boto3) utilities


"""
import os
from pathlib import Path
import logging

import dotenv
import boto3

from qary.constants import DATA_DIR, BASE_DIR

log = logging.getLogger(__name__)
HOME = os.path.expanduser('~')

for p in (Path('.envs', 'digitalocean-nlpia.org', '.env.prod'), Path('.env')):
    for base_dir in (os.path.curdir, '~', BASE_DIR, DATA_DIR):
        Path(base_dir, p)
        if os.path.isfile(p):
            expanded_path = os.path.abspath(os.path.expandvars(p.expanduser()))
            try:
                dotenv.load_dotenv(expanded_path)
            except OSError:
                log.warning('Unable to load .env/* file with python-dotenv package.')
        else:
            dotenv.load_dotenv()


def connect(
        access_key_id=os.getenv('DO_ACCESS_KEY'),
        secret_access_key=os.getenv('DO_ACCESS_SECRET'),
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
