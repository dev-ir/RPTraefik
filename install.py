import os, sys, subprocess, signal, socket, termcolor, requests
from tqdm import tqdm

CONFIG_DIR = "/etc/traefik/"
CONFIG_FILE = os.path.join(CONFIG_DIR, "traefik.yml")
DYNAMIC_FILE = os.path.join(CONFIG_DIR, "dynamic.yml")

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
    modules = ["tqdm", "termcolor", "requests"]
    for module in modules:
        try:
            __import__(module)
        except ImportError:
            install_module(module)

check_and_install_modules()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def signal_handler(sig, frame):
    print(termcolor.colored("\nOperation cancelled by the user.", "red"))
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def check_requirements():
    try:
        subprocess.run(["which", "traefik"], check=True)
    except subprocess.CalledProcessError:
        print(termcolor.colored("Traefik is not installed. Installing Traefik...", "yellow"))
        run_command(["curl", "-L", "https://github.com/traefik/traefik/releases/download/v3.1.0/traefik_v3.1.0_linux_amd64.tar.gz", "-o", "traefik.tar.gz"])
        run_command(["tar", "-xvzf", "traefik.tar.gz"])
        run_command(["sudo", "mv", "traefik", "/usr/local/bin/"])
        os.remove("traefik.tar.gz")

def check_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('localhost', port))
        return result != 0

def create_config_files(ip_iran, ip_abroad, ports_list):
    traefik_config = "entryPoints:\n"
    for port in ports_list:
        traefik_config += f"  port_{port}:\n    address: ':{port}'\n"
    traefik_config += f"providers:\n  file:\n    filename: '{DYNAMIC_FILE}'\napi:\n  dashboard: true\n  insecure: true\n"

    dynamic_config = "tcp:\n  routers:\n"
    for port in ports_list:
        dynamic_config += f"    tcp_router_{port}:\n      entryPoints:\n        - port_{port}\n      service: tcp_service_{port}\n      rule: 'HostSNI(`*`)'\n"
    dynamic_config += "  services:\n"
    for port in ports_list:
        dynamic_config += f"    tcp_service_{port}:\n      loadBalancer:\n        servers:\n          - address: '{ip_iran}:{port}'\n          - address: '{ip_abroad}:{port}'\n"

    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as traefik_file:
        traefik_file.write(traefik_config)
    with open(DYNAMIC_FILE, "w") as dynamic_file:
        dynamic_file.write(dynamic_config)

def install_tunnel():
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

    ip_iran = input(f"Enter IPv{version} address of the Iran server: ")
    ip_abroad = input(f"Enter IPv{version} address of the Abroad server: ")
    ports = input("Enter the ports to tunnel (comma-separated): ")
    ports_list = ports.split(',')

    for port in ports_list:
        if not check_port_available(int(port)):
            print(termcolor.colored(f"Port {port} is already in use. Please choose another port.", "red"))
            return

    create_config_files(ip_iran, ip_abroad, ports_list)

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
    service_file_path = "/etc/systemd/system/traefik-tunnel.service"
    with open(service_file_path, "w") as service_file:
        service_file.write(service_file_content)

    run_command(["sudo", "systemctl", "daemon-reload"])
    run_command(["sudo", "systemctl", "enable", "traefik-tunnel.service"])
    run_command(["sudo", "systemctl", "start", "traefik-tunnel.service"])

    print(termcolor.colored("Tunnel is being established and the service is running in the background...", "green"))
    input(termcolor.colored("Press any key to continue...", "cyan"))

def uninstall_tunnel():
    try:
        run_command(["sudo", "systemctl", "stop", "traefik-tunnel.service"])
        run_command(["sudo", "systemctl", "disable", "traefik-tunnel.service"])
        os.remove("/etc/systemd/system/traefik-tunnel.service")
        os.remove(CONFIG_FILE)
        os.remove(DYNAMIC_FILE)
        run_command(["sudo", "systemctl", "daemon-reload"])
        print(termcolor.colored("Tunnel has been successfully removed.", "green"))
    except Exception as e:
        print(termcolor.colored(f"An error occurred while removing the tunnel: {e}", "red"))
    input(termcolor.colored("Press any key to continue...", "cyan"))

def display_banner():
    banner = """
+-------------------------------------------------------------------------------------------------------------------------------------+    
|#### ##  ### ##     ##     ### ###  ### ###    ####   ##  ###      #### ##  ##  ###  ###  ##  ###  ##  ### ###  ####                 |
|# ## ##   ##  ##     ##     ##  ##   ##  ##     ##    ##  ##       # ## ##  ##   ##    ## ##    ## ##   ##  ##   ##                  |  
|  ##      ##  ##   ## ##    ##       ##         ##    ## ##          ##     ##   ##   # ## #   # ## #   ##       ##                  |  
|  ##      ## ##    ##  ##   ## ##    ## ##      ##    ## ##          ##     ##   ##   ## ##    ## ##    ## ##    ##    TG CHANNEL    |
|  ##      ## ##    ## ###   ##       ##         ##    ## ###         ##     ##   ##   ##  ##   ##  ##   ##       ##    @DVHOST_CLOUD |
|  ##      ##  ##   ##  ##   ##  ##   ##         ##    ##  ##         ##     ##   ##   ##  ##   ##  ##   ##  ##   ##  ##              |  
| ####    #### ##  ###  ##  ### ###  ####       ####   ##  ###       ####     ## ##   ###  ##  ###  ##  ### ###  ### ###              |   
+-------------------------------------------------------------------------------------------------------------------------------------+   
"""
    print(termcolor.colored(banner, "cyan"))

def check_tunnel_status():
    try:
        response = requests.get("http://localhost:8080/api/rawdata")
        if response.status_code == 200:
            return response.json()
        else:
            print(termcolor.colored("Failed to retrieve Traefik status. Please check if Traefik is running.", "red"))
            return None
    except requests.exceptions.RequestException as e:
        print(termcolor.colored(f"Error connecting to Traefik API: {e}", "red"))
        return None

def display_tunnel_status():
    status = check_tunnel_status()
    if status:
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
        print(termcolor.colored("Tunnel is not running. Please check the Traefik configuration.", "red"))

def main():
    check_requirements()
    
    while True:
        clear_screen()
        display_banner()
        print("\nSelect an option:")
        print("1 - Install Tunnel")
        print("2 - Uninstall Tunnel")
        print("3 - Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            install_tunnel()
        elif choice == "2":
            uninstall_tunnel()
        elif choice == "3":
            break
        else:
            print(termcolor.colored("Invalid choice. Please try again.", "red"))

if __name__ == "__main__":
    main()
