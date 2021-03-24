#!/bin/bash


#Debug enable next 3 lines
exec 5> install.txt
BASH_XTRACEFD="5"
set -x
# ------ end debug


function killpython()
{

sudo killall python3

}


function system_update_light()
{

# ---- system_update

sudo apt-get -y update

}

function system_update()
{

# ---- remove unnecessary packages

sudo apt-get remove --purge libreoffice-*
sudo apt-get remove --purge wolfram-engine


# ---- system_update

sudo apt-get -y update
sudo apt-get -y upgrade

}

function system_update_UI()
{

while true; do
    read -p "Do you wish to update the Raspbian system (y/n)?" yn
    case $yn in
        [Yy]* ) system_update; break;;
        [Nn]* ) break;;
        * ) echo "Please answer y or n.";;
    esac
done

}

function install_dependencies()
{


#--- start installing dependencies

sudo apt-get -y install python3-dev || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}
sudo apt -y install python3-pip || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}
sudo pip3 install flask || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}
#sudo pip3 install pyserial || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}
sudo apt-get install python3-future
sudo pip install future

#(for external IP address, using DNS)
sudo apt-get -y install dnsutils || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}

#(web server)
#sudo pip3 install tornado || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}

#(GPIO)
sudo pip3 install RPi.GPIO
}

function enable_I2C()
{

# --- Enable I2C and Spi :
# /boot/config.txt

sed -i 's/\(^.*#dtparam=i2c_arm=on.*$\)/dtparam=i2c_arm=on/' /boot/config.txt
sed -i 's/\(^.*#dtparam=spi=on.*$\)/dtparam=spi=on/' /boot/config.txt
sed -i 's/\(^.*#dtparam=i2s=on.*$\)/dtparam=i2s=on/' /boot/config.txt

# --- install I2C tools
#sudo apt-get install python-smbus
#sudo apt-get install python3-smbus

sudo apt-get -y install git build-essential python3-dev python3-smbus || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}
sudo apt-get -y install -y i2c-tools  || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}

}


### -- WIFI setup --- STANDARD

function valid_ip()
{
    local  ip=$1
    local  stat=1

    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
            && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi
    return $stat
}


input_UI ()
{

echo "Hello, following initial setting is requested:"

# IP part input

IP="0"
while ! valid_ip $IP; do
	read -p "Local IP address (range 192.168.0.100-192.168.1.200), to confirm press [ENTER] or modify: " -e -i 192.168.1.124 IP
	if valid_ip $IP; then stat='good'; 
	else stat='bad'; echo "WRONG FORMAT, please enter a valid value for IP address"
	fi

done
	echo "Confirmed IP address: "$IP

PORT=""
while [[ ! $PORT =~ ^[0-9]+$ ]]; do
read -p "Local PORT, to confirm press [ENTER] or modify: " -e -i 124 PORT
	if [[ ! $PORT =~ ^[0-9]+$ ]];
	then echo "WRONG FORMAT, please enter a valid value for PORT";
	fi
done
	echo "Confirmed PORT: "$PORT
	
# Local WiFi AP name and password setting	

read -p "System WiFi AP name, to confirm press [ENTER] or modify: " -e -i Raspbeery WiFiAPname
echo "Confirmed Name: "$WiFiAPname

read -p "System WiFi AP password, to confirm press [ENTER] or modify: " -e -i birraiscoming WiFiAPpsw
echo "Confirmed Password: "$WiFiAPpsw

read -p "Do you want to change hostname? (y,n): " -e -i y ChangeHostName
echo "Confirmed Answer: "$ChangeHostName

if [ "$ChangeHostName" == "y" ]; then
	read -p "System Hostname, to confirm press [ENTER] or modify: " -e -i Raspbeery-124 NewHostName
	echo "Confirmed Hostname: "$NewHostName
fi


}


apply_newhostname ()
{

# --- change system hostname
if [ "$ChangeHostName" == "y" ]; then
	sudo hostnamectl set-hostname $NewHostName # change the name in /etc/hostname

	aconf="/etc/hosts"
	# Update hostapd main config file
	sudo sed -i "s/127.0.1.1.*/127.0.1.1	"$NewHostName"/" $aconf
	
fi

}


ask_reboot ()
{


read -p "Do you want to reboot the system? (y,n): " -e -i y doreboot
echo "Confirmed Answer: "$doreboot

if [ "$doreboot" == "y" ]; then
	sudo reboot
fi

}




install_Raspbeery ()
{
# --- INSTALL Raspbeery software
sudo apt-get -y install git || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}


# check if file exist in local folder
aconf="/home/pi/env/Raspbeery2"
if [ -d $aconf ]; then  # if the directory exist
	cd /home/pi
else
	cd /home/pi
	sudo rm -r env
	mkdir env
	cd env
	sudo rm -r raspbeery
    git clone https://github.com/Didacus85/Raspbeery2.git
	sudo killall python3
	mv Master Raspbeery2
    sudo chmod -R 777 /home/pi/env/
	cd ..

fi

}



fn_hostapd ()
{

sudo apt-get -y install hostapd || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}

# unmask the service
sudo systemctl unmask hostapd.service
	
# create hostapd.conf file
aconf="/etc/hostapd/hostapd.conf"
if [ -f $aconf ]; then
   cp $aconf $aconf.1
   sudo rm $aconf
   echo "remove file"
fi


sudo bash -c "cat >> $aconf" << EOF
# HERE-> {"name": "IPsetting", "LocalIPaddress": "$IP", "LocalPORT": "$PORT", "LocalAPSSID" : "$WiFiAPname"}
ieee80211n=1
interface=wlan0
ssid=$WiFiAPname
hw_mode=g
channel=6
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=$WiFiAPpsw
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF


aconf="/etc/init.d/hostapd"
# Update hostapd main config file
sudo sed -i "s/\(^.*DAEMON_CONF=.*$\)/DAEMON_CONF=\/etc\/hostapd\/hostapd.conf/" $aconf

aconf="/etc/default/hostapd"
# Update hostapd main config file
sudo sed -i "s/\(^.*DAEMON_CONF=.*$\)/DAEMON_CONF=\/etc\/hostapd\/hostapd.conf/" $aconf

sudo systemctl enable hostapd.service 

}


fn_dnsmasq ()
{
	
sudo apt-get -y install dnsmasq || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}

	
# edit /etc/dnsmasq.conf file
aconf="/etc/dnsmasq.conf"

# delete rows between #START and #END
sed -i '/^#START RASPBEERY SECTION/,/^#END RASPBEERY SECTION/{/^#START RASPBEERY SECTION/!{/^#END RASPBEERY SECTION/!d}}' $aconf
sed -i '/#START RASPBEERY SECTION/d' $aconf
sed -i '/#END RASPBEERY SECTION/d' $aconf

# calculation of the range starting from assigned IP address
IFS="." read -a a <<< $IP
IFS="." read -a b <<< 0.0.0.1
IFS="." read -a c <<< 0.0.0.9
IPSTART="$[a[0]].$[a[1]].$[a[2]].$[a[3]+b[3]]"
IPEND="$[a[0]].$[a[1]].$[a[2]].$[a[3]+c[3]]"
if [[ a[3] -gt 244 ]]; then
IPSTART="$[a[0]].$[a[1]].$[a[2]].$[a[3]-c[3]]"
IPEND="$[a[0]].$[a[1]].$[a[2]].$[a[3]-b[3]]"
fi

echo $IPSTART $IPEND



# -----



sudo bash -c "cat >> $aconf" << EOF
#START RASPBEERY SECTION
interface=wlan0
dhcp-range=$IPSTART,$IPEND,12h
#no-resolv
#END RASPBEERY SECTION
EOF

sudo systemctl enable dnsmasq.service
 

}


fn_dhcpcd ()
{
	
# edit /etc/dnsmasq.conf file
aconf="/etc/dhcpcd.conf"

# delete rows between #START and #END
sed -i '/^#START RASPBEERY SECTION/,/^#END RASPBEERY SECTION/{/^#START RASPBEERY SECTION/!{/^#END RASPBEERY SECTION/!d}}' $aconf
sed -i '/#START RASPBEERY SECTION/d' $aconf
sed -i '/#END RASPBEERY SECTION/d' $aconf


sudo bash -c "cat >> $aconf" << EOF
#START RASPBEERY SECTION
profile static_wlan0
static ip_address=$IP/24
#static routers=192.168.1.1
#static domain_name_servers=192.169.1.1
# fallback to static profile on wlan0
interface wlan0
fallback static_wlan0
#END RASPBEERY SECTION
EOF
 

}

fn_ifnames ()
{
# this is to preserve the network interfaces names, becasue staring from debian stretch (9) the ifnames have new rules 	
# edit /etc/dnsmasq.conf file
aconf="/boot/cmdline.txt"

APPEND=' net.ifnames=0'
echo "$(cat $aconf)$APPEND" > $aconf
 
}




install_nginx ()
{
# this function is used
cd /home/pi

sudo apt-get -y install nginx

# create default file
aconf="/etc/nginx/sites-enabled/default"
if [ -f $aconf ]; then
   cp $aconf /home/pi/$aconf.1
   sudo rm $aconf
   echo "remove file"
fi


sudo bash -c "cat >> $aconf" << EOF
server {
    # for a public HTTP server:
    listen $PORT;
    server_name localhost;

    access_log off;
    error_log off;
    
    root /home/pi/env/Raspbeery2/templates;

    location / {
        proxy_pass http://127.0.0.1:5000;
    }

}
EOF

sudo service nginx start

cd ..
cd ..

}


edit_defaultnetworkdb ()
{


aconf="/home/pi/env/raspbeery/database/default/defnetwork.txt "

# if file already exist then no action, otherwise create it
if [ -f $aconf ]; then
   echo "network default file already exist"
   else
   sudo bash -c "cat >> $aconf" << EOF
{"name": "IPsetting", "LocalIPaddress": "192.168.0.124", "LocalPORT": "5000" , "LocalAPSSID" : "Raspbeery"}
EOF
   
fi

}

edit_networkdb ()
{


aconf="/home/pi/env/raspbeery/database/network.txt "

# if file already exist then delete it
if [ -f $aconf ]; then
   sudo rm $aconf
   echo "remove file"
fi

sudo bash -c "cat >> $aconf" << EOF
{"name": "IPsetting", "LocalIPaddress": "$IP", "LocalPORT": "$PORT", "LocalAPSSID" : "$WiFiAPname"}
EOF


}


iptables_blockports ()
{
sudo iptables -A INPUT -p tcp -s localhost --dport 5020 -j ACCEPT
sudo iptables -A INPUT -p tcp -s localhost --dport 5022 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 5020 -j DROP
sudo iptables -A INPUT -p tcp --dport 5022 -j DROP

sudo iptables-save > /home/pi/iptables.rules

}

copy_services()
{
sudo cp /home/pi/env/Raspbeery2/app.service /lib/systemd/system

sudo chmod 644 /lib/systemd/system/app.service
sudo chmod +x /home/pi/env/Raspbeery2/app.py
sudo systemctl daemon-reload
sudo systemctl enable app.service
sudo systemctl start app.service

sudo cp /home/pi/env/Raspbeery2/raspbeery.service /lib/systemd/system

sudo chmod 644 /lib/systemd/system/raspbeery.service
sudo chmod +x /home/pi/env/Raspbeery2/raspbeery.py
sudo systemctl daemon-reload
sudo systemctl enable app.service
sudo systemctl start app.service

}



# --- RUN the functions
killpython
input_UI
system_update_light
#system_update_UI
install_dependencies
enable_I2C
#modify_RClocal cancellato
fn_hostapd
fn_dnsmasq
fn_dhcpcd
fn_ifnames
#install_mjpegstr
#install_squid3
install_nginx
install_Raspbeery # this should be called before the DHT22 , SPI and BMP due to local library references
#install_DHT22lib cancellato
#install_SPIlib cancellato
#install_MQTTsupport cancellato
edit_defaultnetworkdb
#edit_networkdb
#iptables_blockports
apply_newhostname
copy_services
echo "installation is finished!!! "
ask_reboot
