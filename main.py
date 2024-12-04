#!/usr/bin/env python3
from src.scanner.service_scanner import ServiceScanner
from src.security.checker import SecurityChecker
from src.security.hardening import SecurityHardening
from colorama import init, Fore, Style

def main():
    init()  # Initialize colorama
    
    print(f"{Fore.CYAN}=== Linux Security Audit and Hardening Tool ==={Style.RESET_ALL}")
    
    # Step 1: Scan for services
    scanner = ServiceScanner()
    found_services = scanner.scan_services()
    
    if not found_services:
        print(f"{Fore.RED}No supported services found.{Style.RESET_ALL}")
        return
    
    # Step 2: Check security configuration
    checker = SecurityChecker(found_services)
    issues = checker.check_all_services()
    checker.display_issues()
    
    # Step 3: Hardening options
    hardening = SecurityHardening(issues)
    
    while True:
        print(f"\n{Fore.CYAN}Select hardening option:{Style.RESET_ALL}")
        print("1) Apply hardening to all services")
        print("2) Select specific services")
        print("3) Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            hardening.apply_hardening()
            break
        elif choice == "2":
            choices = hardening.get_service_choices()
            selected = input("\nEnter service numbers (comma-separated): ")
            selected_services = [choices[num.strip()] for num in selected.split(",") if num.strip() in choices]
            if selected_services:
                hardening.apply_hardening(selected_services)
            break
        elif choice == "3":
            print(f"{Fore.YELLOW}Exiting without applying changes.{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()