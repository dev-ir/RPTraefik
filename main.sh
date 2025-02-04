#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
plain='\033[0m'
NC='\033[0m'

PROJECT_DIR="/opt/DVHOST"

# [[ $EUID -ne 0 ]] && echo -e "${RED}Fatal error: ${plain} Please run this script with root privilege \n " && exit 1

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

loader(){
    install_jq
    SERVER_IP=$(hostname -I | awk '{print $1}')
    SERVER_COUNTRY=$(curl -sS "http://ip-api.com/json/$SERVER_IP" | jq -r '.country')
    SERVER_ISP=$(curl -sS "http://ip-api.com/json/$SERVER_IP" | jq -r '.isp')
}

menu(){
    
    clear
    echo "+--------------------------------------------------------------------------+"
    echo "|  ██████╗ ██████╗ ████████╗██████╗  █████╗ ███████╗███████╗██╗██╗  ██╗    |"
    echo "|  ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝██║██║ ██╔╝    |"
    echo "|  ██████╔╝██████╔╝   ██║   ██████╔╝███████║█████╗  █████╗  ██║█████╔╝     |"
    echo "|  ██╔══██╗██╔═══╝    ██║   ██╔══██╗██╔══██║██╔══╝  ██╔══╝  ██║██╔═██╗     |"
    echo "|  ██║  ██║██║        ██║   ██║  ██║██║  ██║███████╗██║     ██║██║  ██╗    |"
    echo "|  ╚═╝  ╚═╝╚═╝        ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝    |"
    echo "|                                                               ( V3.3.3 ) |" 
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
    echo -e "|  3  - Unistall RPTraefik"
    echo -e "|  0  - Exit"
    echo -e "|${NC}"
    echo "+--------------------------------------------------------------------------+"
    
    read -p "Please choose an option: " choice
    
    case $choice in
        1)  git clone https://github.com/dev-ir/RPTraefik.git
            python3 install.py install ;;
        2)  python3 install.py status ;;
        3)  python3 install.py uninstall ;;
        0)
            echo -e "${GREEN}Exiting program...${NC}"
            exit 0
            ;;
        *)
                echo "Not valid"
            ;;
    esac
    
}

loader
menu