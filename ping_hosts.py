import subprocess
def ping_hosts():
    command = "ANSIBLE_HOST_KEY_CHECKING=False ansible all -m ping -u root --ask-pass --ssh-extra-args='-F /root/.ansible/ssh_config'"
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(f"Command succeeded with output:\n{result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error:\n{e.stderr}")
        return e.stderr


def format_ping_result(raw_result):
    """Formats the ping result data into a human-readable format with custom titles."""
    display_string = "Ping Results:\n\n"
    # Split the result by servers
    lines = raw_result.strip().splitlines()
    for line in lines:
        if "SUCCESS" in line:
            server_name = line.split("|")[0].strip()
            display_string += f"Server: {server_name}\n"
        elif '"ping":' in line:
            ping_status = line.split(":")[1].strip().strip('",')
            display_string += f"  - Ping Response: {ping_status}\n"  # Custom title
        elif '"discovered_interpreter_python":' in line:
            interpreter = line.split(":")[1].strip().strip('",')
            display_string += f"  - Python Interpreter Details: {interpreter}\n"  # Custom title
        elif '"changed":' in line:
            changed_status = line.split(":")[1].strip().strip(',')
            display_string += f"  - Was the Server Updated?: {changed_status}\n"  # Custom title
        display_string += "\n"
    display_string += "=" * 50 + "\n\n"
    return display_string
