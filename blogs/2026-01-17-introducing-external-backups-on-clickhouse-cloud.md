---
title: "Introducing external backups on ClickHouse Cloud"
date: "2025-10-14T21:44:54.968Z"
author: "Aashish Kohli & Garrett Thomas"
category: "Product"
excerpt: "ClickHouse Cloud is launching external backups, letting you export full, daily backups to your own storage on the same cloud provider (AWS/GCP/Azure) for complete control over retention, region placement, cold storage, and costs. "
---

# Introducing external backups on ClickHouse Cloud

As a SaaS database company, we are acutely aware of the amount of trust required from our users, as data corruption or loss could be potentially catastrophic for a business. Given this gravity, we totally understand why users would want to have possession of and control over their data. Therefore, we are announcing external backups. This is a feature in which users will be able to export backups of their ClickHouse cloud services to their cloud storage. This empowers users to:



* Have full sovereignty over their backups.
* Keep backups indefinitely.
* Move backups to cold storage.
* Store backups in a different region for multi-region data protection strategies.
* Take advantage of any cloud credits they may have. 
   

In this blog post, we will show how to set up external backups, how to restore an external backup to ClickHouse cloud, comment on the various technical decisions made, and finally give a sneak peek into what is next for external backups for ClickHouse cloud. This feature is available on all ClickHouse Cloud supported CSPs (AWS, GCP, and Azure). The backups can be exported to any region as long as it is in the same provider as the ClickHouse Cloud service, i.e., cross-cloud backups are not supported. Backups to different regions will incur [data transfer charges](https://clickhouse.com/docs/cloud/manage/network-data-transfer).

In this blog post, we will focus on AWS, and we will assume you already have an S3 bucket to export your backups into.


### Setting up external backups 


#### Permissions

The first step is to create the role and permissions policy that will give the ClickHouse service permissions to backup to the external S3 bucket. 



1. AWS uses role-based authentication, so you need to create an IAM role that the ClickHouse Cloud service can assume. We will then grant that role permissions to write to the bucket.


i. Obtain the ARN from the ClickHouse Cloud service settings page, under Network security information. It will look similar to this:
    
![Image 1.png](https://clickhouse.com/uploads/Image_1_ee15d840fc.png)

ii. Create the trust policy as follows, replacing the role ARN from your service: 

```
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "backup service",
			"Effect": "Allow",
			"Principal": {
				"AWS":  "arn:aws:iam::463754717262:role/CH-S3-bordeaux-ar-90-ue2-29-Role"
			},
			"Action": "sts:AssumeRole"
		},
	]
}
```


2. We also need to grant this role the necessary permissions to export a backup to the S3 bucket. This is done by creating a permissions policy for the role with a JSON similar to this one, where you substitute in your bucket ARN in every resource field.

```
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Action": [
				"s3:GetBucketLocation",
				"s3:ListBucket"
			],
			"Resource": [
				"arn:aws:s3:::backup-bucket"
			],
			"Effect": "Allow"
		},
		{
			"Action": [
				"s3:Get*",
				"s3:List*",
				"s3:PutObject"
			],
			"Resource": [
				"arn:aws:s3:::backup-bucket/*"
			],
			"Effect": "Allow"
		},
		{
			"Action": [
				"s3:DeleteObject"
			],
			"Resource": [
                "arn:aws:s3:::backup-bucket/*/.lock"
             ],
			"Effect": "Allow"
		},
	]
}
```

At this point, the ClickHouse Cloud service can assume the new role and has all the necessary permissions. Now we just have to configure ClickHouse Cloud to enable external backups. 

:::global-blog-cta::: 

#### ClickHouse Cloud Configuration

On the ClickHouse Cloud console, you will need to configure the external bucket.



1. On the Settings page, click on “Set up external backup”

![Image 2.png](https://clickhouse.com/uploads/Image_2_75696b2c9e.png)

2. On the subsequent screen, provide the AWS IAM Role ARN you just created and the S3 bucket URL in the following format

![Image 3...png](https://clickhouse.com/uploads/Image_3_7c0b7df0fb.png)


That’s it, and the first external backup will start within an hour!

By default, backups will then be taken daily (as specified [here](https://clickhouse.com/docs/cloud/manage/backups/overview#default-backup-policy)). However, for additional control, we also support [configurable](https://clickhouse.com/docs/cloud/manage/backups/configurable-backups) backups to your own cloud account to set a custom schedule. You are able to set a start time and frequency (with daily being the most frequent option) for backing up to external buckets. 

Up until now, external backups may appear quite similar to the default backups within ClickHouse Cloud. However, there are two important distinctions that set external backups apart:

The first key difference is in lifecycle management. Unlike ClickHouse Cloud backups, which are automatically lifecycled (i.e., deleted once a defined TTL is past, given there are a sufficient number of newer backups), external backups are not managed by ClickHouse Cloud once they are written to the external storage location e.g., S3 bucket. This decision was made because: 



1. ClickHouse cloud cannot be certain that it knows where the backup is after it is written to the external storage (for example, the backups could be moved to cold storage to save costs), and
2. External backups can be stored as long as you want and according to whatever conditions you want. Lifecycling the backups yourself gives you the most freedom to implement any desired retention logic. 

The fact that ClickHouse Cloud does not lifecycle backups means that this responsibility falls entirely on you, the user. If backups are not deleted manually or programmatically, they will persist indefinitely, potentially leading to unnecessary storage costs and clutter. To address this, users are encouraged to automate backup deletion using tools like bucket TTL policies (which can automatically remove objects from cloud storage after a set period) or through custom scripts. 

The second major difference is that incremental backups are disabled i.e. all external backups are full backups. While this does require more compute and storage, it is safer. An incremental backup relies on **all previous backups** in the backup chain. If one is removed or corrupted, all following backups will be unrecoverable. Backups are the last line of defense against data loss and corruption, so we decided to err on the side of safety and go with all full backups. The tradeoff is this, though: full backups take longer to complete, often running for several hours, especially on large services. Due to this, the highest allowed external backup frequency is once per day. Allowing more frequent full backups could result in concurrent backup processes, which could stress the system. Backups to the default bucket still use incremental backups and continue on the standard schedule.


### Restoring a Backup

To restore a backup, we template the backup command, and let you run it yourself. 

This approach has the following benefits: 



* A congruous process for restoring a backup in the original location or in a new location. For example, if the backup was moved to another bucket for cold storage, editing the backup command requires only a few keystrokes.  
* Providing the users feedback about any misconfiguration of permissions or backup location. This information will come by way of ClickHouse error messages. For example, if the permissions are incorrectly configured they may see error messages like:

![Image 3...png](https://clickhouse.com/uploads/Image_3_7c0b7df0fb.png)


Or if the path is incorrect they may see error messages like:

![image 4...png](https://clickhouse.com/uploads/image_4_7f31632823.png)

This way, you can readily have clarity on what’s causing an error and have direction for remediation, hopefully reducing time to fix or mitigating escalation altogether. 



#### Restore Process



1. Create a new service to restore the backup to. 
2. Add the newly created service’s ARN (from the service settings page in ClickHouse Cloud console) to the trust policy for the IAM role - same as the second step in the “Permissions” section above. This is required so the new service can access the S3 bucket.
3. Click on the “Access or restore a backup” link above the list of backups in the UI to obtain the SQL command to restore the backup. The command will look like this: 

![image 5....png](https://clickhouse.com/uploads/image_5_2c93eca274.png)


   You can pick the desired backup from the dropdown to get the restore command for that specific backup. If you have moved your backup somewhere else in your cloud storage, you will need to customize the command yourself.



4. Run the restore command from the SQL console in the newly created service to restore the backup.


### Looking Ahead: Cross-Cloud Backup Support

We're excited to announce that cross-cloud backup capabilities are on our roadmap. This will enable you to backup your ClickHouse Cloud service running on one cloud provider (such as AWS) to storage on a different provider (like GCP or Azure), unlocking multi-cloud data protection strategies and unlocking potential economic benefits from different clouds (for example, cheaper storage or existing cloud credits). 

If this capability would be valuable for you, we'd love to hear from you—please reach out to our support team to share your requirements and help us prioritize this feature development.


### Conclusion

External backups represent a significant step forward in giving ClickHouse Cloud users sovereignty over their data. By enabling you to export backups to your own cloud storage, you maintain control over your own backups. You can implement custom retention policies, leverage existing cloud credits, utilize cold storage for cost optimization, and store backups across different regions for enhanced security.

External backups are now available across all ClickHouse Cloud supported CSPs (AWS, GCP, and Azure). We encourage you to explore this feature and take advantage of the enhanced control and flexibility it provides for your data needs. For questions or support with implementation, don't hesitate to reach out to our support team!
