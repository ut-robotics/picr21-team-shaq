# Project in Competitive Robotics 2021 (Shaq team)

This repository contains code for the course "Project in Competitive Robotics" of team "Shaq"

## Running the code

The code runs on a computer located on the robot, so some kind of remote connection (ssh, for example) with it is required. If SSH is used and seeing processed images is required, then SSH connection should be established with X forwarding enabled:

```
ssh -X [username]@[host]
```

Before running game code itself, it is advised to calibrate detection of different colors.

### Calibration

To calibrate detection of a color, move to **tests** directory and run **calibrate.py** file along with desired color as an argument.

For example for calibrating green color, run this:

```
cd tests/
python3 calibrate.py green
```

*Note*: If your computer is relatively old, then it's advised not to run calibration remotely, but disconnect the camera from robot's computer, connect it to your computer and run script locally.

### Running WebSocket server

The robot depends on referee server to provide info about color of target basket and when to start or stop. By default robot will not do anything until it receives start signal directed to it. Therefore, unless some other WebSocket server is already provided, WebSocket server will need to be run before running the game code.

Move to **src** directory. Before running the server, open the file and change the value of *ipaddr* value to IP address of machine running the server. The port generally need not be changed. Run **server.py** file. Until client is connected it will not ouput anything. Once client successfully connected, you will be prompted to enter either **start** or **stop** to send appropriate signals. The content of both signals is contained in **config** directory as **referee_start.json** and **referee_stop.json** files which can be edited manually. Refer [here](https://github.com/ut-robotics/robot-basketball-manager) for more info on signals.

### Running game logic

Before running the code make sure that camera is connected to the robot computer and the mainboard is turned on.

Move to the **src** directory.

Game code is ran from **main.py** file. Before running the code, edit *referee_ip* variable to the IP-address of your WebSocket server and *robot_name* variable to the name used to identify your robot. Since the communication with the mainboard requires root, **main.py** and all files using *Communication* and *Movement* classes needs to be ran with root privileges:

```
sudo python3 main.py
```

However, if SSH is used and seeing images is also required, then SSH connection will need to be established with a **root** user first, and the file will need to be ran as a root user.

```
python3 main.py
```

If you do not need to output the images, comment following lines near the end of main try-block out:

```
cv2.imshow("View", frame)
cv2.imshow("Balls", ball_mask)
```
