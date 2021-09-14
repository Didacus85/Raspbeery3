#######################################

###  https://raspberrypi.stackexchange.com/questions/100195/automatically-create-hotspot-if-no-network-is-available
###  https://github.com/0unknwn/auto-hotspot

sudo chmod -R 777 /etc/wpa_supplicant

#######################################
### copiare in etc/wpa_supplicant/wpa_supplicant.conf

ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=IT

ap_scan=1

### auto hotspot ###      # has to be the first network section!                                                                                  
network={
    priority=0            # Lowest priority, so wpa_supplicant prefers the other networks below 
    ssid="Raspbeery Hotspot"    # your access point's name                                                            
    mode=2                                                                       
    key_mgmt=WPA-PSK                                                             
    psk="birraiscoming"      # your access point's password                                    
    frequency=2462                                                               
}

### your network(s) ###    
network={                                                                                                                               
    ssid="WiFi is Coming"
    psk="birraiscoming"                                                 
} 


#######################################