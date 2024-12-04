import subprocess
import re
from colorama import Fore, Style

class UFWHardener:
    def __init__(self):
        self.ssh_config_path = '/etc/ssh/sshd_config'

    def get_ufw_status(self):
        try:
            result = subprocess.run(['ufw', 'status'], 
                                  capture_output=True, 
                                  text=True)
            return result.stdout
        except subprocess.CalledProcessError:
            return None

    def is_ufw_active(self):
        status = self.get_ufw_status()
        return status is not None and 'Status: active' in status

    def get_ssh_port(self):
        try:
            with open(self.ssh_config_path, 'r') as f:
                content = f.read()
                port_match = re.search(r'^Port\s+(\d+)', content, re.MULTILINE)
                return port_match.group(1) if port_match else '22'
        except Exception:
            return '22'

    def apply_security_settings(self):
        try:
            ssh_port = self.get_ssh_port()
            print(f"{Fore.CYAN}Detected SSH port: {ssh_port}{Style.RESET_ALL}")

            subprocess.run(['ufw', '--force', 'reset'], check=True)
            subprocess.run(['ufw', 'default', 'deny', 'incoming'], check=True)
            subprocess.run(['ufw', 'default', 'allow', 'outgoing'], check=True)
            subprocess.run(['ufw', 'allow', f'{ssh_port}/tcp'], check=True)
            
            if not self.is_ufw_active():
                print(f"{Fore.YELLOW}Enabling UFW...{Style.RESET_ALL}")
                subprocess.run(['ufw', '--force', 'enable'], check=True)
            
            print(f"{Fore.GREEN}UFW configuration applied successfully{Style.RESET_ALL}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Error applying UFW settings: {str(e)}{Style.RESET_ALL}")
            return False