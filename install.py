import os, sys, subprocess, signal, socket

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    process.communicate()
    return process.returncode

def install_pip():
    run_command(["sudo", "apt", "update"])
    run_command(["sudo", "apt", "install", "-y", "python3-pip"])

def install_module(module_name):
    run_command([sys.executable, "-m", "pip", "install", module_name])

def check_and_install_modules():
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
    except subprocess.CalledProcessError:
        install_pip()
    
    modules = ["tqdm", "termcolor", "requests"]
    for module in modules:
        try:
            __import__(module)
        except ImportError:
            install_module(module)

# Check and install necessary modules
check_and_install_modules()

# Import modules after ensuring they are installed
import termcolor
import requests
from tqdm import tqdm

CONFIG_DIR = "/etc/traefik/"
CONFIG_FILE = os.path.join(CONFIG_DIR, "traefik.yml")
DYNAMIC_FILE = os.path.join(CONFIG_DIR, "dynamic.yml")
SERVICE_FILE = "/etc/systemd/system/traefik-tunnel.service"

def signal_handler(sig, frame):
    print(termcolor.colored("\nOperation cancelled by the user.", "red"))
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def check_requirements():
    try:
        subprocess.run(["which", "traefik"], check=True)
    except subprocess.CalledProcessError:
        print(termcolor.colored("Traefik is not installed. Installing Traefik...", "yellow"))
        run_command(["curl", "-L", "https://github.com/traefik/traefik/releases/download/v3.3.3/traefik_v3.3.3_linux_amd64.tar.gz", "-o", "traefik.tar.gz"])
        run_command(["tar", "-xvzf", "traefik.tar.gz"])
        run_command(["sudo", "mv", "traefik", "/usr/local/bin/"])
        os.remove("traefik.tar.gz")

def check_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('localhost', port))
        return result != 0

def create_config_files(ip_backend, ports_list):
    traefik_config = "entryPoints:\n"
    for port in ports_list:
        traefik_config += f"  port_{port}:\n    address: ':{port}'\n"
    traefik_config += f"providers:\n  file:\n    filename: '{DYNAMIC_FILE}'\napi:\n  dashboard: true\n  insecure: true\n"

    dynamic_config = "tcp:\n  routers:\n"
    for port in ports_list:
        dynamic_config += f"    tcp_router_{port}:\n      entryPoints:\n        - port_{port}\n      service: tcp_service_{port}\n      rule: 'HostSNI(`*`)'\n"
    dynamic_config += "  services:\n"
    for port in ports_list:
        dynamic_config += f"    tcp_service_{port}:\n      loadBalancer:\n        servers:\n          - address: '{ip_backend}:{port}'\n"

    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as traefik_file:
        traefik_file.write(traefik_config)
    with open(DYNAMIC_FILE, "w") as dynamic_file:
        dynamic_file.write(dynamic_config)

def install_tunnel():
    check_requirements()
    
    while True:
        print("Select IP version:")
        print("1 - IPv6")
        print("2 - IPv4")
        version_choice = input("Enter your choice: ")
        
        if version_choice == "1":
            version = '6'
            break
        elif version_choice == "2":
            version = '4'
            break
        else:
            print(termcolor.colored("Invalid choice. Please enter '1' or '2'.", "red"))

    ip_backend = input(f"Enter IPv{version} address of the backend server: ")
    ports = input("Enter the ports to tunnel (comma-separated): ")
    ports_list = ports.split(',')

    for port in ports_list:
        if not check_port_available(int(port)):
            print(termcolor.colored(f"Port {port} is already in use. Please choose another port.", "red"))
            return

    create_config_files(ip_backend, ports_list)

    service_file_content = f"""
[Unit]
Description=Traefik Tunnel Service
After=network.target

[Service]
ExecStart=/usr/local/bin/traefik --configFile={CONFIG_FILE}
Restart=always
User=root
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    with open(SERVICE_FILE, "w") as service_file:
        service_file.write(service_file_content)

    run_command(["sudo", "systemctl", "daemon-reload"])
    run_command(["sudo", "systemctl", "enable", "traefik-tunnel.service"])
    run_command(["sudo", "systemctl", "start", "traefik-tunnel.service"])

    print(termcolor.colored("Tunnel is being established and the service is running in the background...", "green"))

def uninstall_tunnel():
    try:
        run_command(["sudo", "systemctl", "stop", "traefik-tunnel.service"])
        run_command(["sudo", "systemctl", "disable", "traefik-tunnel.service"])
        if os.path.exists(SERVICE_FILE):
            os.remove(SERVICE_FILE)
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        if os.path.exists(DYNAMIC_FILE):
            os.remove(DYNAMIC_FILE)
        run_command(["sudo", "systemctl", "daemon-reload"])
        print(termcolor.colored("Tunnel has been successfully removed.", "green"))
    except Exception as e:
        print(termcolor.colored(f"An error occurred while removing the tunnel: {e}", "red"))

def display_tunnel_status():
    try:
        response = requests.get("http://localhost:8080/api/rawdata")
        if response.status_code == 200:
            status = response.json()
            routers = status.get('tcp', {}).get('routers', {})
            services = status.get('tcp', {}).get('services', {})
            
            print(termcolor.colored("Routers:", "yellow"))
            for router, details in routers.items():
                print(f"  - {router}: {details}")

            print(termcolor.colored("Services:", "yellow"))
            for service, details in services.items():
                print(f"  - {service}: {details}")
            print(termcolor.colored("Tunnel is up and running.", "green"))
        else:
            print(termcolor.colored("Failed to retrieve Traefik status. Please check if Traefik is running.", "red"))
    except requests.exceptions.RequestException as e:
        print(termcolor.colored(f"Error connecting to Traefik API: {e}", "red"))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "install":
            install_tunnel()
        elif sys.argv[1] == "uninstall":
            uninstall_tunnel()
        elif sys.argv[1] == "status":
            display_tunnel_status()
        else:
            print("Invalid argument. Use 'install', 'uninstall', or 'status'.")
