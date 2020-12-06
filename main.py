from flask import Flask, request, render_template, redirect
import json
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from telnetlib import Telnet

app = Flask(__name__, static_url_path='/static')
hosts = ["IP OR HOSTNAME","IP OR HOSTNAME","IP OR HOSTNAME"]
target_temp = 75
temp = 70
fah_running = True

def FAHrun():
    for host in hosts:
        tn = Telnet(host,36330)
        tn.read_until(b"> ")
        tn.write(b"unpause\n")
        tn.write(b"exit\n")
        print("[+] "+host + " has been started")


def FAHpause():
    for host in hosts:
        tn = Telnet(host,36330)
        tn.read_until(b"> ")
        tn.write(b"pause\n")
        tn.write(b"exit\n")
        print("[-] "+host + " has been stopped")
        
def FAHrunning():
    running = True
    runningcount = 0
    for host in hosts:
        tn = Telnet(host,36330)
        tn.read_until(b"> ").decode('ascii')
        tn.write(b"slot-info \n")
        response = tn.read_until(b"> ").decode('ascii')
        if "\"status\": \"PAUSED\"" in response:
            running = False
            print("[*] "+host + " is not running")
        else:
            print("[*] "+host + " is running")
            runningcount = runningcount + 1
        tn.write(b"exit\n")

    if not running and runningcount > 0:
        print("[!] FAH clients out of sync. stopping everything to resync.")
        FAHpause()
    return running


def thermostat():
    log_file = open("fahtemp.log", 'a')
    global temp
    global fah_running
    try:
        r = requests.get('http://[IP of ESP8622]/temperature')
        temp = float(r.text)
        fah_running = FAHrunning()
        if temp < target_temp and fah_running:
            print("Current temp ("+str(temp)+") < target temp ("+str(target_temp)+") and FAH is running. doing nothing!")
            log_file.write(str(round(time.time())) +","+str(temp)+","+str(target_temp)+", FAH is running\n")
            
        elif temp < target_temp and not fah_running:
            print("Current temp ("+str(temp)+") < target temp ("+str(target_temp)+") and FAH is not running. starting FAH!")
            FAHrun()
            log_file.write(str(round(time.time())) +","+str(temp)+","+str(target_temp)+", FAH is running\n")
            
        elif temp > target_temp and fah_running:
            print("Current temp ("+str(temp)+") > target temp ("+str(target_temp)+") and FAH is running. stoping FAH!")
            FAHpause()
            log_file.write(str(round(time.time())) +","+str(temp)+","+str(target_temp)+", FAH is not running\n")
            
        elif temp > target_temp and not fah_running:
            print("Current temp ("+str(temp)+") > target temp ("+str(target_temp)+") and FAH is not running. doing nothing!")
            log_file.write(str(round(time.time())) +","+str(temp)+","+str(target_temp)+", FAH is not running\n")

    except:
        print("[!] Can't get reading from sensor!")
        temp = "ERROR"
        log_file.write(str(round(time.time())) +","+str(temp)+","+str(target_temp)+", Sensor error!\n")
                
    log_file.close()
    


scheduler = BackgroundScheduler()
scheduler.add_job(func=thermostat, trigger="interval", seconds=30)
scheduler.start()

######################
#     main page
######################
# this sheet down, parses it, and then renders it
@app.route("/",methods=['GET'])
def hello():
    if fah_running:
        x = "running"
    else:
        x = "not running"
    data = {"target_temp" : target_temp, "temp" : temp, "fah_running" : x}
    return render_template('index.html', title='Home', data=data)

######################
# target temp up
######################
@app.route("/targettempup",methods=['GET'])
def targettempup():
    global target_temp
    target_temp = target_temp + 1
    return redirect("/", code=302)
    
######################
# target temp down
######################
@app.route("/targettempdown",methods=['GET'])
def targettempdown():
    global target_temp
    target_temp = target_temp - 1
    return redirect("/", code=302)

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=1337,use_reloader=False)