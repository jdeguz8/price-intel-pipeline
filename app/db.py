import boto3
from .config import settings


def dynamodb_resource():
    return boto3.resource("dynamodb", region_name=settings.aws_region)


def products_table():
    return dynamodb_resource().Table(settings.products_table)
