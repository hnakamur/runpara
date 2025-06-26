#!/usr/bin/env python3
import argparse
import asyncio
import os
import shlex
import sys


version = "v0.0.1"


async def run_command_for_host(command):
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout_data, stderr_data = await process.communicate()
    result = stdout_data.decode()
    stderr_text = stderr_data.decode()
    if stderr_text != "":
        result = result + f"\nSTDERR:\n{stderr_text}"
    if process.returncode != 0:
        result = result + f"\nRETURNCODE:\n{process.returncode}"
    return result.rstrip("\n")


async def run(args):
    if args.version:
        print(version)
        return

    hosts = args.hosts.split()
    command_template = args.template

    if sys.stdin.isatty():
        print("Enter Command and EOF (Ctrl+D): ", end="", flush=True)
    command = sys.stdin.read().rstrip("\n")
    if command.strip() == "":
        raise ValueError("cannot execute empty command")
    quoted_command = shlex.quote(command)

    tasks = [
        run_command_for_host(
            command_template.format(
                host=host, command=command, quoted_command=quoted_command
            )
        )
        for host in hosts
    ]
    results = await asyncio.gather(*tasks)
    if any("\n" in result for result in results):
        for host, result in zip(hosts, results):
            print(f"=== {host} ===")
            print(result)
    else:
        for host, result in zip(hosts, results):
            print(f"{host} {result}")


async def main():
    try:
        default_template = os.environ.get(
            "RUNPARA_TEMPLATE", "ssh {host} {quoted_command}"
        )

        parser = argparse.ArgumentParser(
            prog="runpara",
            description="""Run a command on each target host in parallel.
            The command is supposed to be passed to stdin.""",
        )
        parser.add_argument("--hosts", "-H", help="Target hosts")
        parser.add_argument(
            "--template",
            "-t",
            default=default_template,
            help=f"""Command template for each host.
            Can contain {{host}}, {{command}}, {{quoted_command}}.
            Can be set by RUNPARA_TEMPLATE environment variable.
            Current default value: {default_template}""",
        )
        parser.add_argument(
            "--version", "-V", action="store_true", help="Show version and exit"
        )
        parser.set_defaults(func=run)
        args = parser.parse_args()
        if hasattr(args, "func"):
            await args.func(args)
        else:
            parser.print_help()
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


asyncio.run(main())
