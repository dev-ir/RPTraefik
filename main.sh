#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
plain='\033[0m'
NC='\033[0m'

PROJECT_DIR="/opt/RPTraefik"

check_python_dependencies() {
    echo -e "${YELLOW}Checking Python dependencies...${NC}"

    if ! command -v pip3 &> /dev/null; then
        echo -e "${YELLOW}pip not found. Installing pip...${NC}"
        sudo apt update
        sudo apt install -y python3-pip
    fi

    # Install modules using apt to avoid PEP 668 restrictions
    sudo apt install -y python3-tqdm python3-requests python3-yaml

    REQUIRED_MODULES=("tqdm" "requests" "yaml")

    for module in "${REQUIRED_MODULES[@]}"; do
        python3 -c "import $module" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo -e "${RED}Missing Python module: $module. Please install it manually.${NC}"
            exit 1
        fi
    done
}

install_jq() {
    if ! command -v jq &> /dev/null; then
        if command -v apt-get &> /dev/null; then
            echo -e "${RED}jq is not installed. Installing...${NC}"
            sleep 1
            sudo apt-get update
            sudo apt-get install -y jq
        else
            echo -e "${RED}Error: Unsupported package manager. Please install jq manually.${NC}\n"
            read -p "Press any key to continue..."
            exit 1
        fi
    fi
}

loader() {
    install_jq
    SERVER_IP=$(hostname -I | awk '{print $1}')
    SERVER_COUNTRY=$(curl -sS "http://ip-api.com/json/$SERVER_IP" | jq -r '.country')
    SERVER_ISP=$(curl -sS "http://ip-api.com/json/$SERVER_IP" | jq -r '.isp')
}

menu() {
    clear
    echo "+--------------------------------------------------------------------------+"
    echo "|  ██████╗ ██████╗ ████████╗██████╗  █████╗ ███████╗███████╗██╗██╗  ██╗    |"
    echo "|  ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝██║██║ ██╔╝    |"
    echo "|  ██████╔╝██████╔╝   ██║   ██████╔╝███████║█████╗  █████╗  ██║█████╔╝     |"
    echo "|  ██╔══██╗██╔═══╝    ██║   ██╔══██╗██╔══██║██╔══╝  ██╔══╝  ██║██╔═██╗     |"
    echo "|  ██║  ██║██║        ██║   ██║  ██║██║  ██║███████╗██║     ██║██║  ██╗    |"
    echo "|  ╚═╝  ╚═╝╚═╝        ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝    |"
    echo "|                                                               ( V3.3.4 ) |"
    echo "+--------------------------------------------------------------------------+"
    echo -e "| Telegram Channel : ${YELLOW}@DVHOST_CLOUD ${NC} |  YouTube : ${RED}youtube.com/@dvhost_cloud${NC} |"
    echo "+--------------------------------------------------------------------------+"
    echo -e "${GREEN}|Server Location:${NC} $SERVER_COUNTRY"
    echo -e "${GREEN}|Server IP:${NC} $SERVER_IP"
    echo -e "${GREEN}|Server ISP:${NC} $SERVER_ISP"
    echo "+--------------------------------------------------------------------------+"
    echo -e "${YELLOW}|"
    echo -e "|  1  - Install Core and Setup Tunnel"
    echo -e "|  2  - Display Tunnel Status"
    echo -e "|  3  - Uninstall RPTraefik"
    echo -e "|  0  - Exit"
    echo -e "|${NC}"
    echo "+--------------------------------------------------------------------------+"

    read -p "Please choose an option: " choice

    case $choice in
        1)
            if [ ! -d "$PROJECT_DIR/.git" ]; then
                git clone https://github.com/dev-ir/RPTraefik.git "$PROJECT_DIR"
            else
                echo -e "${YELLOW}Project already exists. Pulling latest changes...${NC}"
                cd "$PROJECT_DIR" && git pull
            fi
            check_python_dependencies
            python3 "$PROJECT_DIR/install.py" install
            setup_symlink
            ;;
        2)
            python3 "$PROJECT_DIR/install.py" status
            ;;
        3)
            python3 "$PROJECT_DIR/install.py" uninstall
            ;;
        0)
            echo -e "${GREEN}Exiting program...${NC}"
            exit 0
            ;;
        *)
            echo "Not valid"
            ;;
    esac
}

setup_symlink() {
    local target_link="/usr/local/bin/RPTraefik"
    local source_file="/opt/RPTraefik/main.sh"

    if [ -f "$source_file" ]; then
        chmod +x "$source_file"
        if [ ! -L "$target_link" ]; then
            ln -s "$source_file" "$target_link"
        fi
        chmod +x "$target_link"
        echo -e "${GREEN}✔️ 'RPTraefik' command is now available globally.${NC}"
    fi
}

loader
menu
