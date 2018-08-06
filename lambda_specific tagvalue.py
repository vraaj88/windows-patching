# This script will search for all EC2 instances having specific tag key-values(you can find around 28 tags below in the code) appeared on each instance or not. 
# We loop through each instance for fixed tag key-value and if we found that value doesn't appeared on that key tag, then it will create the missed and pre-defined tag key-value for that instance.
# Also, it will not do override if there is tag key-value exists.

import boto3

company_tags = ['Appl_Or_Function_Code', 'Backup', 'Biz_Departments', 'Blue_Green', 'ContactPhone', 'Contact_email', 'Cost_Center', 'Created_By', 'Domain_Name', 'Environment', 'Expiration_Date', 'Host_Name', 'MSP_Managed', 'Name', 'OS', 'Resource_Owner', 'Retention', 'Schedule_Action', 'Schedule_Time', 'Sec_Crypto', 'Sec_DataTypes', 'Sec_Data_Class', 'Sec_Forensics', 'Sec_Retention', 'Sec_Std', 'Sec_Zone', 'Team_Supporting_Application', 'Tech_Owner_Dept']

key_value = {'Appl_Or_Function_Code':'CITRIX',
'Backup':'',
'Biz_Departments':'Servicing-Collections-Sales',
'Blue_Green':'',
'ContactPhone':'',
'Contact_email':'',
'Cost_Center':'44599',
'Created_By':'',
'Domain_Name':'',
'Environment':'',
'Expiration_Date':'',
'Host_Name':'',
'MSP_Managed':'',
'Name':'',
'OS':'',
'Resource_Owner':'e57635',
'Retention':'',
'Schedule_Action':'',
'Schedule_Time':'',
'Sec_Crypto':'',
'Sec_DataTypes':'',
'Sec_Data_Class':'',
'Sec_Forensics':'',
'Sec_Retention':'',
'Sec_Std':'',
'Sec_Zone':'',
'Team_Supporting_Application':'ECCaM@salliemae.com',
'Tech_Owner_Dept':'ECCaM@salliemae.com',
}

def main(event, context):
    ec2client = boto3.client('ec2')
    response = ec2client.describe_instances(Filters=[
        {
            'Name': 'instance-state-name',
            'Values': [
                'running',
            ]
        },
    ])

    for r in response["Reservations"]:
        for inst in r["Instances"]:
            inst_id = inst['InstanceId']
            #print "----------------------------------------------"
            #print "Checking Instance - \"%s\"" %(inst["InstanceId"])
            #print "----------------------------------------------"
            get_tag_list(inst, ec2client)
            if inst['InstanceType'] == 't2.xlarge':
                ec2client.create_tags(
                    Resources=[inst_id],
                    Tags=[
                        {
                            'Key': 'Appl_Or_Function_Code',
                            'Value': 'Cloud VDI'
                        }
                    ]
                )

def get_tag_list(instance, ec2client):
    tag_list = []

    try:
        tag_list = instance["Tags"]
        print "EC2 instance having some tags: Validating..."
    except:
        print "EC2 instance having No Tags: Attaching All"

    tag_key_list = []
    empty_key_list = []

    for tag in tag_list:
        t = tag["Key"]
        tag_key_list.append(t)

        if tag["Value"] == '':
            empty_key_list.append(t)

    for tag_key in company_tags:
        if tag_key in tag_key_list:
            if tag_key in empty_key_list:
                if key_value[tag_key] != '':
                    update_tag(instance, tag_key, ec2client)
        else:
            create_tag(instance, tag_key, ec2client)
    print "Validated"

def update_tag(instance, tag_key, ec2client):
    instance_id = instance["InstanceId"]
    tag_value = key_value[tag_key]

    response = ec2client.delete_tags(
        DryRun=False,
        Resources=[
            instance_id,
        ],
        Tags=[
            {
                'Key': tag_key,
                'Value': ''
            },
        ]
    )

    response = ec2client.create_tags(
        DryRun=False,
        Resources=[
            instance_id,
        ],
        Tags=[
            {
                'Key': tag_key,
                'Value': tag_value
            },
        ]
    )


def create_tag(instance, tag_key, ec2client):
    instance_id = instance["InstanceId"]

    ec2client.create_tags(
        Resources=[instance_id],
        Tags=[
            {
                'Key': tag_key,
                'Value': key_value[tag_key]
            }
        ]
    )
