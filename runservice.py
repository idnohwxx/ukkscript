import subprocess
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def run_command(command: str):
    """
    Run a system command and log its output.
    """
    try:
        logging.info(f"Executing: {command}")
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        logging.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {e.stderr}")
        raise
def configure_dependencies():
    sources_list = """
    deb http://deb.debian.org/debian bookworm main contrib non-free
    deb http://security.debian.org/debian-security bookworm-security main contrib non-free
    deb http://deb.debian.org/debian bookworm-updates main contrib non-free
    """
    with open("/etc/apt/sources.list", "a") as f:
        f.write(sources_list)
    logging.info("Sources list updated.")

def configure_bind9():
    """
    Configure BIND9 DNS server.
    """
    # Example: Write a DNS zone file
    zone_config = """
    zone "example.com" {
        type master;
        file "/etc/bind/db.example.com";
    };
    """
    with open("/etc/bind/named.conf.local", "a") as f:
        f.write(zone_config)
    logging.info("BIND9 configured successfully.")

    # Example DNS zone file
    dns_zone = """
    $TTL    604800
    @       IN      SOA     ns1.example.com. admin.example.com. (
                          2025011501 ; Serial
                          604800     ; Refresh
                          86400      ; Retry
                          2419200    ; Expire
                          604800 )   ; Negative Cache TTL
    ;
    @       IN      NS      ns1.example.com.
    ns1     IN      A       192.168.1.1
    www     IN      A       192.168.1.2
    """
    with open("/etc/bind/db.example.com", "w") as f:
        f.write(dns_zone)
    logging.info("DNS zone file created.")

    # Restart BIND9
    run_command("sudo systemctl restart bind9")

def configure_apache2():
    """
    Configure Apache2 web server.
    """
    # Example: Create a virtual host file
    virtual_host = """
    <VirtualHost *:80>
        ServerName example.com
        DocumentRoot /var/www/example.com
        <Directory /var/www/example.com>
            AllowOverride All
        </Directory>
    </VirtualHost>
    """
    with open("/etc/apache2/sites-available/example.com.conf", "w") as f:
        f.write(virtual_host)
    logging.info("Apache2 virtual host file created.")

    # Enable the site and restart Apache2
    run_command("sudo a2ensite example.com.conf")
    run_command("sudo systemctl restart apache2")

if __name__ == "__main__":
    configure_dependencies()