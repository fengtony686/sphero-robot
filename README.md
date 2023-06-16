# README

This project revolves around a Sphero RVR-based robot, utilizing the [Sphero SDK](https://github.com/sphero-inc/sphero-sdk-raspberrypi-python) and is designed to run on a Raspberry-Pi. 
The robot is equipped with three primary functionalities:

`diggingLoop`:
The `diggingLoop` function utilizes OpenCV to detect a particular color. 
Upon detection of the predefined color, and if the proportion of that color within the frame surpasses a specified threshold, 
the `dig` function is triggered. The dig function is customizable based on the specific needs of the user or the project.

`controlByVoice`:
The `controlByVoice` function employs voice-to-text APIs from Baidu to convert voice recordings into text commands. 
Upon detection of certain predefined commands, the Sphero RVR is programmed to move according to the instructions received.

`vehicleControlByKeyboard`:
The `vehicleControlByKeyboard` function is designed to detect keyboard inputs of 'w', 'a', 's', and 'd' and control the Sphero RVR's movements accordingly.

To ensure these functions operate smoothly and simultaneously, we employ multithreading. Additionally, to prevent the potential issue of deadlock, locks are implemented across these functions.
Ensure to run this code in the directory of the Sphero SDK on a Raspberry-Pi. Remember to include any additional instructions or information relevant to your project. Happy coding!
