#!/bin/bash

#add color for text
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
plain='\033[0m'
NC='\033[0m' # No Color


cur_dir=$(pwd)
# check root
# [[ $EUID -ne 0 ]] && echo -e "${RED}Fatal error: ${plain} Please run this script with root privilege \n " && exit 1

install_jq() {
    if ! command -v jq &> /dev/null; then
        # Check if the system is using apt package manager
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

require_command(){
    
    apt update -y && apt upgrade -y
    apt install python3-pip -y
    install_jq
    if ! command -v pv &> /dev/null
    then
        echo "pv could not be found, installing it..."
        sudo apt update
        sudo apt install -y pv
    fi
}


menu(){
    clear
    # Get server IP
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    # Fetch server country using ip-api.com
    SERVER_COUNTRY=$(curl -sS "http://ip-api.com/json/$SERVER_IP" | jq -r '.country')
    
    # Fetch server isp using ip-api.com
    SERVER_ISP=$(curl -sS "http://ip-api.com/json/$SERVER_IP" | jq -r '.isp')
    
    echo "+------------------------------------------------------------------------------------------------+"
    echo "| ######   ####   #####    ######   ######   ######   #####      ##     ######    ####    ##  ## |"
    echo "| ##        ##    ##  ##   ##         ##     ##       ##  ##    ####    ##         ##     ## ##  |"
    echo "| ##        ##    ##  ##   ##         ##     ##       ##  ##   ##  ##   ##         ##     ####   |"
    echo "| ####      ##    #####    ####       ##     ####     #####    ######   ####       ##     ###    |"
    echo "| ##        ##    ####     ##         ##     ##       ####     ##  ##   ##         ##     ####   |"
    echo "| ##        ##    ## ##    ##         ##     ##       ## ##    ##  ##   ##         ##     ## ##  |"
    echo "| ##       ####   ##  ##   ######     ##     ######   ##  ##   ##  ##   ##        ####    ##  ## |"
    echo -e "| ${RED}Fire Terafik is a modern HTTP reverse proxy and load balancer${NC}                                  |"
    echo "+------------------------------------------------------------------------------------------------+"
    echo -e "|  Telegram Channel : ${GREEN}@DVHOST_CLOUD ${NC}     |     YouTube : ${GREEN}youtube.com/@dvhost_cloud${NC}               |"
    echo "+------------------------------------------------------------------------------------------------+"
    echo -e "|${GREEN}Server Country    |${NC} $SERVER_COUNTRY"
    echo -e "|${GREEN}Server IP         |${NC} $SERVER_IP"
    echo -e "|${GREEN}Server ISP        |${NC} $SERVER_ISP"
    echo "+------------------------------------------------------------------------------------------------+"
    echo -e "|${YELLOW}Please choose an option:${NC}"
    echo "+------------------------------------------------------------------------------------------------+"
    echo -e $1
    echo "+------------------------------------------------------------------------------------------------+"
    echo -e "\033[0m"
}


loader(){
    
    clear
    
    menu "| 1  - Install Tunnel \n| 2  - Uninstall Tunnel \n| 3  - Display Tunnel Status \n| 0  - Exit"
    
    read -p "Enter your choice: " choice
    
    case $choice in
        1)
            python3 install.py install
            read -p "Press any key to continue..."
        ;;
        2)
            python3 install.py uninstall
            read -p "Press any key to continue..."
        ;;
        3)
            python3 install.py status
            read -p "Press any key to continue..."
        ;;
        0)
            echo -e "${GREEN}Exiting program...${NC}"
            exit 0
        ;;
        *)
            echo "Invalid choice. Please try again."
            read -p "Press any key to continue..."
        ;;
    esac
    
}
require_command
loader