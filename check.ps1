$arrService = Get-Service -Name AmazonCloudWatchAgent

while ($arrService.Status -ne 'Running')
{

    Start-Service $ServiceName
    write-host $arrService.status
    write-host 'Service starting'
    Start-Sleep -seconds 60
    $arrService.Refresh()
    if ($arrService.Status -eq 'Running')
    {
        Write-Host 'Service is now Running'
    }

}
#https://stackoverflow.com/questions/40658251/why-are-cloudwatch-logs-sent-from-my-windows-ec2-instance-not-showing-up-on-aws
#https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-ec2_instance-profiles.html
#https://docs.aws.amazon.com/cli/latest/reference/iam/add-role-to-instance-profile.html
#https://stackoverflow.com/questions/406230/regular-expression-to-match-a-line-that-doesnt-contain-a-word 


#https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/create-cloudwatch-agent-configuration-file-wizard.html
#https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/UseCloudWatchUnifiedAgent.html




{
        "agent": {
        "metrics_collection_interval": 60,
        "logfile": "c:\\ProgramData\\Amazon\\AmazonCloudWatchAgent\\Logs\\amazon-cloudwatch-agent.log"
      },
      "logs": {
        "logs_collected": {
          "files": {
            "collect_list": [
              {
                "file_path": "c:\\ProgramData\\Amazon\\AmazonCloudWatchAgent\\Logs\\amazon-cloudwatch-agent.log",
                "log_group_name": "cwlg.01.s.02.e1.03.clwagentlogs",
                "timezone": "UTC"
              },
              {
                "file_path": "c:\\ProgramData\\Amazon\\AmazonCloudWatchAgent\\Logs\\test.log",
                "log_group_name": "cwlg.01.s.02.e1.03.clwagentlogs",
                "timezone": "Local"
              }
            ]
          },
          "windows_events": {
            "collect_list": [
              {
                "event_name": "System",
                "event_levels": [
                  "INFORMATION",
                  "ERROR"
                ],
                "log_group_name": "System",
                "log_stream_name": "System",
                "event_format": "xml"
              },
              {
                "event_name": "Application",
                "event_levels": [
                  "WARNING",
                  "ERROR"
                ],
                "log_group_name": "Application",
                "log_stream_name": "Application",
                "event_format": "xml"
              }
            ]
          }
        },
        "log_stream_name": "{instance_id}"
      },
	"metrics": {
		"append_dimensions": {
			"AutoScalingGroupName": "${aws:AutoScalingGroupName}",
			"ImageId": "${aws:ImageId}",
			"InstanceId": "${aws:InstanceId}",
			"InstanceType": "${aws:InstanceType}"
		},
		"metrics_collected": {
			"LogicalDisk": {
				"measurement": [
					"% Free Space"
				],
				"metrics_collection_interval": 30,
				"resources": [
					"*"
				]
			},
			"Memory": {
				"measurement": [
					"% Committed Bytes In Use"
				],
				"metrics_collection_interval": 30
			},
			"Paging File": {
				"measurement": [
					"% Usage"
				],
				"metrics_collection_interval": 30,
				"resources": [
					"*"
				]
			},
			"PhysicalDisk": {
				"measurement": [
					"% Disk Time",
					"Disk Write Bytes/sec",
					"Disk Read Bytes/sec",
					"Disk Writes/sec",
					"Disk Reads/sec"
				],
				"metrics_collection_interval": 30,
				"resources": [
					"*"
				]
			},
			"Processor": {
				"measurement": [
					"% User Time",
					"% Idle Time",
					"% Interrupt Time"
				],
				"metrics_collection_interval": 30,
				"resources": [
					"*"
				]
			},
			"TCPv4": {
				"measurement": [
					"Connections Established"
				],
				"metrics_collection_interval": 30
			},
			"TCPv6": {
				"measurement": [
					"Connections Established"
				],
				"metrics_collection_interval": 30
			}
		}
	}
}
