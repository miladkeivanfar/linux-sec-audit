import subprocess
import shutil
from colorama import Fore, Style
from src.utils.config import SERVICES_CONFIG

class ServiceScanner:
    def __init__(self):
        self.services = SERVICES_CONFIG
        self.found_services = {}

    def is_service_installed(self, service_name):
        return shutil.which(service_name) is not None

    def is_service_running(self, process_name):
        try:
            subprocess.run(['pgrep', process_name], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def scan_services(self):
        print(f"\n{Fore.CYAN}=== Scanning for Services ==={Style.RESET_ALL}")
        
        for service, details in self.services.items():
            if self.is_service_installed(service) or self.is_service_running(details['process']):
                self.found_services[service] = details
                if service == "ufw":
                  status = "ufw in installed"
                else:
                  status = "Running" if self.is_service_running(details['process']) else "Installed but not running"
                print(f"{Fore.GREEN}✓ {service}: {status}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✗ {service}: Not found{Style.RESET_ALL}")

        return self.found_services
