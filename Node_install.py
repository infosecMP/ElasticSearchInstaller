import subprocess
import json
import psutil
import socket
from termcolor import colored
import time
import sys

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        error_message = f"Error executing command: {e}\n{e.stderr.decode().strip()}"
        print(colored(error_message, 'red'))
        sys.exit(1)

def install_java():
    print_section("Installing Java...")
    run_command("sudo apt update")
    run_command("sudo apt install openjdk-17-jdk -y")
    print_ok()

def install_elasticsearch():
    print_section("Adding Elasticsearch GPG key and repository...")
    run_command("wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -")
    run_command("sudo sh -c 'echo \"deb https://artifacts.elastic.co/packages/8.x/apt stable main\" > /etc/apt/sources.list.d/elastic-8.x.list'")
    run_command("sudo apt update")
    print_ok()
    
    print_section("Installing Elasticsearch...")
    run_command("sudo apt install elasticsearch -y")
    print_ok()

def create_directories(data_path, logs_path):
    print_section(f"Creating directories {data_path} and {logs_path}...")
    run_command(f"sudo mkdir -p {data_path}")
    run_command(f"sudo mkdir -p {logs_path}")
    run_command(f"sudo chown -R elasticsearch:elasticsearch {data_path}")
    run_command(f"sudo chown -R elasticsearch:elasticsearch {logs_path}")
    print_ok()

def configure_elasticsearch(node_name, node_roles, network_host, seed_hosts, initial_master_nodes, cluster_name, data_path, logs_path):
    print_section("Configuring Elasticsearch...")
    config_path = "/etc/elasticsearch/elasticsearch.yml"
    config = {
        "cluster.name": cluster_name,
        "node.name": node_name,
        "node.roles": node_roles,
        "network.host": network_host,
        "discovery.seed_hosts": seed_hosts,
        "cluster.initial_master_nodes": initial_master_nodes,
        "bootstrap.memory_lock": True,
        "path.data": data_path,
        "path.logs": logs_path,
        "xpack.security.transport.ssl.enabled": True,
        "xpack.security.transport.ssl.verification_mode": "certificate",
        "xpack.security.transport.ssl.keystore.path": "/etc/elasticsearch/elastic-certificates.p12",
        "xpack.security.transport.ssl.truststore.path": "/etc/elasticsearch/elastic-certificates.p12"
    }
    
    with open(config_path, 'w') as f:
        for key, value in config.items():
            f.write(f"{key}: {json.dumps(value) if isinstance(value, list) else value}\n")
    
    run_command("sudo systemctl daemon-reload")
    run_command("sudo systemctl enable elasticsearch")
    run_command("sudo systemctl start elasticsearch")
    print_ok()

def generate_token():
    print_section("Generating enrollment token...")
    token = run_command("sudo /usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s node")
    print(f"Enrollment token: {token}")
    print_ok()
    return token

def join_cluster(enrollment_token):
    print_section("Joining the Elasticsearch cluster using the enrollment token...")
    run_command(f"sudo /usr/share/elasticsearch/bin/elasticsearch-join-cluster --enrollment-token {enrollment_token}")
    print_ok()

def set_jvm_heap():
    print_section("Setting JVM heap size...")
    total_memory = psutil.virtual_memory().total
    heap_size = total_memory // 2
    jvm_options_path = "/etc/elasticsearch/jvm.options.d/custom.options"
    with open(jvm_options_path, 'w') as f:
        f.write(f"-Xms{heap_size // (1024 ** 2)}m\n")
        f.write(f"-Xmx{heap_size // (1024 ** 2)}m\n")
    run_command("sudo systemctl restart elasticsearch")
    print_ok()

def get_real_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # connect to a public IP to get the real IP address
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def print_section(message):
    print(colored(f"\n{'='*50}\n{message}\n{'='*50}", 'yellow'))
    time.sleep(1)  # Sleep for 1 second for the animation effect

def print_ok():
    print(colored("OK", 'green'))

def main():
    print(colored("Elasticsearch Installation and Configuration Script", 'yellow'))

    # Step 1: Install Java
    install_java()

    # Step 2: Install Elasticsearch
    install_elasticsearch()

    # Step 3: Get user inputs for configuration
    print_section("User Input for Elasticsearch Configuration")
    node_name = input("Enter the node name: ")
    
    node_roles = input("Enter the node roles (comma-separated, e.g., master, data, ingest, coordinator): ").split(',')
    node_roles = [role.strip() for role in node_roles]

    current_ip = get_real_ip()
    network_host = input(f"Enter the network host IP address [{current_ip}]: ") or current_ip

    seed_hosts = input("Enter the seed hosts (comma-separated IP addresses): ").split(',')
    seed_hosts = [host.strip() for host in seed_hosts]

    initial_master_nodes = input("Enter the initial master nodes (comma-separated node names): ").split(',')
    initial_master_nodes = [node.strip() for node in initial_master_nodes]

    cluster_name = input("Enter the cluster name: ")

    data_path = "/var/data/elasticsearch"
    logs_path = "/var/log/elasticsearch"
    print_ok()

    # Step 4: Create directories for data and logs
    create_directories(data_path, logs_path)

    # Step 5: Configure Elasticsearch
    configure_elasticsearch(node_name, node_roles, network_host, seed_hosts, initial_master_nodes, cluster_name, data_path, logs_path)

    # Step 6: Token generation and cluster joining
    if 'master' in node_roles:
        is_first_master = input("Is this the first master node? (yes/no): ").strip().lower()
        if is_first_master == 'yes':
            enrollment_token = generate_token()
            print(f"Save this token and use it to join other nodes to the cluster: {enrollment_token}")
        else:
            enrollment_token = input("Enter the enrollment token to join the cluster: ")
            join_cluster(enrollment_token)
    else:
        enrollment_token = input("Enter the enrollment token to join the cluster: ")
        join_cluster(enrollment_token)

    # Step 7: Set JVM heap size
    set_jvm_heap()

    print(colored("Elasticsearch installation and configuration completed.", 'yellow'))

if __name__ == "__main__":
    main()
