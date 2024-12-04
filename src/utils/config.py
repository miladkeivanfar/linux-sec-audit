SERVICES_CONFIG = {
    'apache2': {
        'process': 'apache2',
        'config_path': '/etc/apache2/apache2.conf'
    },
    'nginx': {
        'process': 'nginx',
        'config_path': '/etc/nginx/nginx.conf'
    },
    'ssh': {
        'process': 'sshd',
        'config_path': '/etc/ssh/sshd_config'
    },
    'fail2ban': {
        'process': 'fail2ban-server',
        'config_path': '/etc/fail2ban/jail.conf'
    },
    'ufw': {
        'process': 'ufw',
        'config_path': '/etc/default/ufw'
    }
}