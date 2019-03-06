# Automatically Updated Security Group with Route53 Healthcheck CIDR Ranges

---

## Description

Serverless Framework project that will create a Lambda function and a security group. The lambda function is triggered by updates to the [AWS ip-range.json file](https://docs.aws.amazon.com/general/latest/gr/aws-ip-ranges.html) that contains all AWS public endpoint CIDR ranges.

The Lambda function will retrieve this file whenever it is updated by AWS, filter the results to contain only CIDR ranges for Route53 HealthChecks, and then update the security group with ingress rules for these CIDR ranges.  

The purpose of the project is to provide an automatically updated security group that you can use on any resource that will have Route53 healthchecks ran against it.  



---

## Requirements

- Serverless Framework
- Serverless Plugin - [serverless-python-requirements](https://www.npmjs.com/package/serverless-python-requirements)

---

## Installation

Git Clone: 

```
git clone Project-Security-Group-R53-HealthChecks.git
cd Project-Security-Group-R53-HealthChecks
```

Serverless Framework Installation:

```
npm install -g serverless
```

Install Serverless Plugin:

```
sls plugin install -n serverless-python-requirements
```

Deploy to AWS:

```
sls deploy
```
