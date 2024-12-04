import subprocess
import os
from colorama import Fore, Style

class ApacheHardener:
    def __init__(self):
        self.config_path = '/etc/apache2/apache2.conf'
        self.ssl_config_path = '/etc/apache2/mods-available/ssl.conf'
        
    def check_module_enabled(self, module_name):
        try:
            result = subprocess.run(['a2query', '-m', module_name], 
                                  capture_output=True, 
                                  text=True)
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False

    def enable_module(self, module_name):
        try:
            subprocess.run(['a2enmod', module_name], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def validate_config(self):
        try:
            subprocess.run(['apache2ctl', 'configtest'], 
                         check=True, 
                         capture_output=True,
                         text=True)
            return True, ""
        except subprocess.CalledProcessError as e:
            return False, e.stdout + e.stderr

    def backup_config(self, file_path):
        backup_path = f"{file_path}.backup"
        try:
            subprocess.run(['cp', file_path, backup_path], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def fix_options_directives(self, config_lines):
        new_lines = []
        has_changes = False
        in_directory_block = False
        directory_indent = ""

        secure_options = "Options -Indexes -Includes -ExecCGI -MultiViews -FollowSymLinks"

        for line in config_lines:
            stripped_line = line.strip()
            
            if "<Directory" in stripped_line:
                in_directory_block = True
                directory_indent = line[:line.find("<Directory")]
            elif "</Directory>" in stripped_line:
                in_directory_block = False

            if stripped_line.startswith('Options'):
                has_changes = True
                if in_directory_block:
                    new_lines.append(f"{directory_indent}    {secure_options}\n")
                else:
                    new_lines.append(f"    {secure_options}\n")
            else:
                new_lines.append(line)

        return new_lines, has_changes

    def apply_security_settings(self):
        if not self.check_module_enabled('ssl'):
            print(f"{Fore.YELLOW}Enabling SSL module...{Style.RESET_ALL}")
            if not self.enable_module('ssl'):
                print(f"{Fore.RED}Failed to enable SSL module{Style.RESET_ALL}")
                return False

        if not self.backup_config(self.config_path):
            print(f"{Fore.RED}Failed to create backup of Apache configuration{Style.RESET_ALL}")
            return False

        try:
            with open(self.config_path, 'r') as f:
                config_lines = f.readlines()

            new_config_lines, changes_made = self.fix_options_directives(config_lines)

            if not changes_made:
                print(f"{Fore.YELLOW}No Options directives found, adding secure defaults...{Style.RESET_ALL}")
                new_config_lines.append("\n# Secure Options settings\nOptions -Indexes -Includes -ExecCGI -MultiViews -FollowSymLinks\n")

            with open(self.config_path, 'w') as f:
                f.writelines(new_config_lines)

            is_valid, error_msg = self.validate_config()
            if not is_valid:
                print(f"{Fore.RED}Configuration validation failed:{Style.RESET_ALL}")
                print(error_msg)
                subprocess.run(['cp', f"{self.config_path}.backup", self.config_path], check=True)
                return False

            try:
                subprocess.run(['systemctl', 'restart', 'apache2'], check=True)
                print(f"{Fore.GREEN}Apache configuration updated and service restarted successfully{Style.RESET_ALL}")
                return True
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}Failed to restart Apache. Please check the service status.{Style.RESET_ALL}")
                return False

        except Exception as e:
            print(f"{Fore.RED}Error applying Apache security settings: {str(e)}{Style.RESET_ALL}")
            if os.path.exists(f"{self.config_path}.backup"):
                subprocess.run(['cp', f"{self.config_path}.backup", self.config_path], check=True)
            return False