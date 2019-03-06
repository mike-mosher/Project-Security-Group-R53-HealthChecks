# Purpose:
#
# Download the ip-ranges.json file that lists all AWS public endpoints and
# filter out the ip cidr ranges for Route53 Healthchecks
#
# Then use this data to update a security group, which should only allow
# traffic from the current list of ip cidr ranges in this ip-ranges.json file

import os
import boto3
import botocore
import requests

# Globals
ip_ranges_url = 'https://ip-ranges.amazonaws.com/ip-ranges.json'
r53_healthcheck_service_type = 'ROUTE53_HEALTHCHECKS'
region = os.environ['region']
security_group_id = os.environ['SecurityGroupId']
FromPort = int(os.environ['FromPort'])
ToPort = int(os.environ['ToPort'])
IpProtocol = os.environ['IpProtocol']
ec2 = boto3.resource('ec2')
security_group = ec2.SecurityGroup(security_group_id)


def get_aws_service_cidr_ranges(ip_ranges_url):
    """
    Gets https://ip-ranges.amazonaws.com/ip-ranges.json and returns the
    "prefixes" element which is a list of services and the IPv4 prefix/cidr
    range that service uses.
    Example:
    [{
        "ip_prefix": "18.208.0.0/13",
        "region": "us-east-1",
        "service": "EC2"
    }, …]

    Arguments:
        ip_ranges_url {str} -- ip-ranges.json URL as string

    Returns:
        list -- list of dictionary objects that represent AWS services
    """

    response = requests.get(ip_ranges_url)

    if not response.status_code == 200:
        exit('error retrieving data from URL')

    return response.json()['prefixes']


def filter_cidr_ranges_by_service_type_and_current_region(cidr_ranges, service):
    """
    Returns a filtered list of AWS services by service type and current region

    Arguments:
        cidr_range {list} -- list of dictionary objects that represent AWS
        services.  Example:
        [{
            "ip_prefix": "18.208.0.0/13",
            "region": "us-east-1",
            "service": "EC2"
        }, …]

        service {string} -- service used to filter the list

    Returns:
        list -- list of filtered dictionary objects that represent AWS services
    """

    return [cidr_range['ip_prefix'] for cidr_range in cidr_ranges
            if cidr_range['service'] == service and
            cidr_range['region'] == region]


def remove_all_rules_from_security_group(security_group):
    """
    Takes a given security group ID and removes all rules from this group

    Arguments:
        security_group {boto3.resources.factory.ec2.SecurityGroup} -- boto3
        object representing the security group

    Returns:
        None -- No return object
    """

    if not security_group.ip_permissions:
        return None

    response = security_group.revoke_ingress(
        IpPermissions=security_group.ip_permissions)

    if not response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print('Unsuccessful API call: ec2.security_group.revoke_ingress')
        print(response)


def add_cidr_ranges_to_security_group(cidr_ranges, security_group):
    """
    Takes a list of CIDR ranges and adds them as rules to the specified
    security group

    Arguments:
        cidr_ranges {list} -- list of dictionary objects that represent AWS
        services

        security_group {boto3.resources.factory.ec2.SecurityGroup} -- boto3
        object representing the security group
    """

    ip_permissions_list = []

    for CidrIp in cidr_ranges:
        ip_permissions_list.append({
            'FromPort': FromPort,
            'ToPort': ToPort,
            'IpProtocol': IpProtocol,
            'IpRanges': [
                {
                    'CidrIp': CidrIp,
                    'Description': 'Route53 HealthCheck Endpoint Cidr Range for ' + region
                }
            ]
        })

    try:
        response = security_group.authorize_ingress(
            GroupId=security_group.id,
            IpPermissions=ip_permissions_list
        )
    except botocore.exceptions.ClientError as e:
        print(e)
    else:
        if not response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print('Unsuccessful API call: ec2.security_group.authorize_ingress')
            print(response)


def main(event, context):

    cidr_ranges = get_aws_service_cidr_ranges(ip_ranges_url)

    r53_healthcheck_cidr_ranges = filter_cidr_ranges_by_service_type_and_current_region(
        cidr_ranges, r53_healthcheck_service_type)

    remove_all_rules_from_security_group(security_group)

    add_cidr_ranges_to_security_group(
        r53_healthcheck_cidr_ranges, security_group)


if __name__ == '__main__':
    main("", "")
