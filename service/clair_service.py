import datetime
import logging
import asyncio
import time
import requests
import json

import diskcache
from urllib3.exceptions import HTTPError
from DTO.VulnerabilityQueue import VulnerabilityQueue
import service.image_service as manage

auth_url = 'https://auth.docker.io/token'
clair_indexer_url = 'http://localhost:6060/indexer/api/v1/index_report'
clair_matcher_url = 'http://localhost:6060/matcher/api/v1/vulnerability_report/'

def clair_post_manifest(layers: list, registry_url: str, reservation: VulnerabilityQueue):
    token = get_auth_token(reservation)
    header = { 'Authorization': [ f'Bearer {token}' ] }
    digest = reservation.digest
    repo = reservation.repo_name

    _layers = []
    for layer in layers:
        layer_digest = layer['digest']
        layer_uri = 'http://' + registry_url
        layer_uri += f'/v2/{repo}/blobs/{layer_digest}'

        _layers.append({'hash': layer_digest, 'uri': layer_uri, 'headers': header})

    _manifest = {
                    'hash': digest,
                    'layers': _layers
                }

    response = requests.post(clair_indexer_url, json=_manifest)
    if response.status_code >= 500:
        raise HTTPError(f"clair_post_manifest: {response.content}")
    return response.status_code

def clair_get_layers(reservation: VulnerabilityQueue):
    token = 'Bearer ' + get_auth_token(reservation)
    header = {'Authorization': token}
    digest = reservation.digest
    repo = reservation.repo_name

    manifest_url = 'http://' + reservation.registry_url + '/v2/{}/manifests/{}'

    request_url = manifest_url.format(repo, digest)
    response = requests.get(request_url, headers=header)
    parsed_res = json.loads(response.content)

    if 'layers' in parsed_res:
        return parsed_res['layers']

    elif 'manifests' in parsed_res:
        # It must have 'layers', not 'manifests'
        # see 'validate_digest' function
        raise Exception('Cannot get manifest: digest not validated.\n' + parsed_res)

    else:
        raise Exception('Cannot get manifest: Unexpected Response.\n' + parsed_res)

def validate_digest(reservation: VulnerabilityQueue):
    if reservation.is_local_image:
        validate_local_digest(reservation)
        return reservation.digest

    repo = reservation.repo_name
    digest = reservation.digest
    token = 'Bearer ' + get_auth_token(reservation)
    header = {'Authorization': token}

    manifest_url = 'http://' + reservation.registry_url + '/v2/{}/manifests/{}'
    request_url = manifest_url.format(repo, digest)
    response = requests.get(request_url, headers=header)
    if response.status_code >= 400:
        reservation.registry_url = 'localhost:5000/'
        reservation.is_local_image = True
        validate_local_digest(reservation)
        return reservation.digest

    parsed_res = json.loads(response.content)
    if 'manifests' in parsed_res:
        for manifest in parsed_res['manifests']:
            # For this reason, arm is not supported currently.
            if manifest['platform']['architecture'] == 'amd64':
                reservation.digest = manifest['digest']
                return reservation.digest

    elif 'layers' in parsed_res:
        return reservation.digest

    else:
        raise Exception('Cannot validate digest: Unexpected response' + parsed_res)

def validate_local_digest(reservation: VulnerabilityQueue):
    # Image Tagging: tag should not include url scheme(e.g., http://)
    local_image = manage.get_image(reservation.imageId)
    local_image.tag(reservation.registry_url + reservation.repo_name)
    manage.push_image(reservation.registry_url + reservation.repo_name)

    local_image = manage.get_image(reservation.imageId)
    reservation.digest = local_image.attrs['RepoDigests'][0].split('@')[1]

    return reservation.digest

def clair_get_report(digest: str):
    response = requests.get(clair_matcher_url + digest)
    if response.status_code == 401:
        error_report = 'clair_get_report: 401 Unauthorized\n'
        error_report += json.loads(response.content)
        raise HTTPError(error_report)
    if response.status_code >= 500:
        error_report = 'clair_get_report: Database or clair server has error; it might be because it is busy.'
        error_report += json.loads(response.content)
        raise HTTPError(error_report)
    return json.loads(response.content)['vulnerabilities']

def get_auth_token(rsv: VulnerabilityQueue)->str:
    # request for token of 'ch1keen/pwnable': OK
    # request for token of 'library/ruby': OK
    # request for token of 'ruby': OK but won't work
    auth_token = diskcache.Cache(directory="./cache/auth_token")
    repository = rsv.repo_name

    token = auth_token.get(repository)
    if token is None:
        params = {
                    'service': 'registry.docker.io',
                    'scope': f'repository:{repository}:pull',
                 }
        response = requests.get(auth_url, params = params)

        if response.status_code == 200:
            token_json = json.loads(response.content)

            auth_token.set(repository, token_json['token'], expire=token_json['expires_in'])
            return token_json['token']

        else:
            logging.error("Cannot retrieve a token: Received %d" % response.status_code)
            logging.error(json.loads(response.content))

            raise HTTPError('get_auth_token: Cannot retrieve the token.')

    else:
        return str(token)


if __name__ == '__main__':
    # Simple CLI integration goes here:
    pass
