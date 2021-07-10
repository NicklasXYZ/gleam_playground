"""
Python script for automatically generating a subset of the necessary Kubernetes
manifests for the Gleam playground.

Resource: https://github.com/kubernetes-client/python/tree/master/kubernetes/docs

TODO: Simplify... Duplicate code can be collected in certain places.
"""
import os
import argparse
import yaml
from tempfile import TemporaryDirectory
from types import MethodType
from kubernetes import client
import configparser
import subprocess
import shutil

# Kubernetes manifests output directory
# The value is set in main()
OUTPUT_DIR = ""
 
def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    return shutil.which(name) is not None

def run_subprocess(commandline_args):
    """
    """
    print("::SUBPROCESS COMMANDLINE ARGS: ", commandline_args)
    s = subprocess.Popen(commandline_args, stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT, shell=True)
    (stdout_data, stderr_data) = s.communicate()
    print("::SUBPROCESS STDOUT          : ")
    for string in stdout_data.decode("utf-8").split("\n"):
        print(string)
    print("::SUBPROCESS STDERR          : ")
    for string in str(stderr_data).split("\n"):
        print(string)
    # Check the returncode to see whether the process terminated normally
    if s.returncode == 0:
        print("INFO: Subprocess exited normally with return code: " + str(s.returncode))
    else:
        print("INFO: Subprocess exited with non-zero return code: " + str(s.returncode))
        raise SystemExit

def parse_commandline_args(args_list = None):
    """ Setup, parse and validate given commandline arguments.
    """
    # Create main parser
    parser = argparse.ArgumentParser(description = "")
    add_parser_arguments(parser)
    # Parse commandline arguments
    args = parser.parse_args(args_list)
    return args

def add_required_parser_arguments(parser):
    parser.add_argument("-config_file", "--config_file",
        required = False,
        type = str,
        help = "Specify the name of the config file to parse.",
    )
    parser.add_argument("-xconfig_files", "--xconfig_files",
        required = False,
        default = None,
        type = str,
        help = "Specify an additional config file to parse.",
        nargs="+",
    )
    parser.add_argument("-account_name", "--account_name",
        required = False,
        default = "nicklasxyz",
        type = str,
        help = "Specify a dockerhub account where docker images are stored.",
    )
    parser.add_argument("-service_name", "--service_name",
        required = True,
        type = str,
        help = "Specify the name of the service to generate files for."
    )
    parser.add_argument("-namespace", "--namespace",
        required = False,
        default = "default",
        type = str,
        help = "Specify the name of the service to generate files for.",
    )
    parser.add_argument("-xnamespaces", "--xnamespaces",
        required = False,
        default = None,
        type = str,
        help = "Specify additional namespaces that we need to define secrets in.",
        nargs="+",
    )
    parser.add_argument("-kubeconfig", "--kubeconfig",
        required = False,
        default = None,
        type = str,
        help = "Used by SealedSecrets. Specify the path to the KUBECONFIG " + \
            "of the target kubernetes cluster.",
    )
    parser.add_argument("-sealed_secrets_namespace", "--sealed_secrets_namespace",
        required = False,
        default = "sealed-secrets",
        type = str,
        help = "Used by SealedSecrets. Specify the namespace of the " + \
            "SealedSecrets controller.",
    )
    parser.add_argument("-output_dir", "--output_dir",
        required = False,
        default = "manifests",
        type = str,
        help = "Specify the output directory for the generated " + \
            "manifests.",
    )

def add_parser_arguments(parser):
    # Add required commandline arguments:
    add_required_parser_arguments(parser)

def parse_config(args):
    _args = [args.config_file]
    try:
        if args.xconfig_files is not None:
            _args.extend([f for f in args.xconfig_files])    
    except AttributeError:
        pass
    config = configparser.ConfigParser()
    try:
        config.read(_args)
        return config
    except IOError as e:
        print("INFO : File ", args.config_file, " not accessible!")
        print("Error: ", e)
        raise SystemExit

def _camelized_to_dict(self):
    """Override the default k8s object to_dict to camelize it's keys"""
    result = {}
    for attr, camel_attr in self.attribute_map.items():
        value = getattr(self, attr)

        if isinstance(value, list):
            result[camel_attr] = list(
                map(
                    lambda x: _camelized_to_dict(x) if hasattr(x, "to_dict") else x,
                    value,
                )
            )
        elif hasattr(value, "to_dict"):
            result[camel_attr] = _camelized_to_dict(value)
        elif isinstance(value, dict):
            result[camel_attr] = dict(
                map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict")
                    else item,
                    value.items(),
                )
            )
        else:
            # ignore None values - we don't need them for the output
            if value is not None:
                result[camel_attr] = value
    return result

def persistent_volume_claim_template(pvc_name, pvc_resources, namespace):
    pvc = client.V1PersistentVolumeClaim(
        api_version="v1",
        kind="PersistentVolumeClaim",
        metadata=client.V1ObjectMeta(
            name=pvc_name,
            namespace=namespace,
            labels={"io.service": pvc_name},
        ),
        spec=client.V1PersistentVolumeClaimSpec(
            # Use k3s native storage class for local path storage
            storage_class_name="local-path",
            access_modes=["ReadWriteOnce"],
            resources=pvc_resources,
        ),
    )
    return pvc

def deployment_template(
    service_name,
    image_name,
    image_version,
    namespace,
    container_ports=None,
    container_args=None,
    container_env_from=None,
    container_resources=None,
    container_volume_mounts=None,
    volumes=None,
    startup_probe=None,
    liveness_probe=None,
    lifecycle=None,
    security_context=None,
    host_network=False,
    container_replicas=1,
    ):
    # Configure Pod template container
    container = client.V1Container(
        name=service_name,
        image="{}:{}".format(image_name, image_version),
        ports=container_ports,
        args=container_args,
        env_from=container_env_from,
        resources=container_resources,
        volume_mounts=container_volume_mounts,
        startup_probe=startup_probe,
        liveness_probe=liveness_probe,
        lifecycle=lifecycle,
        security_context=security_context,
    )
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(
            labels={"io.service": service_name},
        ),
        spec=client.V1PodSpec(
            containers=[container],
            volumes=volumes,
            host_network=host_network,
        ),
    )
    # Create the specification of the deployment
    spec = client.V1DeploymentSpec(
        replicas=container_replicas,
        template=template,
        selector={"matchLabels": {"io.service": service_name}},
        strategy=client.V1DeploymentStrategy(type="Recreate"),
    )
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=service_name, namespace=namespace),
        spec=spec,
    )
    return deployment

def service_template(service_name, service_type, service_ports, namespace):
    pvc = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(
            name=service_name,
            namespace=namespace,
            labels={"io.service": service_name},
        ),
        spec=client.V1ServiceSpec(
            type=service_type,
            ports=service_ports,
            selector={"io.service": service_name},
        ),
    )
    return pvc

def namespace_template(namespace):
    ns = client.V1Namespace(
        api_version="v1",
        kind="Namespace",
        metadata=client.V1ObjectMeta(
            name=namespace,
        ),
    )
    return ns

def create_target_dir(dirname):
    # Create target directory & all intermediate directories if they do no exist
    try:
        os.makedirs(os.path.join(OUTPUT_DIR, dirname))
        print("--> Creating directory: " , dirname)
    except FileExistsError:
        pass

def to_yaml(k8s_object, filename, dirname):
    """Convert a k8s object to a yaml file"""
    create_target_dir(dirname)
    print("--> Creating file     : ", os.path.join(OUTPUT_DIR, dirname, filename))
    with open(os.path.join(OUTPUT_DIR, dirname, filename), "w+") as file:
        yaml.dump(
            k8s_object,
            file,
            default_flow_style=False
        )

def create_gleam_playground_db_manifests(
    config,
    account_name,
    service_name,
    namespace,
    parent_service_name=None,
    secret_ref_name=None
    ):
    """Generate k8s manifests pertaining to the 'gleam-playground-db' app."""
    port = int(config._sections.get("database").get("postgres_port"))
    pvc_name = service_name + "-claim"

    ###
    ### PersistentVolumeClaim
    ###
    k8s_pvc_obj = persistent_volume_claim_template(
        pvc_name=pvc_name,
        pvc_resources=client.V1ResourceRequirements(
            requests={"storage": "5Gi"},
        ),
        namespace=namespace,
    )
    # Override the default to_dict method so we can update the k8s keys
    k8s_pvc_obj.to_dict = MethodType(_camelized_to_dict, k8s_pvc_obj)
    k8s_pvc_obj = k8s_pvc_obj.to_dict()
    to_yaml(k8s_pvc_obj, service_name + "-pvc.yaml", service_name)

    ###
    ### Deployment
    ###
    k8s_deployment_obj = deployment_template(
        service_name=service_name,
        image_name="postgres",
        image_version="latest",
        namespace=namespace,
        container_ports=[
            client.V1ContainerPort(container_port=port)
        ],
        container_env_from=[
            client.V1EnvFromSource(
                secret_ref=client.V1SecretEnvSource(name=secret_ref_name, optional=False),
            )
        ],
        container_resources=client.V1ResourceRequirements(
            requests={"cpu": "250m", "memory": "500Mi"},
        ),
        container_volume_mounts=[
            client.V1VolumeMount(
                mount_path="/var/lib/postgresql/data",
                name=pvc_name,
            ),
        ],
        volumes=[
            client.V1Volume(
                name=pvc_name,
                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                    claim_name=pvc_name,
                    read_only=False,
                ),
            ),
        ],
    )
    # Override the default to_dict method so we can update the k8s keys
    k8s_deployment_obj.to_dict = MethodType(_camelized_to_dict, k8s_deployment_obj)
    k8s_deployment_obj = k8s_deployment_obj.to_dict()
    to_yaml(k8s_deployment_obj, service_name + "-deployment.yaml", service_name)

    ###
    ### Service
    ###
    k8s_service_obj = service_template(
        service_name = service_name,
        service_type = "ClusterIP",
        service_ports = [
            client.V1ServicePort(
                name=str(port),
                # Port that is exposed by the service
                port=port,
                # Number or name of the port to access on the pods targeted by the service
                target_port=port,
            ),
        ],
        namespace=namespace,
    )
    # Override the default to_dict method so we can update the k8s keys
    k8s_service_obj.to_dict = MethodType(_camelized_to_dict, k8s_service_obj)
    k8s_service_obj = k8s_service_obj.to_dict()
    to_yaml(k8s_service_obj, service_name + "-service.yaml", service_name)

def create_gleam_playground_pgbouncer_manifests(
    config,
    account_name,
    service_name,
    namespace,
    parent_service_name=None,
    secret_ref_name=None
    ):
    """Generate k8s manifests pertaining to the 'gleam-playground-pgbouncer' app."""
    port = int(config._sections.get("database").get("postgres_port"))

    ###
    ### Deployment
    ###
    k8s_deployment_obj = deployment_template(
        service_name=service_name,
        image_name="edoburu/pgbouncer",
        namespace=namespace,
        image_version="1.9.0",
        container_ports=[
            client.V1ContainerPort(container_port=port)
        ],
        container_env_from=[
            client.V1EnvFromSource(
                secret_ref=client.V1SecretEnvSource(name=secret_ref_name, optional=False),
            )
        ],
        # container_resources=client.V1ResourceRequirements(
        #     requests={"cpu": "100m", "memory": "200Mi"},
        #     limits={"cpu": "500m", "memory": "500Mi"},
        # ),
        liveness_probe=client.V1Probe(
            tcp_socket=client.V1TCPSocketAction(
                port=port, # and host is pod IP
            ),
            # How often (in seconds) to perform the probe
            period_seconds=60,
        ),
        lifecycle=client.V1Lifecycle(
            pre_stop=client.V1Handler(
                _exec=client.V1ExecAction(
                    # Allow existing queries clients to complete within 120 seconds
                    command=["/bin/sh", "-c", "killall -INT pgbouncer && sleep 120"],
                ),
            ),
        ),
        security_context=client.V1SecurityContext(
            allow_privilege_escalation=False,
            capabilities=client.V1Capabilities(
                drop=["all"],
            ),
        ),
    )
    # Override the default to_dict method so we can update the k8s keys
    k8s_deployment_obj.to_dict = MethodType(_camelized_to_dict, k8s_deployment_obj)
    k8s_deployment_obj = k8s_deployment_obj.to_dict()
    to_yaml(k8s_deployment_obj, service_name + "-deployment.yaml", service_name)

    ###
    ### Service
    ###
    k8s_service_obj = service_template(
        service_name = service_name,
        service_type = "ClusterIP",
        service_ports = [
            client.V1ServicePort(
                name=str(port),
                # Port that is exposed by the service
                port=port,
                # Number or name of the port to access on the pods targeted by the service
                target_port=port,
            ),
        ],
        namespace=namespace,
    )
    # Override the default to_dict method so we can update the k8s keys
    k8s_service_obj.to_dict = MethodType(_camelized_to_dict, k8s_service_obj)
    k8s_service_obj = k8s_service_obj.to_dict()
    to_yaml(k8s_service_obj, service_name + "-service.yaml", service_name)

def create_gleam_playground_frontend_manifests(
    config,
    account_name,
    service_name,
    namespace,
    parent_service_name=None,
    secret_ref_name=None
    ):
    """Generate k8s manifests pertaining to the 'gleam-playground-frontend' app."""
    port = int(config._sections.get("gleam-playground").get("nginx_port"))

    ###
    ### Deployment
    ###
    k8s_deployment_obj = deployment_template(
        service_name=service_name,
        image_name=os.path.join(account_name, service_name),
        namespace=namespace,
        image_version="latest",
        container_replicas=2,
    )
    # Override the default to_dict method so we can update the k8s keys
    k8s_deployment_obj.to_dict = MethodType(_camelized_to_dict, k8s_deployment_obj)
    k8s_deployment_obj = k8s_deployment_obj.to_dict()
    to_yaml(k8s_deployment_obj, service_name + "-deployment.yaml", service_name)

    ###
    ### Service
    ###
    k8s_service_obj = service_template(
        service_name = service_name,
        service_type = "ClusterIP",
        service_ports = [
            client.V1ServicePort(
                name=str(port),
                # Port that is exposed by the service
                port=port,
                # Number or name of the port to access on the pods targeted by the service
                target_port=port,
            ),
        ],
        namespace=namespace,
    )
    # Override the default to_dict method so we can update the k8s keys
    k8s_service_obj.to_dict = MethodType(_camelized_to_dict, k8s_service_obj)
    k8s_service_obj = k8s_service_obj.to_dict()
    to_yaml(k8s_service_obj, service_name + "-service.yaml", service_name)


def create_redis_manifests(
    config,
    account_name,
    service_name,
    namespace,
    parent_service_name=None,
    secret_ref_name=None
    ):
    """Generate k8s manifests pertaining to the 'redis' microservice."""
    # Make sure that the host names align. Else other services will have 
    # problems connecting to redis, as one host name is given here but
    # another host name is set in the settings file.
    assert config._sections.get("redis").get("redis_host") == service_name
    port = int(config._sections.get("redis").get("redis_port"))

    ###
    ### Deployment
    ###
    k8s_deployment_obj = deployment_template(
        service_name=service_name,
        image_name="redis",
        namespace=namespace,
        image_version="latest",
        container_ports=[
            client.V1ContainerPort(container_port=port)
        ],
        container_args=["redis-server"],
        container_resources=client.V1ResourceRequirements(
            requests={"cpu": "500m", "memory": "1000Mi"},
        ),
    )
    # Override the default to_dict method so we can update the k8s keys
    k8s_deployment_obj.to_dict = MethodType(_camelized_to_dict, k8s_deployment_obj)
    k8s_deployment_obj = k8s_deployment_obj.to_dict()
    to_yaml(k8s_deployment_obj, service_name + "-deployment.yaml", service_name)

    ###
    ### Service
    ###
    k8s_service_obj = service_template(
        service_name = service_name,
        service_type = "ClusterIP",
        service_ports = [
            client.V1ServicePort(
                name=str(port),
                # Port that is exposed by the service
                port=port,
                # Number or name of the port to access on the pods targeted by the service
                target_port=port,
            ),
        ],
        namespace=namespace,
    )
    # Override the default to_dict method so we can update the k8s keys
    k8s_service_obj.to_dict = MethodType(_camelized_to_dict, k8s_service_obj)
    k8s_service_obj = k8s_service_obj.to_dict()
    to_yaml(k8s_service_obj, service_name + "-service.yaml", service_name)

def generate_sealed_secrets(
    config, 
    service_name,
    secret_name,
    kubeconfig,
    secret_namespace,
    sealed_secrets_namespace,
    ):
    # Make sure the kubeconfig is supplied. We need it for encrypting the data
    if kubeconfig is None:
        raise ValueError("Supply a path to the KUBECONFIG of the target kubernetes cluster!")
    # Create a temporary directory where we can hold the files
    with TemporaryDirectory() as td:
        sealed_secret_name = "sealed-" + secret_name + "-" + secret_namespace
        print("Name: ", sealed_secret_name)
        _in = f"{os.path.join(td, secret_name)}.yaml"
        _out = f"{os.path.join(td, sealed_secret_name)}.yaml"
        # Create ordinary secrets file
        command = ""
        for section in config._sections:
            for arg in config._sections[section]:
                command += f"--from-literal='{arg.upper()}={config._sections[section][arg]}' "
        command = "sudo k3s " + \
            f"kubectl create secret generic {secret_name} " + \
            command + \
            f"--namespace={secret_namespace} " + \
            "--dry-run=client " + \
            f"--output=yaml > {_in}"
        run_subprocess(command)
        # Create a sealed secrets file
        command = f"sudo kubeseal --kubeconfig={args.kubeconfig} " + \
        "--scope=cluster-wide " + \
        f"--controller-namespace={sealed_secrets_namespace} " + \
        f"--format=yaml < {_in} > {_out}"
        run_subprocess(command)
        # Delete ordinary secrets file
        run_subprocess(f"rm -f {_in}")
        # Create target directory if does not yet exist
        create_target_dir(service_name)
        # Move secrets file to the appropriate directory
        shutil.move(
            f"{_out}",
            os.path.join(OUTPUT_DIR, service_name, sealed_secret_name),
        )

def extend_args(config, service_name):
    # Add extra pgbouncer specific parameters and settings
    if "pgbouncer" not in config._sections:
        config.add_section("pgbouncer")
    config.set("pgbouncer","DB_HOST", service_name + "-db")
    config.set("pgbouncer","DB_USER", config["database"]["postgres_user"])
    config.set("pgbouncer","DB_PASSWORD", config["database"]["postgres_password"])
    return config

def validate_args(config, args):
    """Make sure all required database args are provided"""
    required_db_args = [
        "postgres_name", "postgres_db",
        "postgres_user", "postgres_password",
        "postgres_port",
        "postgres_data_dir",
    ]
    if "database" in config._sections:
        for var in required_db_args:
            assert var in config["database"]
    required_redis_args = [
        "redis_host", "redis_port",
    ]
    if "redis" in config._sections:
        for var in required_redis_args:
            assert var in config["redis"]

def checks():
    # Make sure the appropriate programs are installed
    required_programs = ["k3s", "kubeseal"]
    for program in required_programs:
        if not is_tool(program):
            raise Exception("Program %r is not installed " % (program))
    
def main(account_name, config, args):
    global OUTPUT_DIR
    OUTPUT_DIR = args.output_dir
    
    ###
    ### Create a namespace manifest
    ###
    # Override the default to_dict method so we can update the k8s keys
    k8s_ns_obj = namespace_template(args.namespace)
    k8s_ns_obj.to_dict = MethodType(_camelized_to_dict, k8s_ns_obj)
    k8s_ns_obj = k8s_ns_obj.to_dict()
    to_yaml(k8s_ns_obj, args.namespace + "-ns.yaml", "")

    if args.service_name == "redis":
        ###
        ### Create 'redis' manifests
        ###
        service_name = args.service_name
        # Validate redis args
        validate_args(config, args)
        create_redis_manifests(
            config=config,
            account_name=account_name,
            service_name=service_name,
            namespace=args.namespace,
        )
    elif args.service_name == "gleam-playground":
        service_name = args.service_name
        secret_ref_name = service_name + "-secret"
        # Validate database and redis args
        validate_args(config, args)
        # Extend config with extra database args
        config = extend_args(config, service_name)
        # Set db host. We should use pgbouncer
        config._sections["database"]["postgres_host"] = service_name + "-pgbouncer"
        generate_sealed_secrets(
            config=config,
            service_name=service_name, 
            secret_name=secret_ref_name,
            kubeconfig=args.kubeconfig,
            secret_namespace=args.namespace, 
            sealed_secrets_namespace=args.sealed_secrets_namespace,
        )
        if args.xnamespaces is not None:
            for namespace in args.xnamespaces:
                generate_sealed_secrets(
                    config=config,
                    service_name=service_name, 
                    secret_name=secret_ref_name,
                    kubeconfig=args.kubeconfig,
                    secret_namespace=namespace, 
                    sealed_secrets_namespace=args.sealed_secrets_namespace,
                )
        ###
        ### Create 'gleam-playground-db' manifests
        ###
        create_gleam_playground_db_manifests(
            config=config,
            account_name=account_name,
            service_name=service_name + "-db",
            secret_ref_name=secret_ref_name,    
            namespace=args.namespace,
        )
        ###
        ### Create 'gleam-playground-pgbouncer' manifests
        ###
        create_gleam_playground_pgbouncer_manifests(
            config=config,
            account_name=account_name,
            service_name=service_name + "-pgbouncer",
            secret_ref_name=secret_ref_name,
            namespace=args.namespace,
        )
        ###
        ### Create 'gleam-playground-frontend' manifests
        ###
        create_gleam_playground_frontend_manifests(
            config=config,
            account_name=account_name,
            service_name=service_name + "-frontend",
            secret_ref_name=secret_ref_name,
            namespace=args.namespace,
        )

if __name__ == "__main__":
    # Run checks before generating files...
    checks()
    # Parse commandline arguments and configs
    args = parse_commandline_args()
    config = parse_config(args)
    # Generate manifests for a particular service
    main(args.account_name, config, args)