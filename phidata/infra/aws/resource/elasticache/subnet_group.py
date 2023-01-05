from typing import Optional, Any, Dict, List

from phidata.infra.aws.api_client import AwsApiClient
from phidata.infra.aws.resource.base import AwsResource
from phidata.infra.aws.resource.cloudformation.stack import CloudFormationStack
from phidata.utils.cli_console import print_info, print_error
from phidata.utils.log import logger


class CacheSubnetGroup(AwsResource):
    """
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elasticache.html#ElastiCache.Client.create_cache_subnet_group

    Creates a cache subnet group.
    """

    resource_type = "CacheSubnetGroup"
    service_name = "elasticache"

    # A name for the cache subnet group. This value is stored as a lowercase string.
    # Constraints: Must contain no more than 255 alphanumeric characters or hyphens.
    name: str
    # A description for the cache subnet group.
    description: Optional[str] = None
    # A list of VPC subnet IDs for the cache subnet group.
    subnet_ids: Optional[List[str]] = None
    # Get Subnet IDs from a VPC CloudFormationStack
    # NOTE: only gets privatesubnets from the vpc stack
    vpc_stack: Optional[CloudFormationStack] = None
    # A list of tags to be added to this resource.
    tags: Optional[List[Dict[str, str]]] = None

    def _create(self, aws_client: AwsApiClient) -> bool:
        """Creates the CacheSubnetGroup

        Args:
            aws_client: The AwsApiClient for the current cluster
        """

        print_info(f"Creating {self.get_resource_type()}: {self.get_resource_name()}")
        try:
            # create a dict of args which are not null, otherwise aws type validation fails
            not_null_args: Dict[str, Any] = {}

            if self.tags:
                not_null_args["Tags"] = self.tags

            subnet_ids = self.subnet_ids
            if subnet_ids is None and self.vpc_stack is not None:
                logger.debug("Getting private subnet_ids from vpc stack")
                subnet_ids = self.vpc_stack.get_private_subnets(aws_client=aws_client)

            # Create CacheSubnetGroup
            service_client = self.get_service_client(aws_client)
            create_response = service_client.create_cache_subnet_group(
                CacheSubnetGroupName=self.name,
                CacheSubnetGroupDescription=self.description
                or f"Created for {self.name}",
                SubnetIds=subnet_ids,
                **not_null_args,
            )
            logger.debug(f"create_response type: {type(create_response)}")
            logger.debug(f"create_response: {create_response}")

            self.active_resource = create_response.get("CacheSubnetGroup", None)
            if self.active_resource is not None:
                print_info(
                    f"{self.get_resource_type()}: {self.get_resource_name()} created"
                )
                logger.debug(f"CacheSubnetGroup: {self.active_resource}")
                return True
        except Exception as e:
            print_error(f"{self.get_resource_type()} could not be created.")
            print_error(e)
        return False

    def _read(self, aws_client: AwsApiClient) -> Optional[Any]:
        """Returns the CacheSubnetGroup

        Args:
            aws_client: The AwsApiClient for the current cluster
        """
        from botocore.exceptions import ClientError

        logger.debug(f"Reading {self.get_resource_type()}: {self.get_resource_name()}")
        try:
            service_client = self.get_service_client(aws_client)
            describe_response = service_client.describe_cache_subnet_groups(
                CacheSubnetGroupName=self.name
            )
            logger.debug(f"describe_response type: {type(describe_response)}")
            logger.debug(f"describe_response: {describe_response}")

            cache_subnet_group_list = describe_response.get("CacheSubnetGroups", None)
            if cache_subnet_group_list is not None and isinstance(
                cache_subnet_group_list, list
            ):
                for _cache_subnet_group in cache_subnet_group_list:
                    _cache_sg_name = _cache_subnet_group.get(
                        "CacheSubnetGroupName", None
                    )
                    if _cache_sg_name == self.name:
                        self.active_resource = _cache_subnet_group
                        break

            if self.active_resource is None:
                logger.debug(f"No {self.get_resource_type()} found")
                return None

            logger.debug(f"CacheSubnetGroup: {self.active_resource}")
        except ClientError as ce:
            logger.debug(f"ClientError: {ce}")
        except Exception as e:
            print_error(f"Error reading {self.get_resource_type()}.")
            print_error(e)
        return self.active_resource

    def _delete(self, aws_client: AwsApiClient) -> bool:
        """Deletes the CacheSubnetGroup

        Args:
            aws_client: The AwsApiClient for the current cluster
        """

        print_info(f"Deleting {self.get_resource_type()}: {self.get_resource_name()}")
        try:
            service_client = self.get_service_client(aws_client)
            self.active_resource = None

            delete_response = service_client.delete_cache_subnet_group(
                CacheSubnetGroupName=self.name
            )
            logger.debug(f"delete_response: {delete_response}")
            print_info(
                f"{self.get_resource_type()}: {self.get_resource_name()} deleted"
            )
            return True
        except Exception as e:
            print_error(f"{self.get_resource_type()} could not be deleted.")
            print_error("Please try again or delete resources manually.")
            print_error(e)
        return False
