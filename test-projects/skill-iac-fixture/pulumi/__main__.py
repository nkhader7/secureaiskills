"""
scan-iac-security fixture — Pulumi Python program misconfigurations
Intentionally vulnerable — do not deploy
"""

import pulumi
import pulumi_aws as aws

# IAC-PULUMI-003: S3 bucket with public ACL
data_bucket = aws.s3.Bucket(
    "public-data",
    acl="public-read",  # IAC-PULUMI-003: public read
    versioning=aws.s3.BucketVersioningArgs(enabled=False),  # IAC-PULUMI-004: no versioning
)

# IAC-PULUMI-005: security group allowing all traffic
open_sg = aws.ec2.SecurityGroup(
    "open-sg",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            from_port=0,
            to_port=65535,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],  # IAC-PULUMI-005: world open
        )
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
)

# IAC-PULUMI-006: RDS with plaintext password and public access
db = aws.rds.Instance(
    "vulnerable-db",
    engine="mysql",
    instance_class="db.t3.micro",
    allocated_storage=20,
    username="admin",
    password="pulumi_rds_password_123",  # IAC-PULUMI-006: hardcoded secret
    publicly_accessible=True,  # IAC-PULUMI-007
    storage_encrypted=False,  # IAC-PULUMI-008
    deletion_protection=False,
    skip_final_snapshot=True,
)

# IAC-PULUMI-009: IAM policy with admin wildcard
admin_policy = aws.iam.Policy(
    "admin-policy",
    policy="""{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": "*",
            "Resource": "*"
        }]
    }""",
)

pulumi.export("bucket_name", data_bucket.id)
pulumi.export("db_endpoint", db.endpoint)
