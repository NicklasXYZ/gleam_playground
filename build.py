"""
Python script for automatically building and pushing docker images to docker hub.
"""
import os
import argparse
from tempfile import TemporaryDirectory
import configparser
import subprocess
import shutil


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    return shutil.which(name) is not None


def run_subprocess(commandline_args):
    """
    """
    print("::SUBPROCESS COMMANDLINE ARGS: ", commandline_args)
    s = subprocess.Popen(commandline_args, stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT, shell = True)
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
    parser.add_argument("-user", "--user",
        required = True,
        type = str,
        help = "Specify a docker hub user.",
    )
    parser.add_argument("-version", "--version",
        required = False,
        default = "latest",
        type = str,
        help = "Specify a docker hub user.",
    )
    parser.add_argument("-settings", "--settings",
        required = True,
        type = str,
        help = "Specify the relative path to the settings directory.",
    )
    parser.add_argument("-service", "--service",
        required = False,
        default = None,
        type = str,
        help = "Specify which service to build.",
        nargs="+",
    )
    parser.add_argument("-action", "--action",
        required = False,
        default="build",
        type = str,
        choices = ["build", "push"],
        help = "Specify whether to build or push an image to Docker Hub.",
    )


def add_parser_arguments(parser):
    # Add required commandline arguments:
    add_required_parser_arguments(parser)


def parse_config(config_files):
    config = configparser.ConfigParser()
    try:
        config.read(config_files)
        return config
    except IOError as e:
        print("INFO : File ", args.config_file, " not accessible!")
        print("Error: ", e)
        raise SystemExit


def checks():
    # Make sure the appropriate programs are installed
    required_programs = ["docker"]
    for program in required_programs:
        if not is_tool(program):
            raise Exception("Program %r is not installed " % (program))
    

def docker_build(path: str, image_name: str, dockerfile: str = "Dockerfile"):
    command = f"docker build {path} --file {dockerfile} --tag {image_name}"
    run_subprocess(command)


def docker_run(image_name: str, env_file: str, host_path: str, container_path: str): 
    command = f"docker run --env-file {env_file} -v {host_path}:{container_path} {image_name}"
    run_subprocess(command)


def docker_push(image_name: str):
    command = f"docker push {image_name}"
    run_subprocess(command)


def docker_remove(image_name: str): 
    command = f"docker rmi -f {image_name}"
    run_subprocess(command)


# # Generic function for building a service
# def build_generic_svc(svc_dir, svc_tag, common_files_dir = None, dockerfile = "Dockerfile"):
#     # Create a temporary directory for building service
#     with TemporaryDirectory() as td0:
#         # Copy necessary files to temporary build directory
#         if common_files_dir is not None:
#             shutil.copytree(common_files_dir, os.path.join(td0, common_files_dir))
#         for directory in os.listdir(svc_dir):
#             if os.path.isdir(os.path.join(svc_dir, directory)):
#                 # Copy directory
#                 shutil.copytree(
#                     os.path.join(svc_dir, directory),
#                     os.path.join(td0, directory),
#                 )
#             else:
#                 # Copy file
#                 shutil.copy(
#                     os.path.join(svc_dir, directory),
#                     os.path.join(td0, directory),
#                 )
#         # Build image
#         docker_build(
#             path = td0,
#             image_name = svc_tag,
#             dockerfile = os.path.join(td0, dockerfile),
#         )


# Build service 'dashboard'
def build_frontend_svc(service_directory: str, settings_directory: str):
    ignore = ["node_modules"]
    # Parse configuration files
    config_file = os.path.join(*[settings_directory, "gleam-playground-settings.conf"])
    if not os.path.exists(config_file):
        raise ValueError(f"The config file: {config_file} could not be found!")
    config = parse_config([
        os.path.join(*[settings_directory, "gleam-playground-settings.conf"]),
    ])
    # Create a temporary directory for building service
    with TemporaryDirectory() as td0:
        # Loop through each section in the environment variables files that were read
        # in and construct a single file with all the necessary environment variables 
        with open(os.path.join(td0, ".env"), "w") as f:
            for section in config._sections:
                for key, value in config._sections[section].items():
                    # Make sure the key value is in upper case
                    f.write(f"{key.upper()}={value}\n")
        # Copy necessary files to temporary build directory 
        # shutil.copytree(COMMON_FILES_DIR, os.path.join(td0, COMMON_FILES_DIR))
        for directory in os.listdir(service_directory):
            if directory not in ignore:
                if os.path.isdir(os.path.join(service_directory, directory)):
                    # Copy directory
                    shutil.copytree(
                        os.path.join(service_directory, directory),
                        os.path.join(td0, directory),
                    )
                else:
                    # Copy file
                    shutil.copy(
                        os.path.join(service_directory, directory),
                        os.path.join(td0, directory),
                    )
        # Build image
        docker_build(
            path = td0,
            image_name = "dummy",
            dockerfile = os.path.join(td0, "Dockerfile0"),
        )
        docker_run(
            image_name = "dummy",
            env_file = os.path.join(td0, ".env"),
            host_path = os.path.join(td0, "build"),
            # NOTE: This path should correspond to the WORKDIR path set in 'Dockerfile0'
            container_path = "/tmp/web/build",
        )
        docker_build(
            path = td0,
            image_name = "nicklasxyz/gleam-playground-frontend:latest",
            dockerfile = os.path.join(td0, "Dockerfile1"),
        )
        docker_remove(
            image_name = "dummy",
        )


def main(args):
    if args.action.lower() == "build":
        if "frontend" in args.service:
            build_frontend_svc(
                service_directory = "frontend",
                settings_directory = args.settings,
            )
    elif args.action.lower() == "push":
        if "frontend" in args.service:
            # docker_push(image_name = f"{args.user}/gleam-playground-frontend:{args.version}")
            docker_push(image_name = f"nicklasxyz/gleam-playground-frontend:latest")


if __name__ == "__main__":
    # Run checks before generating files...
    checks()
    # Parse commandline arguments and configs
    args = parse_commandline_args()
    # Main call
    main(args = args)
