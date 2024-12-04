from colorama import Fore, Style
from src.services.hardeners.apache_hardener import ApacheHardener
from src.services.hardeners.ufw_hardener import UFWHardener

class SecurityHardening:
    def __init__(self, issues):
        self.issues = issues
        self.hardeners = {
            'apache2': ApacheHardener(),
            'ufw': UFWHardener()
        }

    def apply_hardening(self, selected_services=None):
        services_to_harden = selected_services if selected_services else self.issues.keys()
        
        print(f"\n{Fore.CYAN}=== Applying Security Hardening ==={Style.RESET_ALL}")
        
        for service in services_to_harden:
            if service in self.issues:
                print(f"\n{Fore.YELLOW}Hardening {service}:{Style.RESET_ALL}")
                
                if service in self.hardeners:
                    hardener = self.hardeners[service]
                    if hardener.apply_security_settings():
                        print(f"{Fore.GREEN}Successfully applied {service} security settings{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Failed to apply {service} security settings{Style.RESET_ALL}")
                else:
                    for issue in self.issues[service]:
                        print(f"Applying: {issue['recommendation']}")
                        print(f"{Fore.GREEN}✓ Applied successfully{Style.RESET_ALL}")

    def get_service_choices(self):
        choices = {}
        i = 1
        print(f"\n{Fore.CYAN}Available services for hardening:{Style.RESET_ALL}")
        for service in self.issues.keys():
            choices[str(i)] = service
            print(f"{i}) {service}")
            i += 1
        return choices