import requests
from typing import Dict


ROLE_NAME = 'a2-ec2-s3-role'


def get_access_key() -> Dict[str, str]:
    url = f'http://169.254.169.254/latest/meta-data/iam/security-credentials/{ROLE_NAME}'
    response = requests.get(url).json()

    return {
        'AccessKeyId': response['AccessKeyId'],
        'SecretAccessKey': response['SecretAccessKey'],
        'Token': response['Token']
    }


# if __name__ == '__main__':
#     print(get_access_key())