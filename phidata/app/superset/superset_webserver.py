from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from typing_extensions import Literal

from phidata.app.db import DbApp
from phidata.app.superset.superset_base import SupersetBase
from phidata.infra.k8s.create.apps.v1.deployment import RestartPolicy
from phidata.infra.k8s.create.core.v1.service import ServiceType
from phidata.infra.k8s.create.core.v1.container import CreateContainer, ImagePullPolicy
from phidata.infra.k8s.create.core.v1.volume import CreateVolume
from phidata.infra.k8s.create.common.port import CreatePort
from phidata.infra.k8s.create.group import (
    CreateNamespace,
    CreateServiceAccount,
    CreateSecret,
    CreateConfigMap,
    CreateStorageClass,
    CreateService,
    CreateDeployment,
    CreateCustomObject,
    CreateCustomResourceDefinition,
    CreatePersistentVolume,
    CreatePVC,
    CreateClusterRole,
    CreateClusterRoleBinding,
)


class SupersetWebserver(SupersetBase):
    def __init__(
        self,
        name: str = "superset-ws",
        version: str = "1",
        enabled: bool = True,
        # Image args,
        image_name: str = "phidata/superset",
        image_tag: str = "2.0.0",
        entrypoint: Optional[Union[str, List]] = None,
        command: Optional[Union[str, List]] = "webserver",
        # Install python dependencies using a requirements.txt file,
        # Sets the REQUIREMENTS_LOCAL & REQUIREMENTS_FILE_PATH env var to requirements_file_path,
        install_requirements: bool = False,
        # Path to the requirements.txt file relative to the workspace_root,
        requirements_file_path: str = "requirements.txt",
        # Configure Superset db,
        wait_for_db: bool = False,
        # Connect to database using a DbApp,
        db_app: Optional[DbApp] = None,
        # Provide database connection details manually,
        # db_user can be provided here or as the,
        # DATABASE_USER env var in the secrets_file,
        db_user: Optional[str] = None,
        # db_password can be provided here or as the,
        # DATABASE_PASSWORD env var in the secrets_file,
        db_password: Optional[str] = None,
        # db_schema can be provided here or as the,
        # DATABASE_DB env var in the secrets_file,
        db_schema: Optional[str] = None,
        # db_host can be provided here or as the,
        # DATABASE_HOST env var in the secrets_file,
        db_host: Optional[str] = None,
        # db_port can be provided here or as the,
        # DATABASE_PORT env var in the secrets_file,
        db_port: Optional[int] = None,
        # db_driver can be provided here or as the,
        # DATABASE_DIALECT env var in the secrets_file,
        db_dialect: Optional[str] = None,
        # Configure superset redis,
        wait_for_redis: bool = False,
        # Connect to redis using a PhidataApp,
        redis_app: Optional[Any] = None,
        # redis_host can be provided here or as the,
        # REDIS_HOST env var in the secrets_file,
        redis_host: Optional[str] = None,
        # redis_port can be provided here or as the,
        # REDIS_PORT env var in the secrets_file,
        redis_port: Optional[int] = None,
        # redis_driver can be provided here or as the,
        # REDIS_DRIVER env var in the secrets_file,
        redis_driver: Optional[str] = None,
        # Configure the superset container,
        container_name: Optional[str] = None,
        # Set the SUPERSET_CONFIG_PATH env var,
        superset_config_path: Optional[str] = None,
        # Set the FLASK_ENV env var,
        flask_env: str = "production",
        # Set the SUPERSET_ENV env var,
        superset_env: str = "production",
        # Set the PYTHONPATH env var,
        # defaults to "/app/pythonpath:/app/docker/pythonpath_dev",
        python_path: Optional[str] = None,
        # Add labels to the container,
        container_labels: Optional[Dict[str, Any]] = None,
        # Docker configuration,
        # NOTE: Only available for Docker,
        # Run container in the background and return a Container object.,
        container_detach: bool = True,
        # Enable auto-removal of the container on daemon side when the container’s process exits.,
        container_auto_remove: bool = True,
        # Remove the container when it has finished running. Default: False.,
        container_remove: bool = True,
        # Username or UID to run commands as inside the container.,
        container_user: Optional[Union[str, int]] = None,
        # Keep STDIN open even if not attached.,
        container_stdin_open: bool = True,
        container_tty: bool = True,
        # Specify a test to perform to check that the container is healthy.,
        container_healthcheck: Optional[Dict[str, Any]] = None,
        # Optional hostname for the container.,
        container_hostname: Optional[str] = None,
        # Platform in the format os[/arch[/variant]].,
        container_platform: str = "linux/amd64",
        # Path to the working directory.,
        container_working_dir: Optional[str] = None,
        # Restart the container when it exits. Configured as a dictionary with keys:,
        # Name: One of on-failure, or always.,
        # MaximumRetryCount: Number of times to restart the container on failure.,
        # For example: {"Name": "on-failure", "MaximumRetryCount": 5},
        container_restart_policy_docker: Optional[Dict[str, Any]] = None,
        # Add volumes to DockerContainer,
        # container_volumes is a dictionary which adds the volumes to mount,
        # inside the container. The key is either the host path or a volume name,,
        # and the value is a dictionary with 2 keys:,
        #   bind - The path to mount the volume inside the container,
        #   mode - Either rw to mount the volume read/write, or ro to mount it read-only.,
        # For example:,
        # {,
        #   '/home/user1/': {'bind': '/mnt/vol2', 'mode': 'rw'},,
        #   '/var/www': {'bind': '/mnt/vol1', 'mode': 'ro'},
        # },
        container_volumes_docker: Optional[Dict[str, dict]] = None,
        # Add ports to DockerContainer,
        # The keys of the dictionary are the ports to bind inside the container,,
        # either as an integer or a string in the form port/protocol, where the protocol is either tcp, udp.,
        # The values of the dictionary are the corresponding ports to open on the host, which can be either:,
        #   - The port number, as an integer.,
        #       For example, {'2222/tcp': 3333} will expose port 2222 inside the container as port 3333 on the host.,
        #   - None, to assign a random host port. For example, {'2222/tcp': None}.,
        #   - A tuple of (address, port) if you want to specify the host interface.,
        #       For example, {'1111/tcp': ('127.0.0.1', 1111)}.,
        #   - A list of integers, if you want to bind multiple host ports to a single container port.,
        #       For example, {'1111/tcp': [1234, 4567]}.,
        container_ports_docker: Optional[Dict[str, Any]] = None,
        # K8s configuration,
        # NOTE: Only available for Kubernetes,
        image_pull_policy: ImagePullPolicy = ImagePullPolicy.IF_NOT_PRESENT,
        # Container ports,
        # Open a container port if open_container_port=True,
        open_container_port: bool = False,
        # Port number on the container,
        container_port: int = 8000,
        # Port name: Only used by the K8sContainer,
        container_port_name: str = "http",
        # Host port: Only used by the DockerContainer,
        container_host_port: int = 8000,
        # Open the app port if open_app_port=True,
        open_app_port: bool = True,
        # App port number on the container,
        # Set the SUPERSET_PORT env var,
        app_port: int = 8088,
        # Only used by the K8sContainer,
        app_port_name: str = "app",
        # Only used by the DockerContainer,
        app_host_port: int = 8088,
        # Container env,
        # Add env variables to container env,
        env: Optional[Dict[str, str]] = None,
        # Read env variables from a file in yaml format,
        env_file: Optional[Path] = None,
        # Configure the ConfigMap name used for env variables that are not Secret,
        config_map_name: Optional[str] = None,
        # Container secrets,
        # Add secret variables to container env,
        secrets: Optional[Dict[str, str]] = None,
        # Read secret variables from a file in yaml format,
        secrets_file: Optional[Path] = None,
        # Read secret variables from AWS Secrets Manager,
        aws_secret: Optional[Any] = None,
        # Configure the Secret name used for env variables that are Secret,
        secret_name: Optional[str] = None,
        # Container volumes,
        # Configure workspace volume,
        # Mount the workspace directory on the container,
        mount_workspace: bool = False,
        workspace_volume_name: Optional[str] = None,
        # Path to mount the workspace volume under,
        # This is the parent directory for the workspace on the container,
        # i.e. the ws is mounted as a subdir in this dir,
        # eg: if ws name is: idata, workspace_dir would be: /workspaces/idata,
        # eg: if ws name is: idata, workspace_root would be: /mnt/workspaces/idata,
        workspace_mount_container_path: str = "/mnt/workspaces",
        # NOTE: On DockerContainers the local workspace_root_path is mounted under workspace_mount_container_path,
        # because we assume that DockerContainers are running locally on the user's machine,
        # On K8sContainers, we load the workspace_dir from git using a git-sync sidecar container,
        create_git_sync_sidecar: bool = True,
        create_git_sync_init_container: bool = True,
        git_sync_repo: Optional[str] = None,
        git_sync_branch: Optional[str] = None,
        git_sync_wait: int = 1,
        # When running k8s locally, we can mount the workspace using host path as well.,
        k8s_mount_local_workspace=False,
        # Configure resources volume - only on docker,
        # Superset resources directory relative to the workspace_root,
        # This directory contains all the files required by superset.,
        # eg: docker-bootstrap.sh,
        # This dir is mounted to the `/app/docker` directory on the container,
        mount_resources: bool = False,
        resources_dir: str = "workspace/superset",
        resources_dir_container_path: str = "/app/docker",
        resources_volume_name: Optional[str] = None,
        # Configure the deployment,
        deploy_name: Optional[str] = None,
        pod_name: Optional[str] = None,
        replicas: int = 1,
        pod_annotations: Optional[Dict[str, str]] = None,
        pod_node_selector: Optional[Dict[str, str]] = None,
        deploy_restart_policy: RestartPolicy = RestartPolicy.ALWAYS,
        termination_grace_period_seconds: Optional[int] = None,
        # Add deployment labels,
        deploy_labels: Optional[Dict[str, Any]] = None,
        # Determine how to spread the deployment across a topology,
        # Key to spread the pods across,
        topology_spread_key: Optional[str] = None,
        # The degree to which pods may be unevenly distributed,
        topology_spread_max_skew: Optional[int] = None,
        # How to deal with a pod if it doesn't satisfy the spread constraint.,
        topology_spread_when_unsatisfiable: Optional[
            Literal["DoNotSchedule", "ScheduleAnyway"]
        ] = None,
        # Configure the app service,
        create_app_service: bool = True,
        app_svc_name: Optional[str] = None,
        app_svc_type: Optional[ServiceType] = None,
        # The port that will be exposed by the service.,
        app_svc_port: int = 8088,
        # The node_port that will be exposed by the service if app_svc_type = ServiceType.NODE_PORT,
        app_node_port: Optional[int] = None,
        # The app_target_port is the port to access on the pods targeted by the service.,
        # It can be the port number or port name on the pod.,
        app_target_port: Optional[Union[str, int]] = None,
        # Extra ports exposed by the app service,
        app_svc_ports: Optional[List[CreatePort]] = None,
        # Add labels to app service,
        app_svc_labels: Optional[Dict[str, Any]] = None,
        # Add annotations to app service,
        app_svc_annotations: Optional[Dict[str, str]] = None,
        # If ServiceType == LoadBalancer,
        ws_svc_health_check_node_port: Optional[int] = None,
        ws_svc_internal_taffic_policy: Optional[str] = None,
        ws_svc_load_balancer_class: Optional[str] = None,
        ws_svc_load_balancer_ip: Optional[str] = None,
        ws_svc_load_balancer_source_ranges: Optional[List[str]] = None,
        ws_svc_allocate_load_balancer_node_ports: Optional[bool] = None,
        # Configure K8s rbac: use a separate Namespace, ServiceAccount,,
        # ClusterRole & ClusterRoleBinding,
        use_rbac: bool = False,
        # Create a Namespace with name ns_name & default values,
        ns_name: Optional[str] = None,
        # Provide the full Namespace definition,
        namespace: Optional[CreateNamespace] = None,
        # Create a ServiceAccount with name sa_name & default values,
        sa_name: Optional[str] = None,
        # Provide the full ServiceAccount definition,
        service_account: Optional[CreateServiceAccount] = None,
        # Create a ClusterRole with name sa_name & default values,
        cr_name: Optional[str] = None,
        # Provide the full ClusterRole definition,
        cluster_role: Optional[CreateClusterRole] = None,
        # Create a ClusterRoleBinding with name sa_name & default values,
        crb_name: Optional[str] = None,
        # Provide the full ClusterRoleBinding definition,
        cluster_role_binding: Optional[CreateClusterRoleBinding] = None,
        # Other args,
        # Set SUPERSET_LOAD_EXAMPLES = "yes",
        load_examples: bool = False,
        print_env_on_load: bool = True,
        # Add extra Kubernetes resources,
        extra_secrets: Optional[List[CreateSecret]] = None,
        extra_config_maps: Optional[List[CreateConfigMap]] = None,
        extra_storage_classes: Optional[List[CreateStorageClass]] = None,
        extra_services: Optional[List[CreateService]] = None,
        extra_deployments: Optional[List[CreateDeployment]] = None,
        extra_custom_objects: Optional[List[CreateCustomObject]] = None,
        extra_crds: Optional[List[CreateCustomResourceDefinition]] = None,
        extra_pvs: Optional[List[CreatePersistentVolume]] = None,
        extra_pvcs: Optional[List[CreatePVC]] = None,
        extra_containers: Optional[List[CreateContainer]] = None,
        extra_init_containers: Optional[List[CreateContainer]] = None,
        extra_ports: Optional[List[CreatePort]] = None,
        extra_volumes: Optional[List[CreateVolume]] = None,
        # If True, use cached resources
        # i.e. skip resource creation/deletion if active resources with the same name exist.
        use_cache: bool = True,
        **extra_kwargs,
    ):
        super().__init__(
            name=name,
            version=version,
            enabled=enabled,
            image_name=image_name,
            image_tag=image_tag,
            entrypoint=entrypoint,
            command=command,
            install_requirements=install_requirements,
            requirements_file_path=requirements_file_path,
            wait_for_db=wait_for_db,
            db_app=db_app,
            db_user=db_user,
            db_password=db_password,
            db_schema=db_schema,
            db_host=db_host,
            db_port=db_port,
            db_dialect=db_dialect,
            wait_for_redis=wait_for_redis,
            redis_app=redis_app,
            redis_host=redis_host,
            redis_port=redis_port,
            redis_driver=redis_driver,
            container_name=container_name,
            superset_config_path=superset_config_path,
            flask_env=flask_env,
            superset_env=superset_env,
            python_path=python_path,
            container_labels=container_labels,
            container_detach=container_detach,
            container_auto_remove=container_auto_remove,
            container_remove=container_remove,
            container_user=container_user,
            container_stdin_open=container_stdin_open,
            container_tty=container_tty,
            container_healthcheck=container_healthcheck,
            container_hostname=container_hostname,
            container_platform=container_platform,
            container_working_dir=container_working_dir,
            container_restart_policy_docker=container_restart_policy_docker,
            container_volumes_docker=container_volumes_docker,
            container_ports_docker=container_ports_docker,
            image_pull_policy=image_pull_policy,
            open_container_port=open_container_port,
            container_port=container_port,
            container_port_name=container_port_name,
            container_host_port=container_host_port,
            open_app_port=open_app_port,
            app_port=app_port,
            app_port_name=app_port_name,
            app_host_port=app_host_port,
            env=env,
            env_file=env_file,
            config_map_name=config_map_name,
            secrets=secrets,
            secrets_file=secrets_file,
            aws_secret=aws_secret,
            secret_name=secret_name,
            mount_workspace=mount_workspace,
            workspace_volume_name=workspace_volume_name,
            workspace_mount_container_path=workspace_mount_container_path,
            create_git_sync_sidecar=create_git_sync_sidecar,
            create_git_sync_init_container=create_git_sync_init_container,
            git_sync_repo=git_sync_repo,
            git_sync_branch=git_sync_branch,
            git_sync_wait=git_sync_wait,
            k8s_mount_local_workspace=k8s_mount_local_workspace,
            mount_resources=mount_resources,
            resources_dir=resources_dir,
            resources_dir_container_path=resources_dir_container_path,
            resources_volume_name=resources_volume_name,
            deploy_name=deploy_name,
            pod_name=pod_name,
            replicas=replicas,
            pod_annotations=pod_annotations,
            pod_node_selector=pod_node_selector,
            deploy_restart_policy=deploy_restart_policy,
            termination_grace_period_seconds=termination_grace_period_seconds,
            deploy_labels=deploy_labels,
            topology_spread_key=topology_spread_key,
            topology_spread_max_skew=topology_spread_max_skew,
            topology_spread_when_unsatisfiable=topology_spread_when_unsatisfiable,
            create_app_service=create_app_service,
            app_svc_name=app_svc_name,
            app_svc_type=app_svc_type,
            app_svc_port=app_svc_port,
            app_node_port=app_node_port,
            app_target_port=app_target_port,
            app_svc_ports=app_svc_ports,
            app_svc_labels=app_svc_labels,
            app_svc_annotations=app_svc_annotations,
            ws_svc_health_check_node_port=ws_svc_health_check_node_port,
            ws_svc_internal_taffic_policy=ws_svc_internal_taffic_policy,
            ws_svc_load_balancer_class=ws_svc_load_balancer_class,
            ws_svc_load_balancer_ip=ws_svc_load_balancer_ip,
            ws_svc_load_balancer_source_ranges=ws_svc_load_balancer_source_ranges,
            ws_svc_allocate_load_balancer_node_ports=ws_svc_allocate_load_balancer_node_ports,
            use_rbac=use_rbac,
            ns_name=ns_name,
            namespace=namespace,
            sa_name=sa_name,
            service_account=service_account,
            cr_name=cr_name,
            cluster_role=cluster_role,
            crb_name=crb_name,
            cluster_role_binding=cluster_role_binding,
            load_examples=load_examples,
            print_env_on_load=print_env_on_load,
            extra_secrets=extra_secrets,
            extra_config_maps=extra_config_maps,
            extra_storage_classes=extra_storage_classes,
            extra_services=extra_services,
            extra_deployments=extra_deployments,
            extra_custom_objects=extra_custom_objects,
            extra_crds=extra_crds,
            extra_pvs=extra_pvs,
            extra_pvcs=extra_pvcs,
            extra_containers=extra_containers,
            extra_init_containers=extra_init_containers,
            extra_ports=extra_ports,
            extra_volumes=extra_volumes,
            use_cache=use_cache,
            extra_kwargs=extra_kwargs,
        )