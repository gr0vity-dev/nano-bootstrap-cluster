#!/usr/bin/python3
import argparse
import json
import asyncio


async def async_subprocess_run(command):
    proc = await asyncio.create_subprocess_exec(*command,
                                                stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    return stdout, stderr


async def list_instances_async():
    command = ["gcloud", "compute", "instances", "list", "--format", "json"]
    stdout, stderr = await async_subprocess_run(command)
    instances = json.loads(stdout)
    return instances


def escape_docker_tag(docker_tag):
    return docker_tag.replace('/', '-').replace(':', '-').replace('.',
                                                                  '-').lower()


def generate_instance_names(docker_tag, num_instances):
    safe_docker_tag = escape_docker_tag(docker_tag)
    return [f"{safe_docker_tag}-instance-{i}" for i in range(num_instances)]


async def create_instances_with_docker_tag(docker_tag, num_instances):
    instance_names = generate_instance_names(docker_tag, num_instances)
    create_tasks = [
        create_instance(docker_tag, instance_name)
        for instance_name in instance_names
    ]
    await asyncio.gather(*create_tasks)


async def create_instance(docker_tag, instance_name):
    zone = "europe-central2-a"
    startup_script_name = f"startup-script_{escape_docker_tag(docker_tag)}.sh"

    startup_script = f"""#!/bin/bash
    apt-get update
    apt-get install -y docker.io
    systemctl start docker
    systemctl enable docker
    docker run --restart=unless-stopped -d -p 54000:54000 -p 127.0.0.1:55000:55000 -p 127.0.0.1:57000:57000 -v nano:/root --name nanobeta {docker_tag} nano_node daemon --network=beta
    """

    with open(startup_script_name, "w") as f:
        f.write(startup_script)

    command = [
        "gcloud", "compute", "instances", "create", instance_name,
        "--metadata-from-file", f"startup-script={startup_script_name}",
        "--scopes", "default", "--image-family", "ubuntu-2204-lts",
        "--image-project", "ubuntu-os-cloud", "--machine-type", "e2-small",
        "--zone", zone
    ]
    print(f"Creating instance {instance_name} in zone {zone}...")
    stdout, stderr = await async_subprocess_run(command)


async def stop_instance(instance):
    instance_name = instance["name"]
    zone = instance["zone"].split("/")[-1]
    print(f"Stopping instance {instance_name} in zone {zone}...")
    command = [
        "gcloud", "compute", "instances", "stop", instance_name, "--zone", zone
    ]
    stdout, stderr = await async_subprocess_run(command)


async def stop_instances():
    instances = await list_instances_async()
    stop_tasks = [stop_instance(instance) for instance in instances]
    await asyncio.gather(*stop_tasks)


async def delete_instance(instance):
    instance_name = instance["name"]
    zone = instance["zone"].split("/")[-1]
    print(f"Deleting instance {instance_name} in zone {zone}...")
    command = [
        "gcloud", "compute", "instances", "delete", instance_name, "--zone",
        zone, "--quiet"
    ]
    stdout, stderr = await async_subprocess_run(command)


async def delete_instances():
    instances = await list_instances_async()
    delete_tasks = [delete_instance(instance) for instance in instances]
    await asyncio.gather(*delete_tasks)


async def restart_instance(instance):
    instance_name = instance["name"]
    zone = instance["zone"].split("/")[-1]
    print(f"Restarting instance {instance_name} in zone {zone}...")
    command = [
        "gcloud", "compute", "instances", "start", instance_name, "--zone",
        zone
    ]
    stdout, stderr = await async_subprocess_run(command)


async def restart_instances():
    instances = await list_instances_async()
    restart_tasks = [
        restart_instance(instance) for instance in instances
        if instance["status"] == "TERMINATED"
    ]
    await asyncio.gather(*restart_tasks)


def main():
    parser = argparse.ArgumentParser(
        description=
        "Betaboot: A tool for managing Google Cloud instances running Nano.")
    parser.add_argument("--create",
                        nargs="+",
                        metavar=("TAG", "NUM_INSTANCES"),
                        help="Docker tag and number of instances to create")
    parser.add_argument("--stop",
                        action="store_true",
                        help="Stop all instances")
    parser.add_argument("--restart",
                        action="store_true",
                        help="Restart all terminated instances")
    parser.add_argument("--delete",
                        action="store_true",
                        help="Delete all instances")
    args = parser.parse_args()

    asyncio.run(main_async(args))


async def main_async(args):
    if args.create:
        create_tasks = [
            create_instances_with_docker_tag(args.create[i],
                                             int(args.create[i + 1]))
            for i in range(0, len(args.create), 2)
        ]
        await asyncio.gather(*create_tasks)

    if args.stop:
        await stop_instances()

    if args.restart:
        await restart_instances()

    if args.delete:
        await delete_instances()


if __name__ == "__main__":
    main()
