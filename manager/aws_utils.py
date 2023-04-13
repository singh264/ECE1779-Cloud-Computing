import boto3
from datetime import datetime, timedelta
import json
import time
from typing import List, Any, Dict

from auto_scaling_policy import AutoScalingPolicy
from graph_data import GraphData
from worker import Worker
import mysql.connector

# AWS config
REGION_NAME = 'us-east-1'
IMAGE_ID = 'ami-005d3e61ce51b5a83'
KEY_NAME = 'key'
SECURITY_GROUPS = ['launch-wizard-3']
IAM_ROLE = 'arn:aws:iam::552776069481:instance-profile/ec2_s3'
ALB = 'arn:aws:elasticloadbalancing:us-east-1:552776069481:loadbalancer/app/ece1779-a2-alb/70ce7307f8b90bb9'
ALB_DNS = 'ece1779-a2-alb-1282510941.us-east-1.elb.amazonaws.com'
TARGET_GROUP = 'arn:aws:elasticloadbalancing:us-east-1:552776069481:targetgroup/user-app-target-group/c5a146d5484eb21b'
MANAGER_TAG_NAME = 'ece1779_assignment2_manager'
WORKER_POOL_LOWER_BOUND = 1
WORKER_POOL_UPPER_BOUND = 8

# Database config
DB_NAME     = 'uSLSzoVPTB'
DB_USERNAME = 'admin'
DB_PASSWORD = 'pass12345'
DB_HOST = 'database-1.cf18wqhdlvtt.us-east-1.rds.amazonaws.com'
username = 'user1'
password = '12345'



class AwsUtils:
    def __init__(self) -> None:
        self.__ec2 = boto3.client('ec2', REGION_NAME)
        self.__elb = boto3.client('elbv2', REGION_NAME)
        self.__cloudwatch = boto3.client('cloudwatch', REGION_NAME)

    def get_alb_dns_name(self) -> str:
        return ALB_DNS

    def get_cpu_utilization(self, instance_id: str) -> List[GraphData]:
        now = datetime.now()

        payload = self.__cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                },
            ],
            StartTime=now - timedelta(minutes=30),
            EndTime=now,
            Period=60,
            Statistics=['Maximum'],
            Unit='Percent')

        if 'Datapoints' in payload:
            data = [GraphData(timestamp=dp['Timestamp'], value=float(dp['Maximum'])) for dp in payload['Datapoints']]
 
            return sorted(data, key=lambda d: d.timestamp)
    
        return []

    def get_alb_workers_history(self) -> List[GraphData]:
        now = datetime.now()

        payload = self.__cloudwatch.get_metric_statistics(
            Namespace='AWS/ApplicationELB',
            MetricName='HealthyHostCount',
            Dimensions=[
                {
                    'Name': 'LoadBalancer',
                    'Value': ALB[ALB.find('app'):]
                },
                {
                    'Name': 'TargetGroup',
                    'Value': TARGET_GROUP[TARGET_GROUP.find('targetgroup'):]
                },
            ],
            StartTime=now - timedelta(minutes=30),
            EndTime=now,
            Period=60,
            Statistics=['Average'],
            Unit='Count')

        if 'Datapoints' in payload:
            data = [GraphData(timestamp=dp['Timestamp'], value=float(dp['Average'])) for dp in payload['Datapoints']]
 
            return sorted(data, key=lambda d: d.timestamp)
    
        return []

    def grow_worker_pool_size_by_1(self) -> str:
        new_worker = self.__launch_worker()
        new_worker_id = new_worker['InstanceId']
        print(f'New worker: {new_worker_id}')

        while not self.__is_new_worker_running(new_worker_id):
            print('New worker starting...')
            time.sleep(2)
        
        time.sleep(5)
        print('Adding new worker to target group...')
        payload = self.__register_worker_to_alb_target_group(new_worker_id)
        payload_status = payload['ResponseMetadata']['HTTPStatusCode']
        print(f'Result: {payload_status}')

        return payload_status

    def __launch_worker(self) -> Dict[str, Any]:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.run_instances
        payload = self.__ec2.run_instances(ImageId=IMAGE_ID,
                                            InstanceType='t2.micro',
                                            MinCount=1,
                                            MaxCount=1,
                                            SecurityGroups=SECURITY_GROUPS,
                                            TagSpecifications=[{
                                                'ResourceType': 'instance',
                                                'Tags': [
                                                    {
                                                        'Key': 'Name',
                                                        'Value': 'ece1779_assignment2_worker_auto'
                                                    }]
                                            }],
                                            Monitoring= {
                                                'Enabled': True 
                                            },
                                            IamInstanceProfile={
                                                'Arn': IAM_ROLE
                                            },
                                            Placement={
                                                'AvailabilityZone': 'us-east-1a'
                                            })
        
        # {'AmiLaunchIndex': 0, 'ImageId': 'ami-0c3e1eca3bc99701c', 'InstanceId': 'i-0bb35290e9d469590', 'InstanceType': 't2.micro', 'KeyName': 'ece1779', 'LaunchTime': datetime.datetime(2021, 3, 14, 0, 39, 58, tzinfo=tzlocal()), 'Monitoring': {'State': 'pending'}, 'Placement': {'AvailabilityZone': 'us-east-1a', 'GroupName': '', 'Tenancy': 'default'}, 'PrivateDnsName': 'ip-172-31-41-20.ec2.internal', 'PrivateIpAddress': '172.31.41.20', 'ProductCodes': [], 'PublicDnsName': '', 'State': {'Code': 0, 'Name': 'pending'}, 'StateTransitionReason': '', 'SubnetId': 'subnet-1bea7844', 'VpcId': 'vpc-1b7bd966', 'Architecture': 'x86_64', 'BlockDeviceMappings': [], 'ClientToken': '34cce611-79bb-4af9-bfb5-b5eaeb3d57ba', 'EbsOptimized': False, 'Hypervisor': 'xen', 'NetworkInterfaces': [{'Attachment': {'AttachTime': datetime.datetime(2021, 3, 14, 0, 39, 58, tzinfo=tzlocal()), 'AttachmentId': 'eni-attach-0780b4de68da3b824', 'DeleteOnTermination': True, 'DeviceIndex': 0, 'Status': 'attaching', 'NetworkCardIndex': 0}, 'Description': '', 'Groups': [{'GroupName': 'launch-wizard-6', 'GroupId': 'sg-0a6adaca32b100eaa'}], 'Ipv6Addresses': [], 'MacAddress': '0e:c3:56:39:af:a3', 'NetworkInterfaceId': 'eni-04252646ad621a78e', 'OwnerId': '187864651079', 'PrivateDnsName': 'ip-172-31-41-20.ec2.internal', 'PrivateIpAddress': '172.31.41.20', 'PrivateIpAddresses': [{'Primary': True, 'PrivateDnsName': 'ip-172-31-41-20.ec2.internal', 'PrivateIpAddress': '172.31.41.20'}], 'SourceDestCheck': True, 'Status': 'in-use', 'SubnetId': 'subnet-1bea7844', 'VpcId': 'vpc-1b7bd966', 'InterfaceType': 'interface'}], 'RootDeviceName': '/dev/sda1', 'RootDeviceType': 'ebs', 'SecurityGroups': [{'GroupName': 'launch-wizard-6', 'GroupId': 'sg-0a6adaca32b100eaa'}], 'SourceDestCheck': True, 'StateReason': {'Code': 'pending', 'Message': 'pending'}, 'Tags': [{'Key': 'Name', 'Value': 'ece1779_assignment2_worker_auto'}], 'VirtualizationType': 'hvm', 'CpuOptions': {'CoreCount': 1, 'ThreadsPerCore': 1}, 'CapacityReservationSpecification': {'CapacityReservationPreference': 'open'}, 'MetadataOptions': {'State': 'pending', 'HttpTokens': 'optional', 'HttpPutResponseHopLimit': 1, 'HttpEndpoint': 'enabled'}, 'EnclaveOptions': {'Enabled': False}}
        return payload['Instances'][0]


    def __is_new_worker_running(self, instance_id: str) -> bool:
        payload = self.__ec2.describe_instance_status(InstanceIds=[instance_id])
        states = payload['InstanceStatuses']
        state = '' if len(states) == 0 else states[0]['InstanceState']['Name']

        return state == 'running'

    def shrink_worker_pool_size_by_1(self) -> None:
        workers = self.get_alb_target_group_workers()
        for worker in workers:
            if worker.state == 'healthy':
                worker_id = worker.id
                print(f'Terminating worker: {worker_id}')
                self.__terminate_worker(worker_id)
                return worker_id

        return ''
    
    def get_alb_target_group_workers(self) -> List[Worker]:
        response = self.__elb.describe_target_health(TargetGroupArn=TARGET_GROUP)
        
        workers = []
        if 'TargetHealthDescriptions' in response:
            for target in response['TargetHealthDescriptions']:
                workers.append(Worker(id=target['Target']['Id'], 
                                        state=target['TargetHealth']['State']))

        return workers

    def __register_worker_to_alb_target_group(self, instance_id: str) -> Dict[str, Any]:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.register_targets
        payload = self.__elb.register_targets(
            TargetGroupArn = TARGET_GROUP,
            Targets=[
                {
                    'Id': instance_id,
                    'Port': 5000
                },
            ]
        )

        # {'ResponseMetadata': {'RequestId': '8dab638b-1447-4283-9efc-8dc9e2ac7f34', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '8dab638b-1447-4283-9efc-8dc9e2ac7f34', 'content-type': 'text/xml', 'content-length': '253', 'date': 'Sun, 14 Mar 2021 00:50:44 GMT'}, 'RetryAttempts': 0}}
        return payload

    def terminate_all_workers(self) -> None:
        workers = self.__get_workers()
        for worker in workers:
            if worker.state == 'running':
                print(f'Terminating: {worker}')
                self.__terminate_worker(worker.id)

    def __get_workers(self) -> List[Worker]:
        workers = []
        filters = [{'Name': 'tag:Name', 'Values': ['ece1779_assignment2_worker*']}]
        instances = self.__ec2.describe_instances(Filters=filters)
        reservations = instances['Reservations']
        for reservation in reservations:
            instances = reservation['Instances']
            if len(instances) > 0:
                for instance in instances:
                    workers.append(Worker(id=instance['InstanceId'], 
                                            state=instance['State']['Name'], 
                                            name=instance['Tags'][0]['Value']))

        return workers    

    def __terminate_worker(self, instance_id: str) -> Dict[str, Any]:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.terminate_instances
        print(f'Terminating: {instance_id}')
        payload = self.__ec2.terminate_instances(InstanceIds=[instance_id])

        # {'TerminatingInstances': [{'CurrentState': {'Code': 32, 'Name': 'shutting-down'}, 'InstanceId': 'i-0bb35290e9d469590', 'PreviousState': {'Code': 32, 'Name': 'shutting-down'}}], 'ResponseMetadata': {'RequestId': '80baad05-a58e-4dfc-92b2-82733ecdf3d3', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '80baad05-a58e-4dfc-92b2-82733ecdf3d3', 'cache-control': 'no-cache, no-store', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'content-type': 'text/xml;charset=UTF-8', 'transfer-encoding': 'chunked', 'vary': 'accept-encoding', 'date': 'Sun, 14 Mar 2021 02:43:08 GMT', 'server': 'AmazonEC2'}, 'RetryAttempts': 0}}
        return payload
    
    def stop_manager(self) -> None:
        workers = []
        filters = [{'Name': 'tag:Name', 'Values': [MANAGER_TAG_NAME]}]
        instances = self.__ec2.describe_instances(Filters=filters)
        reservations = instances['Reservations']
        for reservation in reservations:
            instances = reservation['Instances']
            if len(instances) > 0:
                for instance in instances:
                    workers.append(Worker(id=instance['InstanceId'], 
                                            state=instance['State']['Name'], 
                                            name=instance['Tags'][0]['Value']))

        for worker in workers:
            if worker.state == 'running':
                print(f'Stopping Manager: {worker}')
                self.__ec2.stop_instances(InstanceIds=[worker.id])
    
    def get_system_cpu_utilization(self) -> float:
        workers = self.get_alb_target_group_workers()
        workers_cpu_utilization = {w.id: self.__get_worker_cpu_utilization(w) for w in workers if w.state == 'healthy'}
        print(f'Workers cpu: {workers_cpu_utilization}')

        return (sum(workers_cpu_utilization.values()) / len(workers_cpu_utilization) 
                if workers_cpu_utilization 
                else -1)
    
    def __get_worker_cpu_utilization(self, worker: Worker) -> float:
        cpu_utilization = [cu.value for cu in self.get_cpu_utilization(worker.id)][-2:]
        cpu_utilization_snapshots_count = max(len(cpu_utilization), 1)       

        return sum(cpu_utilization) / cpu_utilization_snapshots_count
    
    def get_auto_scaling_policy(self) -> AutoScalingPolicy:
        cnx = mysql.connector.connect(user=DB_USERNAME,
                                   password=DB_PASSWORD,
                                   host=DB_HOST,
                                   database=DB_NAME)

        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM Scaler_config")
        configs = cursor.fetchall()

        return AutoScalingPolicy(
            growth_cpu_threshold=configs[0][2],
            shrinking_cpu_threshold=configs[0][1],
            expanding_ratio=configs[0][3],
            shrinking_ratio=configs[0][4],
            enable_auto=configs[0][0]
        )

    def get_worker_pool_lower_bound(self) -> int:
        return WORKER_POOL_LOWER_BOUND
    
    def get_worker_pool_upper_bound(self) -> int:
        return WORKER_POOL_UPPER_BOUND


if __name__ == '__main__':
    aws_utils = AwsUtils()

    if len(aws_utils.get_alb_target_group_workers()) == 0:
        aws_utils.grow_worker_pool_size_by_1()

    #print(aws_utils.get_alb_dns_name())
    #print(aws_utils.get_alb_target_group_workers())
    # print(aws_utils.get_alb_workers_history())
    #print(aws_utils.grow_worker_pool_size_by_1())
    # print(aws_utils.shrink_worker_pool_size_by_1())
    # print(aws_utils.get_cpu_utilization('i-09fd497631427ad8d'))
    #print(aws_utils.terminate_all_workers())
    #print(aws_utils.stop_manager())

    # print(aws_utils.__get_workers())
    # print(aws_utils.__is_new_worker_running('i-07762d120b8ea3584'))
    # print(aws_utils.__launch_worker())
    # print(aws_utils.__register_worker_to_alb_target_group('i-0f886bb118e7a9c01'))
    # print(aws_utils.__terminate_worker('i-0bb35290e9d469590'))
