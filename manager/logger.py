import logging

class Logger:
    def __init__(self, logfile: str) -> None:
        self.__disable_boto3_logs()

        logging.basicConfig(filename=logfile, 
                            filemode='a', 
                            format='%(asctime)s %(levelname)-8s %(message)s')
        
        logging.root.setLevel(logging.NOTSET)
    
    @staticmethod
    def __disable_boto3_logs():
        logging.getLogger('botocore.hooks').setLevel(logging.CRITICAL)
        logging.getLogger('botocore.utils').setLevel(logging.CRITICAL)
        logging.getLogger('botocore.credentials').setLevel(logging.CRITICAL)
        logging.getLogger('botocore.loaders').setLevel(logging.CRITICAL)
        logging.getLogger('botocore.endpoint').setLevel(logging.CRITICAL)
        logging.getLogger('botocore.client').setLevel(logging.CRITICAL)
        logging.getLogger('botocore.auth').setLevel(logging.CRITICAL)
        logging.getLogger('botocore.httpsession').setLevel(logging.CRITICAL)
        logging.getLogger('urllib3.connectionpool').setLevel(logging.CRITICAL)
        logging.getLogger('botocore.parsers').setLevel(logging.CRITICAL)
        logging.getLogger('botocore.retryhandler').setLevel(logging.CRITICAL)
    
    @staticmethod
    def log(message: str) -> None:
        print(message)
        logging.info(message)
