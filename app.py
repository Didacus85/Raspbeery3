from flask import Flask, request, session, g, redirect, url_for, abort, \
	 render_template, flash, _app_ctx_stack, jsonify , Response

import networkmod
import tempidbmod
import requests
import os

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	message=""
	error = None
	change=False
	username=logindbmod.getusername().lower() #always transform to lowercase
	password=logindbmod.getpassword()
	
	if request.method == 'POST':
		print(" LOGIN " , username)
		reqtype = request.form['button']
		if reqtype=="login":
			usernameform=request.form['username'].lower()
			passwordform=request.form['password']
			if (usernameform != username) or (passwordform != password):
				error = 'Invalid Credentials'
			else:
				session['logged_in'] = True
				#flash('You were logged in')   
				return redirect(url_for('show_entries'))

		elif reqtype=="change":
			print("Display change password interface")
			change=True
						
		elif reqtype=="save":
			print("saving new login password")
			usernameform=request.form['username'].lower()
			passwordform=request.form['password']
			newpassword=request.form['newpassword']
			if (usernameform != username) or (passwordform != password):
				error = 'Invalid Credentials'
				change=True
			else:
				isok1=logindbmod.changesavesetting('password',newpassword)
				if isok1:
					session['logged_in'] = True
					flash('New Password Saved')   
					return redirect(url_for('show_entries'))
				
		elif reqtype=="cancel":
			return redirect(url_for('show_entries'))
			
	elif request.method == 'GET':
		message = request.args.get('message')
		#print "we are in GETTTTTTTTTTTT  " , message

	return render_template('login.html', error=error, change=change, message=message )	

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	#flash('You were logged out')
	return redirect(url_for('show_entries'))

@app.route('/network/', methods=['GET', 'POST'])
def network():
	#if not session.get('logged_in'):
	#	return render_template('login.html',error=None, change=False)
	wifilist=[]
	savedssid=[]	
	filenamelist="wifi networks"
	
	print("visualizzazione menu network:")


	iplocal=networkmod.get_local_ip()
	iplocallist=networkmod.get_local_ip_list()
	ipext=networkmod.get_external_ip()
	iplocalwifi=networkmod.IPADDRESS
	ipport=networkmod.PUBLICPORT
	hostname=networkmod.gethostname()
	connectedssidlist=networkmod.connectedssid()
	if len(connectedssidlist)>0:
		connectedssid=connectedssidlist[0]
	else:
		connectedssid=""
	
	
	localwifisystem=networkmod.localwifisystem
	#print " localwifisystem = ", localwifisystem , " connectedssid ", connectedssid
	message=networkmod.networkdbmod.getstoredmessage()

	return render_template('network.html',filenamelist=filenamelist, connectedssid=connectedssid,localwifisystem=localwifisystem, ipext=ipext, iplocallist=iplocallist , iplocal=iplocal, iplocalwifi=iplocalwifi , ipport=ipport , hostname=hostname, message=message)

@app.route('/networksetting/', methods=['GET', 'POST'])
def networksetting():
	#if not session.get('logged_in'):
	#	return render_template('login.html',error=None, change=False)
	error = None
	
	Fake_password="AP-password"
	
	if request.method == 'POST':
		print(" here we are at network setting")
		reqtype = request.form['button']
		if reqtype=="save":
			print("saving network advanced setting")
			gotADDRESS=request.form['IPADDRESS']
			AP_SSID=request.form['AP_SSID']
			AP_PASSWORD=request.form['AP_PASSWORD']
			AP_TIME=request.form['AP_TIME']
			WIFIENDIS=request.form['WIFIENDIS']
			HOSTNAME=request.form['HOSTNAME']
			
			
			
			# Check
			isok1 , IPADDRESS = networkmod.IPv4fromString(gotADDRESS)
			isok2=False
			isok3=False
			if len(AP_PASSWORD)>7:
				isok2=True
			if len(AP_SSID)>3:
				isok3=True
			
			
			
			
			
			if isok1 and isok2 and isok3:
				
				# previous paramenters
				IPADDRESSold=networkmod.IPADDRESS
				AP_SSIDold=networkmod.localwifisystem	
				AP_TIMEold=str(networkmod.WAITTOCONNECT)
				HOSTNAMEold=networkmod.gethostname()
				WIFIENDISold=networkmod.WIFIENDIS
				
							
				
				print("save in network file in database")
				networkdbmod.changesavesetting('LocalIPaddress',IPADDRESS)
				networkdbmod.changesavesetting('LocalAPSSID',AP_SSID)
				networkdbmod.changesavesetting('APtime',AP_TIME)			
				networkdbmod.changesavesetting('WIFIENDIS',WIFIENDIS)
				
				# save and change values in the HOSTAPD config file
				sysconfigfilemod.hostapdsavechangerow("ssid",AP_SSID)
				if AP_PASSWORD!=Fake_password:
					# change password in the HOSTAPD config file
					sysconfigfilemod.hostapdsavechangerow("wpa_passphrase",AP_PASSWORD)
					print("password changed")
				else:
					AP_PASSWORD=""
					
				if IPADDRESSold!=IPADDRESS:
					# save changes in DHCPCD confign file
					sysconfigfilemod.modifydhcpcdconfigfile(IPADDRESSold, IPADDRESS)
		
					# save changes in DNSMASQ confign file				
					sysconfigfilemod.modifydnsmasqconfigfile(IPADDRESSold, IPADDRESS)			
				
				if HOSTNAME!=HOSTNAMEold:
					networkmod.setnewhostname(HOSTNAME)
									
				
				# proceed with changes
				networkmod.applyparameterschange(AP_SSID, AP_PASSWORD, IPADDRESS)
				networkmod.WAITTOCONNECT=AP_TIME
				networkmod.WIFIENDIS=WIFIENDIS
				
				# Change hostapd file first row with HERE
				data=[]
				networkdbmod.readdata(data)
				sysconfigfilemod.hostapdsavechangerow_spec(data)	
				
				if WIFIENDISold!=WIFIENDIS:
					if WIFIENDIS=="Disabled":
						networkmod.Disable_WiFi()	
					else:
						networkmod.connect_network()		

				flash('Network setting Saved')   
				return redirect(url_for('network'))
			else:
				if not isok1:
					flash('please input valid IP address','danger') 				
				if not isok2:
					flash('please input password longer than 7 characters','danger') 
				if not isok3:
					flash('please input SSID longer than 3 characters','danger') 
		elif reqtype=="cancel":
			return redirect(url_for('network'))
	

	HOSTNAME=networkmod.gethostname()
	iplocal=networkmod.get_local_ip()
	IPADDRESS=networkmod.IPADDRESS
	PORT=networkmod.PUBLICPORT
	AP_SSID=networkmod.localwifisystem	
	AP_TIME=str(networkmod.WAITTOCONNECT)
	WIFIENDIS=networkmod.WIFIENDIS
	connectedssidlist=networkmod.connectedssid()
	if len(connectedssidlist)>0:
		connectedssid=connectedssidlist[0]
	else:
		connectedssid=""	
	AP_PASSWORD=Fake_password



	return render_template('networksetting.html', IPADDRESS=IPADDRESS, AP_SSID=AP_SSID, AP_PASSWORD=AP_PASSWORD, AP_TIME=AP_TIME , HOSTNAME=HOSTNAME, WIFIENDIS=WIFIENDIS)	

@app.route('/wificonfig/', methods=['GET', 'POST'])
def wificonfig():
	##if not session.get('logged_in'):
	#	return render_template('login.html',error=None, change=False)
	print("method " , request.method)
	if request.method == 'GET':
		ssid = request.args.get('ssid')
		print(" argument = ", ssid)

	if request.method == 'POST':
		ssid = request.form['ssid']
		if request.form['buttonsub'] == "Save":
			password=request.form['password']
			#networkmod.savewifi(ssid, password)
			networkmod.waitandsavewifiandconnect(7,ssid,password)	
			#redirect to login	
			#session.pop('logged_in', None)
			return redirect(url_for('/', message="Please wait until the WiFi disconnect and reconnect"))
			
		elif request.form['buttonsub'] == "Forget":
			print("forget")		
			networkmod.waitandremovewifi(7,ssid)
			print("remove network ", ssid)
			print("Try to connect AP")
			networkmod.waitandconnect_AP(9)
			#session.pop('logged_in', None)
			return redirect(url_for('/', message="Please wait until the WiFi disconnect and reconnect"))
			
		else:
			print("cancel")
			return redirect(url_for('network'))

	return render_template('wificonfig.html', ssid=ssid)


@app.route('/settings/', methods=['GET', 'POST'])
def settings():
	#if not session.get('logged_in'):
	#	return render_template('login.html',error=None, change=False)

	if request.method == 'POST':
		if request.form['impostatempi'] == "IMPOSTA TEMPI":
			numCicliPrepara = request.form['numCicliPrepara']
			tempidbmod.changesavesetting("numCicliPrepara", numCicliPrepara)
			
			timeVuoto = request.form['timeVuoto']
			tempidbmod.changesavesetting("timeVuoto", timeVuoto)

			timeCo2 = request.form['timeCo2']
			tempidbmod.changesavesetting("timeCo2", timeCo2)

			timeCo2Sfiato = request.form['timeCo2Sfiato']
			tempidbmod.changesavesetting("timeCo2Sfiato", timeCo2Sfiato)

			timeBirraRiempimento = request.form['timeBirraRiempimento']
			tempidbmod.changesavesetting("timeBirraRiempimento", timeBirraRiempimento)

			timeBirraAttesa = request.form['timeBirraAttesa']
			tempidbmod.changesavesetting("timeBirraAttesa", timeBirraAttesa)

			timeSfiato = request.form['timeSfiato']
			tempidbmod.changesavesetting("timeSfiato", timeSfiato)


		if request.form['impostatempi'] == "Tempistandard":
			print("Tempistandard ")
			tempidbmod.restoredefault()
	
	return render_template('settings.html', numCicliPrepara=tempidbmod.getNumCicliPrepara(), timeVuoto=tempidbmod.getTimeVuoto(), timeCo2=tempidbmod.getTimeCo2(), timeCo2Sfiato=tempidbmod.getTimeCo2Sfiato(), timeBirraRiempimento=tempidbmod.getTimeBirraRiempimento(), timeBirraAttesa=tempidbmod.getTimeBirraAttesa(), timeSfiato=tempidbmod.getTimeSfiato() )


@app.route('/system/', methods=['GET', 'POST'])
def system():
	#if not session.get('logged_in'):
	#	return render_template('login.html',error=None, change=False)

	if request.method == 'POST':
		if request.form['dosystemactions'] == "REBOOT":
			os.system('sudo reboot now')

		if request.form['dosystemactions'] == "SHUTDOWN":
			os.system('sudo shutdown now')
			
		if request.form['dosystemactions'] == "GIT PULL":
			os.system('cd /home/pi/env/Raspbeery3')
			os.system('git fetch origin master')
			os.system('git reset --hard origin/master')
			os.system('git pull origin master')
			os.system('sudo reboot now')
			
	
	return render_template('system.html')


@app.route('/actions/', methods=['GET', 'POST'])
def actions():
	#if not session.get('logged_in'):
	#	return render_template('login.html',error=None, change=False)
	
	if request.method == 'POST':
		os.system('sudo python3 /home/pi/env/Raspbeery3/raspbeery_1.py -a"'+request.form['azionetxt']+'"')
			
	return render_template('actions.html' )


if __name__ == "__main__":
    app.run(debug=True)
