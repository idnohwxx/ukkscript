import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def run_command(command):

    try:
        logging.info(f"Executing: {command}")
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        logging.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {e.stderr}")
        raise

def configure_dependencies():
    sources_list = """deb http://deb.debian.org/debian bookworm main contrib non-free
deb http://security.debian.org/debian-security bookworm-security main contrib non-free
deb http://deb.debian.org/debian bookworm-updates main contrib non-free
    """

    with open("/etc/apt/sources.list", "w") as f:
        f.write(sources_list)

    logging.info("Sources list updated.")

def configure_bind9():

    run_command('apt install -y bind9')
    run_command('cp /etc/bind/db.local /etc/bind/forward')
    run_command('cp /etc/bind/db.127 /etc/bind/reverse')

    domain_name = input("Input your domain name : ")
    ip_address = input("Input your IP Addresses : ")
    ip_parts = ip_address.split('.')

    if(len(ip_parts) != 4):
        raise ValueError("Alamat IP tidak valid, harus memiliki 4 bagian.")

    forward_config = f""";
; BIND data file for local loopback interface
;
$TTL	604800
@	IN	SOA	{domain_name}. root.{domain_name}. (
			      2		; Serial
			 604800		; Refresh
			  86400		; Retry
			2419200		; Expire
			 604800 )	; Negative Cache TTL
;
@	IN	NS	{domain_name}.
@	IN	A	{ip_address}
@	IN	AAAA	::1
    """

    with open("/etc/bind/forward", "w") as f:
        f.write(forward_config)
    logging.info(f'Forward file successfully configured. Domain : {domain_name} and IP Address : {ip_address}')

    reverse_config = f""";
; BIND reverse data file for local loopback interface
;
$TTL    604800
@       IN      SOA     {domain_name}. root.{domain_name}. (
                              1         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      {domain_name}.
{ip_address.split('.')[-1]}       IN      PTR     {domain_name}.
"""

    with open("/etc/bind/reverse", "w") as f:
        f.write(reverse_config)
    logging.info(f'Reverse file successfully configured. Domain : {domain_name} and IP Address : {ip_address}')

    rearranged_ip = f"{ip_parts[2]}.{ip_parts[1]}.{ip_parts[0]}"

    zones_config = f"""// prime the server with knowledge of the root servers
zone "." {{
        type hint;
        file "/usr/share/dns/root.hints";
}};

// be authoritative for the localhost forward and reverse zones, and for
// broadcast zones as per RFC 1912

zone "{domain_name}" {{
        type master;
        file "/etc/bind/forward";
}};

zone "{rearranged_ip}.in-addr.arpa" {{
        type master;
        file "/etc/bind/reverse";
}};

zone "0.in-addr.arpa" {{
        type master;
        file "/etc/bind/db.0";
}};

zone "255.in-addr.arpa" {{
        type master;
        file "/etc/bind/db.255";
}};
"""
    with open("/etc/bind/named.conf.default-zones", "w") as f:
        f.write(zones_config)
    logging.info(f'Default-Zones file successfully configured. Domain : {domain_name} and Rearanged IP : {rearranged_ip}')

    resolv = f"search {domain_name}\nnameserver {ip_address}"

    with open("/etc/resolv.conf", "r") as f:
        old_content = f.read()

    update_resolv = resolv + '\n' + old_content
    
    with open('/etc/resolv.conf', 'w') as file:
        file.write(update_resolv)

    logging.info("Resolv conf successfully configured.")

    run_command('systemctl restart bind9')

    logging.info("Bind9 successfully configured.")


def configure_apache2():
    run_command('apt install -y apache2')

    main_conf = """<VirtualHost *:80>
# The ServerName directive sets the request scheme, hostname and port that
# the server uses to identify itself. This is used when creating
# redirection URLs. In the context of virtual hosts, the ServerName
# specifies what hostname must appear in the request's Host: header to
# match this virtual host. For the default virtual host (this file) this
# value is not decisive as it is used as a last resort host regardless.
# However, you must set it for any further virtual host explicitly.
#ServerName www.example.com

ServerAdmin webmaster@localhost
DocumentRoot /var/www/ukkweb

# Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
# error, crit, alert, emerg.
# It is also possible to configure the loglevel for particular
# modules, e.g.
#LogLevel info ssl:warn

ErrorLog ${APACHE_LOG_DIR}/error.log
CustomLog ${APACHE_LOG_DIR}/access.log combined

# For most configuration files from conf-available/, which are
# enabled or disabled at a global level, it is possible to
# include a line for only one particular virtual host. For example the
# following line enables the CGI configuration for this host only
# after it has been globally disabled with "a2disconf".
#Include conf-available/serve-cgi-bin.conf
</VirtualHost>
"""
    with open('/etc/apache2/sites-available/000-default.conf', 'w') as file:
        file.write(main_conf)
    
    logging.info("Sites-available conf successfully configured.")


    run_command('rm -rf /var/www/*')
    run_command('git clone https://github.com/idnohwxx/ukkweb.git /var/www/ukkweb')

    logging.info("Cloning the website done.")

    run_command('systemctl restart apache2')

    logging.info("apache2 successfully configured.")


if __name__ == "__main__":
    configure_dependencies()
    while True:
        run_command('clear')
        print("rivanrl <3\n")
        print("Tips: \nPastikan kalian sudah set IP Address dan systemctl restart networking\n")
        print('1. Install & Configure Bind9\n2. Install & Configure Apache2')
        choice = input('Choose your command : ')
        if choice == '1':
            configure_bind9()
        elif choice == '2':
            configure_apache2()
