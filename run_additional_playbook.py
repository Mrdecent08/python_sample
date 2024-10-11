import subprocess
import json

def run_additional_playbook():
    command = "ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_STDOUT_CALLBACK=json ansible-playbook tasks/install_python3.yml -u root --ask-pass --ssh-extra-args='-F /root/.ansible/ssh_config'"
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if result.returncode == 0:
            try:
                output_json = json.loads(result.stdout)
                
                stats = output_json.get('stats', {})
                
                for host, stat in stats.items():
                    print(f"Host: {host}")
                    print(f"  Changed: {stat['changed']}")
                    print(f"  Failures: {stat['failures']}")
                    print(f"  Ignored: {stat['ignored']}")
                    print(f"  OK: {stat['ok']}")
                    print(f"  Rescued: {stat['rescued']}")
                    print(f"  Skipped: {stat['skipped']}")
                    print(f"  Unreachable: {stat['unreachable']}")
                    print("-" * 40)
            except json.JSONDecodeError:
                print("Error parsing JSON output.")
        else:
            print("Playbook execution failed:")
            print(result.stderr)  
    except subprocess.CalledProcessError as e:
        return str(e)
