import os
import subprocess
from colorama import Fore, Style
from src.utils.config import SERVICES_CONFIG

class SecurityChecker:
    def __init__(self, found_services):
        self.found_services = found_services
        self.issues = {}

    def check_apache(self):
        issues = []
        config_path = self.found_services['apache2']['config_path']
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config_content = f.read()
                
                # Check for directory listing
                if 'Options Indexes' in config_content or 'Options +Indexes' in config_content:
                    issues.append({
                        'severity': 'HIGH',
                        'description': 'Directory listing is enabled',
                        'recommendation': 'Disable directory listing using "Options -Indexes"'
                    })

                # Check for SSL configuration
                try:
                    ssl_check = subprocess.run(['a2query', '-m', 'ssl'], 
                                            capture_output=True, 
                                            text=True)
                    if ssl_check.returncode != 0:
                        issues.append({
                            'severity': 'HIGH',
                            'description': 'SSL module is not enabled',
                            'recommendation': 'Enable SSL module using "a2enmod ssl"'
                        })
                except subprocess.CalledProcessError:
                    pass

                # Check for mixed Options directives
                options_lines = [line for line in config_content.splitlines() 
                               if line.strip().startswith('Options')]
                if any('+' in line and '-' in line for line in options_lines):
                    issues.append({
                        'severity': 'HIGH',
                        'description': 'Mixed Options directives (both + and -) found',
                        'recommendation': 'Use consistent Options directives (either all + or all -)'
                    })

            except Exception as e:
                print(f"{Fore.RED}Error checking Apache configuration: {str(e)}{Style.RESET_ALL}")
                
        return issues

    def check_ufw(self):
        issues = []
        try:
            ufw_status = subprocess.run(['ufw', 'status'], 
                                      capture_output=True, 
                                      text=True)
            
            if 'Status: inactive' in ufw_status.stdout:
                issues.append({
                    'severity': 'HIGH',
                    'description': 'UFW firewall is installed but not active',
                    'recommendation': 'Enable UFW firewall with appropriate rules'
                })
            elif ufw_status.returncode != 0:
                issues.append({
                    'severity': 'HIGH',
                    'description': 'UFW firewall is not properly configured',
                    'recommendation': 'Install and configure UFW firewall'
                })
        except subprocess.CalledProcessError:
            issues.append({
                'severity': 'HIGH',
                'description': 'UFW firewall is not installed or not accessible',
                'recommendation': 'Install and configure UFW firewall'
            })
        return issues

    def check_ssh(self):
        issues = []
        config_path = self.found_services['ssh']['config_path']
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config_content = f.read()
                    
                if 'PermitRootLogin yes' in config_content:
                    issues.append({
                        'severity': 'HIGH',
                        'description': 'Root login is enabled',
                        'recommendation': 'Set PermitRootLogin to no'
                    })
            except Exception:
                pass
        return issues

    def check_nginx(self):
        issues = []
        config_path = self.found_services['nginx']['config_path']
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config_content = f.read()
                    
                if 'server_tokens on' in config_content or not 'server_tokens off' in config_content:
                    issues.append({
                        'severity': 'MEDIUM',
                        'description': 'Server tokens are enabled',
                        'recommendation': 'Set server_tokens off'
                    })
            except Exception:
                pass
        return issues

    def check_all_services(self):
        print(f"\n{Fore.CYAN}=== Checking Security Configuration ==={Style.RESET_ALL}")
        
        for service in self.found_services:
            if service == 'apache2':
                self.issues[service] = self.check_apache()
            elif service == 'nginx':
                self.issues[service] = self.check_nginx()
            elif service == 'ssh':
                self.issues[service] = self.check_ssh()
            elif service == 'ufw':
                self.issues[service] = self.check_ufw()

        return self.issues

    def display_issues(self):
        for service, service_issues in self.issues.items():
            if service_issues:
                print(f"\n{Fore.YELLOW}Issues found in {service}:{Style.RESET_ALL}")
                for issue in service_issues:
                    severity_color = Fore.RED if issue['severity'] == 'HIGH' else Fore.YELLOW
                    print(f"{severity_color}[{issue['severity']}]{Style.RESET_ALL} {issue['description']}")
                    print(f"{Fore.GREEN}Recommendation:{Style.RESET_ALL} {issue['recommendation']}")