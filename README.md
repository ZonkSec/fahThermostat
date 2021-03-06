# fahThermostat - Folding@Home Thermostat

A system that uses an ESP8622 to measure temperature and a python script that toggles folding@home clients via telnet api to regulate temperatures of a room.

* main.py is a flask server where the target temp can be controlled and it has a scheduled job that does the main thermostat loop and commands FAH clients.
* graph.py uses pandas and matplotlib to graph the systems results. Thanks to my friend Tony (@TMucia) for the help here!
* FAH_temp.ino is the firmware for ESP8622 that collects/averages samples and then hosts a webserver so main.py can retrieve temperatures.

Note: each FAH client must be configured to allow telnet access from IP where main.py is running.

![arch](arch.JPG)

here is what the flask web control looks like:

![web control](webcontrol.png)

some example charts. black line is target temp. squiggly line is actual temp, its red when FAH is running and blue when it is not.
![chart2](chart2.png)
![chart1](chart1.png)
