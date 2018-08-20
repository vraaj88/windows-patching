# AWS resource Tag Report which collects all tags and its values into one CSV file and stores in S3bucket.
#
#
# Gathering the tag report of all EC2, AMI, EBSvolume, EBSSnapshot, SG, ENI, S3bucket. 
# Gathering the tag report of all VPC, Subnets, Route Tables, Internet Gateways, Network ACLs, VPC Peering, DHCP Option Sets, Customer Gateways, VPG and VPN connections. 
# Additionally, configured and implemented the Email notification with attached CSV file to the cloud engineering team.
#
# Below script developed using python 2.7 in AWS Lambda function. 
# Vishnu Bandemneni
# 07/03/2018

import boto3, json, os, sys
from time import gmtime, strftime

#Email Packages
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

account_id = boto3.client('sts').get_caller_identity().get('Account')
#account_name = boto3.client('organizations').describe_account(AccountId=account_id).get('Account').get('Name')

ses = boto3.client('ses')
s3_client = boto3.client('s3')

to_emails = []
COMMASPACE = ', '

date = strftime("%Y-%m-%d", gmtime())
s3 = boto3.resource('s3','us-east-1')

#file_name = 'report_'+account_name+'_'+date+'.csv'
file_name = 'report_'+account_id+'_'+date+'.csv'
os.system('touch /tmp/'+file_name)
file_path = '/tmp/'+file_name

#Sending an Email
def sendmail(file_name,file_path):
    msg = MIMEMultipart()
    msg['Subject'] = 'AWS Tag Report for Account (%s)' %(account_id)
    msg['From'] = 'no-reply@salliemae.com'
    msg['To'] = COMMASPACE.join(to_emails)

    part = MIMEText('Please find the attached CSV of tag Report.\n')
    part1 = MIMEText('Below is the S3 link for the file\n\n https://s3.console.aws.amazon.com/s3/object/s3.02.s.02.e1.01.resource-tagreport/'+file_name+'?region=us-east-1&tab=overview')
    msg.attach(part)
    
    part = MIMEApplication(open(file_path, 'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename=file_name)
    msg.attach(part)
    msg.attach(part1)
    
    ses.send_raw_email(RawMessage={
         'Data': msg.as_string(),
    },
    Source=msg['From'],
    Destinations=to_emails)
    print "-------------------------------------------"
    print "Email Sent"
    print "-------------------------------------------"

#Creating CSV File
def create_csv(file_name,_file):
    try:
        #print "i am here"
        s3.Object('s3.02.s.02.e1.01.resource-tagreport', file_name).upload_file(_file)
    
    except Exception as e:
        print e

#Function to write the Tag values to the file
def writetofile(items,Name,csv_file,list):
    for item in items:
        values = []
        avail_tags = []
        avail_values = []
        print "File writing for %s - %s" %(Name,item.id)
        resource = Name
        icontent = ''
        ivalues = ''
        icontent += resource + ','+ str(item.id) +','
        csv_file.write(icontent)
        csv_file.flush()
        values = item.tags
        if values != None:
            for tag in values:
                if tag['Key'] in list:
                    if tag['Value'] != '':
                        avail_tags.append(tag['Key'])
                        avail_values.append(tag['Value'])

            a = 0
            for i in list:
                if i in avail_tags:
                    ind = avail_tags.index(i)
                    ab = avail_values[ind] +','
                    ivalues += ab
                    a += 1
                else:
                    ab = '     ,'
                    ivalues += ab
            csv_file.write(ivalues + '\n')
            csv_file.flush()
        else:
            for i in list:
                ab = '    ,'
                ivalues += ab

            csv_file.write(ivalues + '\n')
            csv_file.flush()

    csv_file.write('\n')
    csv_file.flush()

#Main Funtion
def main(event, context):
    print "-------------------------------------------"
    print "Writing Tag Report to the CSV File"
    print "-------------------------------------------"
    try:
        #EC2 resource
        ec2 = boto3.resource('ec2',region_name='us-east-1')

        list = ['Name', 'Cost_Center', 'Resource_Owner', 'Appl_Or_Function_Code', 'OS', 'Domain', 'ConfigMgmtParams', 'Created_By', 'Team_Supporting_Application', 'Schedule_Action', 'Expiration_Date', 'Contact_email', 'Contact_Phone', 'Blue_Green', 'Environment', 'MSP_Managed', 'Sec_AppDev', 'Sec_Crypto', 'Sec_Forensics', 'Schedule_Time', 'Application Role', 'Sec_DataTypes', 'Maintenance_window']
        Header = 'Resource Name, Resource ID, Name, Cost_Center, Resource_Owner, Appl_Or_Function_Code, OS, Domain, ConfigMgmtParams, Created_By, Team_Supporting_Application, Schedule_Action, Expiration_Date, Contact_email, Contact_Phone, Blue_Green, Environment, MSP_Managed, Sec_AppDev, Sec_Crypto, Sec_Forensics, Schedule_Time, Application Role, Sec_DataTypes, Maintenance_window \n'
        csv_file = open(file_path, 'r+')

        csv_file.write(Header)
        csv_file.flush()
        running_instances = ec2.instances.filter(Filters=[{
            'Name': 'instance-state-name',
            'Values': ['running']}])

        #print getting EC2 Tags Report"
        for instance in running_instances:
            avail_tags = []
            avail_values = []
            print "File writing for ec2 - %s" %(instance.id)
            ec2content = ''
            _ec2values = ''
            ec2content += 'EC2' + ','+ str(instance.id) +','
            csv_file.write(ec2content)
            csv_file.flush()
            for tag in instance.tags:
                if tag['Key'] in list:
                    if tag['Value'] != '':
                        avail_tags.append(tag['Key'])
                        avail_values.append(tag['Value'])

            a = 0
            for i in list:
                if i in avail_tags:
                    ind = avail_tags.index(i)
                    ab = avail_values[ind] +','
                    _ec2values += ab
                    a += 1
                else:
                    ab = '     ,'
                    _ec2values += ab

            csv_file.write(_ec2values + '\n')
            csv_file.flush()

        csv_file.write('\n')
        csv_file.flush()

        #Doing for AMI
        ec2client = boto3.client('ec2')
        try:
            response = ec2client.describe_images(Owners=['self'])
            for r in response['Images']:
                values = []
                avail_tags = []
                avail_values = []
                print "File writing for AMI - %s" %(r['ImageId'])
                amicontent = ''
                amivalues = ''
                amicontent += 'ami' + ','+ str(r['ImageId']) +','
                csv_file.write(amicontent)
                csv_file.flush()
                ami = ec2.Image(r['ImageId'])
                values = ami.tags
                if values != None:
                    for tag in values:
                        if tag['Key'] in list:
                            if tag['Value'] != '':
                                avail_tags.append(tag['Key'])
                                avail_values.append(tag['Value'])

                    a = 0
                    for i in list:
                        if i in avail_tags:
                            ind = avail_tags.index(i)
                            ab = avail_values[ind] +','
                            amivalues += ab
                            a += 1
                        else:
                            ab = '     ,'
                            amivalues += ab
                    csv_file.write(amivalues + '\n')
                    csv_file.flush()
                else:
                    for i in list:
                        ab = '    ,'
                        amivalues += ab

                    csv_file.write(amivalues + '\n')
                    csv_file.flush()
    
            csv_file.write('\n')
            csv_file.flush()

        except Exception as e:
            print "No AMI's Found"
            pass

        #Doing for EBS Volumes
        volumes = ec2.volumes.all()
        writetofile(volumes,'EBS Volume',csv_file,list)

        #Doing for EBS Snapshots
        ec2client = boto3.client('ec2')
        try:
            response = ec2client.describe_snapshots(OwnerIds=['self'])
            for r in response['Snapshots']:
                values = []
                avail_tags = []
                avail_values = []
                print "File writing for EBS Snapshot - %s" %(r['SnapshotId'])
                ebsscontent = ''
                ebssvalues = ''
                ebsscontent += 'EBS Snapshot' + ','+ str(r['SnapshotId']) +','
                csv_file.write(ebsscontent)
                csv_file.flush()
                snap = ec2.Snapshot(r['SnapshotId'])
                values = snap.tags
                if values != None:
                    for tag in values:
                        if tag['Key'] in list:
                            if tag['Value'] != '':
                                avail_tags.append(tag['Key'])
                                avail_values.append(tag['Value'])

                    a = 0
                    for i in list:
                        if i in avail_tags:
                            ind = avail_tags.index(i)
                            ab = avail_values[ind] +','
                            ebssvalues += ab
                            a += 1
                        else:
                            ab = '     ,'
                            ebssvalues += ab
                    csv_file.write(ebssvalues + '\n')
                    csv_file.flush()
                else:
                    for i in list:
                        ab = '    ,'
                        ebssvalues += ab

                    csv_file.write(ebssvalues + '\n')
                    csv_file.flush()

            csv_file.write('\n')
            csv_file.flush()
        except Exception as e:
            print "EBS Snaps not Found"
            pass

        #Doing for ENI
        #writetofile(eni,'Network Interface',csv_file,list)
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
                for NetworkInterface in inst["NetworkInterfaces"]:
                    values = []
                    avail_tags = []
                    avail_values = []
                    print "File writing for ENI - %s" %(NetworkInterface["NetworkInterfaceId"])
                    enicontent = ''
                    enivalues = ''
                    enicontent += 'ENI' + ','+ str(NetworkInterface["NetworkInterfaceId"]) +','
                    csv_file.write(enicontent)
                    csv_file.flush()
                    eni = ec2.NetworkInterface(NetworkInterface["NetworkInterfaceId"])
                    values = eni.tag_set
                    if values != None:
                        for tag in values:
                            if tag['Key'] in list:
                                if tag['Value'] != '':
                                    avail_tags.append(tag['Key'])
                                    avail_values.append(tag['Value'])

                        a = 0
                        for i in list:
                            if i in avail_tags:
                                ind = avail_tags.index(i)
                                ab = avail_values[ind] +','
                                enivalues += ab
                                a += 1
                            else:
                                ab = '     ,'
                                enivalues += ab
                        csv_file.write(enivalues + '\n')
                        csv_file.flush()
                    else:
                        for i in list:
                            ab = '    ,'
                            enivalues += ab

                        csv_file.write(enivalues + '\n')
                        csv_file.flush()

        csv_file.write('\n')
        csv_file.flush()

        #Doing for SG
        sgs = ec2.security_groups.all()
        writetofile(sgs,'Security Group',csv_file,list)

        #Doing for S3
        client = boto3.client('s3')
        response = client.list_buckets()
        for bucket in response["Buckets"]:
            avail_tags = []
            avail_values = []
            print "File writing for s3 - %s" %(bucket['Name'])
            bucket_tags = []
            s3content = ''
            _s3values = ''
            buck = bucket['Name']
            try:
                resp = client.get_bucket_tagging(Bucket=str(buck))
                for i in range(len(resp['TagSet'])):
                    #compare_bucket_tags(bucket_tags,ab['TagSet'][i])
                    bucket_tags.append(resp['TagSet'][i])

                s3content += 's3' + ','+ str(buck) +','
                csv_file.write(s3content)
                csv_file.flush()

                for tag in bucket_tags:
                    if tag['Key'] in list:
                        if tag['Value'] != '':
                            avail_tags.append(tag['Key'])
                            avail_values.append(tag['Value'])

                a = 0
                for i in list:
                    if i in avail_tags:
                        ind = avail_tags.index(i)
                        ab = avail_values[ind] +','
                        _s3values += ab
                        a += 1
                    else:
                        ab = '     ,'
                        _s3values += ab

            except Exception as e:
                bucket_tags = []

                s3content += 's3' + ','+ str(buck) +','
                csv_file.write(s3content)
                csv_file.flush()

                for i in list:
                    ab = '    ,'
                    _s3values += ab

            csv_file.write(_s3values + '\n')
            csv_file.flush()

        csv_file.write('\n')
        csv_file.flush()

        #Doing for VPC
        #vpc = ec2.vpc_addresses.all()
        response = ec2client.describe_vpcs(Filters=[
            {
                'Name': 'state',
                'Values': [
                    'available',
                ]
            },
        ])
        for r in response["Vpcs"]:
            values = []
            avail_tags = []
            avail_values = []
            print "File writing for VPC - %s" %(r["VpcId"])
            vpccontent = ''
            vpcvalues = ''
            vpccontent += 'VPC' + ','+ str(r["VpcId"]) +','
            csv_file.write(vpccontent)
            csv_file.flush()
            values = r["Tags"]
            if values != None:
                for tag in values:
                    if tag['Key'] in list:
                        if tag['Value'] != '':
                            avail_tags.append(tag['Key'])
                            avail_values.append(tag['Value'])

                a = 0
                for i in list:
                    if i in avail_tags:
                        ind = avail_tags.index(i)
                        ab = avail_values[ind] +','
                        vpcvalues += ab
                        a += 1
                    else:
                        ab = '     ,'
                        vpcvalues += ab
                csv_file.write(vpcvalues + '\n')
                csv_file.flush()
            else:
                for i in list:
                    ab = '    ,'
                    vpcvalues += ab

                csv_file.write(vpcvalues + '\n')
                csv_file.flush()

        csv_file.write('\n')
        csv_file.flush()

        #Doing for Subnet
        subnets = ec2.subnets.all()
        writetofile(subnets,'Subnet',csv_file,list)
        
        #Doing for Route Table
        routetables = ec2.route_tables.all()
        writetofile(routetables,'Route Table',csv_file,list)

        #Doing for Internet Gateways
        igs = ec2.internet_gateways.all()
        writetofile(igs,'Internet Gateway',csv_file,list)

        #Doing for DHCP Option Sets
        dhcp = ec2.dhcp_options_sets.all()
        writetofile(dhcp,'DHCP',csv_file,list)

        #Doing for VPC Peering Connections
        peering = ec2.vpc_peering_connections.all()
        writetofile(peering,'VPC Peering Connection',csv_file,list)

        #Doing for Network ACL's
        acl = ec2.network_acls.all()
        writetofile(acl,'Network ACL',csv_file,list)

        #Doing for Customer Gateways
        response = ec2client.describe_customer_gateways(Filters=[
            {
                'Name': 'state',
                'Values': [
                    'available',
                ]
            },
        ])
        for r in response['CustomerGateways']:
            values = []
            avail_tags = []
            avail_values = []
            print "File writing for Customer Gateway- %s" %(r['CustomerGatewayId'])
            cgcontent = ''
            cgvalues = ''
            cgcontent += 'Customer Gateway' + ','+ str(r['CustomerGatewayId']) +','
            csv_file.write(cgcontent)
            csv_file.flush()
            values = r['Tags']
            if values != None:
                for tag in values:
                    if tag['Key'] in list:
                        if tag['Value'] != '':
                            avail_tags.append(tag['Key'])
                            avail_values.append(tag['Value'])

                a = 0
                for i in list:
                    if i in avail_tags:
                        ind = avail_tags.index(i)
                        ab = avail_values[ind] +','
                        cgvalues += ab
                        a += 1
                    else:
                        ab = '     ,'
                        cgvalues += ab
                csv_file.write(cgvalues + '\n')
                csv_file.flush()
            else:
                for i in list:
                    ab = '    ,'
                    cgvalues += ab

                csv_file.write(cgvalues + '\n')
                csv_file.flush()

        csv_file.write('\n')
        csv_file.flush()

        #Doing for VPG
        response = ec2client.describe_vpn_gateways()
        for r in response['VpnGateways']:
            values = []
            avail_tags = []
            avail_values = []
            print "File writing for VPN Gateway- %s" %(r['VpnGatewayId'])
            vpncontent = ''
            vpnvalues = ''
            vpncontent += 'VPN Gateway' + ','+ str(r['VpnGatewayId']) +','
            csv_file.write(vpncontent)
            csv_file.flush()
            values = r['Tags']
            if values != None:
                for tag in values:
                    if tag['Key'] in list:
                        if tag['Value'] != '':
                            avail_tags.append(tag['Key'])
                            avail_values.append(tag['Value'])

                a = 0
                for i in list:
                    if i in avail_tags:
                        ind = avail_tags.index(i)
                        ab = avail_values[ind] +','
                        vpnvalues += ab
                        a += 1
                    else:
                        ab = '     ,'
                        vpnvalues += ab
                csv_file.write(vpnvalues + '\n')
                csv_file.flush()
            else:
                for i in list:
                    ab = '    ,'
                    vpnvalues += ab

                csv_file.write(vpnvalues + '\n')
                csv_file.flush()

        csv_file.write('\n')
        csv_file.flush()

        #Doing for VPN Connections
        response = ec2client.describe_vpn_connections(Filters=[
            {
                'Name': 'vpn-gateway-id',
            },
        ])
        for r in response['VpnConnections']:
            values = []
            avail_tags = []
            avail_values = []
            print "File writing for VPN Connection- %s" %(r['VpnConnectionId'])
            vpnccontent = ''
            vpncvalues = ''
            vpnccontent += 'VPN Connection' + ','+ str(r['VpnConnectionId']) +','
            csv_file.write(vpnccontent)
            csv_file.flush()
            values = r['Tags']
            if values != None:
                for tag in values:
                    if tag['Key'] in list:
                        if tag['Value'] != '':
                            avail_tags.append(tag['Key'])
                            avail_values.append(tag['Value'])

                a = 0
                for i in list:
                    if i in avail_tags:
                        ind = avail_tags.index(i)
                        ab = avail_values[ind] +','
                        vpncvalues += ab
                        a += 1
                    else:
                        ab = '     ,'
                        vpncvalues += ab
                csv_file.write(vpncvalues + '\n')
                csv_file.flush()
            else:
                for i in list:
                    ab = '    ,'
                    vpncvalues += ab

                csv_file.write(vpncvalues + '\n')
                csv_file.flush()

        csv_file.write('\n')
        csv_file.flush()

        #Creating the File
        create_csv(file_name,file_path)
        
        print "-------------------------------------------"
        print "Sending an email to Cloud Engineering Team..."
        sendmail(file_name,file_path)

    except Exception as e:
        print e
