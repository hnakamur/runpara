# runpara

**`runpara`** is a Python script that executes a given command in parallel across multiple hosts using asynchronous SSH or other customizable remote command templates.

## Features

* Executes shell commands in parallel on multiple target hosts.
* Accepts input from standard input (`stdin`) for interactive or piped command usage.
* Supports customizable command templates via CLI argument or environment variable.
* Displays results per host, including `stderr` and exit code if applicable.

## Usage

```bash
python3 runpara.py --hosts "host1 host2 host3"
```

You will be prompted to input a command via stdin (end with `Ctrl+D`):

```text
Enter Command and EOF (Ctrl+D): uptime
```

## Command-Line Options

* `--hosts`, `-H`
  Space-separated or newline-separated list of target hostnames or IP addresses.

* `--template`, `-t`
  Template for executing the command on each host.
  Available placeholders:

  * `{host}`: the hostname
  * `{command}`: the raw command
  * `{quoted_command}`: the shell-escaped command
    Defaults to:

  ```bash
  ssh {host} {quoted_command}
  ```

  You can also override this via the `RUNPARA_TEMPLATE` environment variable.

## Examples

Run `uptime` on multiple hosts via SSH:

```bash
echo "uptime" | python3 runpara.py -H "$(echo server{1..3})"
```

Use a custom execution method for [Incus](https://github.com/lxc/incus):

```bash
export RUNPARA_TEMPLATE='incus exec {host} -- {command}'
echo "df -h" | python3 runpara.py -H "$(seq -f container%02g 3)"
```

## Requirements

* Python 3.7 or newer
* SSH or any remote shell configured appropriately (depending on the template)

## License

MIT License
