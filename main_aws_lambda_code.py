#import boto3 AWS python3 library
import boto3
#import date and time python3 library
import datetime

#Define the account information from the AWS Account
#Note befor using this script you must be set aws account id then use it 
AWS_REGION='eu-central-1'
Owner_Id = 'xxxxxxxxxxxx'
instances_dict={}
EC2_RESOURCE = boto3.resource('ec2',region_name=AWS_REGION)

def get_instance_volumes(INSTANCE_ID):
    volumes=[]
    instance = EC2_RESOURCE.Instance(INSTANCE_ID)
    device_mappings = instance.block_device_mappings
    for device in device_mappings:
        volumes.append(device['Ebs']['VolumeId'])
    return volumes

def create_snapshot(INSTANCE_Name,Volumes_List):
    counter=0
    snapshot_date= str(datetime.date.today())
    for volume_id in Volumes_List:
        counter += 1 
        Tag_name = str('created snapshot of '+ str(INSTANCE_Name) \
        + ' Disk%d in '+snapshot_date) % (counter)
        response = EC2_RESOURCE.create_snapshot(
        VolumeId=volume_id,
        TagSpecifications=[
        {
            'ResourceType': 'snapshot',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': Tag_name
                }
            ]
        }
        ]
        
    )
    
def delete_old_snapshot(INSTANCE_Name,Volumes_List):
    EC2_RESOURCE = boto3.resource('ec2',region_name=AWS_REGION)
    STS_CLIENT = boto3.client('sts')
    CURRENT_ACCOUNT_ID = STS_CLIENT.get_caller_identity()['Account']
    for volume in Volumes_List:
        snapshots = EC2_RESOURCE.snapshots.filter(
        Filters=[
            {
                'Name': 'volume-id',
                'Values': [
                    volume
                    ]
            }
        ]
    )
    for snapshot in snapshots:
        snapshot_delete = EC2_RESOURCE.Snapshot(snapshot.id)
        snapshot_delete.delete()
    return 0

def main_defination(event , context):
    instances = EC2_RESOURCE.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    
    #Create List of running instances 
    for instance in instances:
        instances_dict[instance.tags[0]['Value']]= instance.id
    
    
    #create snapshot from the every instance. first search which for every instance how many disk added to 
    #ec2 instances, then after that delete snapshot exists , then create a snapshot from the list of runnnig volumes
    device_mappings = instance.block_device_mappings
    for key,value in instances_dict.items():
        instance_name = key
        volumes_list=get_instance_volumes(value)
        delete_old_snapshot(instance_name,volumes_list)
        create_snapshot(instance_name,volumes_list)
    return 0
if __name__ == '__main__':
    main_defination()
    
