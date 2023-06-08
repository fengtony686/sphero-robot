import os
import sys
import time
import sys
import tty
import threading
import termios
import cv2
import numpy as np
import logging
import speech_recognition as sr
import RPi.GPIO as GPIO
from sphero_sdk import SpheroRvrObserver
from aip import AipSpeech


APP_ID = '34269426'
API_KEY = 'VXSiXhkQXGPBW6o59V8zLrAG'
SECRET_KEY = 'e18pZGAqnGstEysHcYsX0b8OzyeAqZuj'
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
path = 'voices/myvoices.wav'
THRESHOLD = 0.3
FLAG=0
rvr = SpheroRvrObserver()
rvr.wake()
# give RVR time to wake up
time.sleep(2)
rvr.reset_yaw()
GPIO.setmode(GPIO.BOARD)  # BOARD编号方式，基于插座引脚编号
GPIO.setwarnings(False)
GPIO.setup(16, GPIO.OUT) # 输出模式#AIN1
GPIO.setup(18, GPIO.OUT) #AIN2
GPIO.setup(31, GPIO.OUT) #BIN1
GPIO.setup(29, GPIO.OUT) #BIN2
GPIO.setup(35, GPIO.OUT)
GPIO.setup(37, GPIO.OUT)
pwm1=GPIO.PWM(35,50)
pwm2=GPIO.PWM(37,50)
pwm1.start(0)
pwm2.start(0)


# Use SpeechRecognition to record 使用语音识别包录制音频
def my_record(rate=16000):
    r = sr.Recognizer()
    with sr.Microphone(sample_rate=rate) as source:
        print("please say something")
        audio = r.listen(source)

    with open("voices/myvoices.wav", "wb") as f:
        f.write(audio.get_wav_data())
    print("录音完成！")

# 将语音转文本STT
def listen():
    # 读取录音文件
    with open(path, 'rb') as fp:
        voices = fp.read()
    try:
        # 参数dev_pid：1536普通话(支持简单的英文识别)、1537普通话(纯中文识别)、1737英语、1637粤语、1837四川话、1936普通>        result = client.asr(voices, 'wav', 16000, {'dev_pid': 1537, })
        result = client.asr(voices, 'wav', 16000, {'dev_pid': 1537, })
        # result = CLIENT.asr(get_file_content(path), 'wav', 16000, {'lan': 'zh', })
        # print(result)
        # print(result['result'][0])
        # print(result)
        result_text = result["result"][0]
        print("you said: " + result_text)
        return result_text
    except KeyError:
        print("KeyError")


#挖呀挖
def dig():

   GPIO.output(18, GPIO.LOW)#AIN2=0

   GPIO.output(16, GPIO.HIGH) #AIN1=1

   return

#转台正转
def table_forward():

   GPIO.output(29, GPIO.LOW) #BIN2=0

   GPIO.output(31, GPIO.HIGH)#BIN1=1

   return

#转台反转
def table_backward():

   GPIO.output(29, GPIO.HIGH) #BIN2=1

   GPIO.output(31, GPIO.LOW)#BIN1=0

   return

#挖掘停止
def stop_dig():

   GPIO.output(16, GPIO.LOW)

   GPIO.output(18, GPIO.LOW)

   return

#转台停止
def stop_table():

   GPIO.output(29, GPIO.LOW)

   GPIO.output(31, GPIO.LOW)

   return

def Move(Speed, Heading, Flags):
    rvr.drive_with_heading(
        speed=Speed,  # Valid speed values are 0-255
        heading=Heading,  # Valid heading values are 0-359
        flags=Flags, #0 for 1 back
        )

def rawMoveForward(speed):
    rvr.raw_motors(1, speed, 1, speed)

def rawMoveReverse(speed):
    rvr.raw_motors(2, speed, 2, speed)

def rawMoveLeft(speed):
    rvr.raw_motors(2, speed, 1, speed)

def rawMoveRight(speed):
    rvr.raw_motors(1, speed, 2, speed)

def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def readkey(getchar_fn=None):
    getchar = getchar_fn or readchar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1
    c3 = getchar()
    return chr(0x10 + ord(c3) - 65)


lock = threading.Lock()
angle = 0
def vehicleControlByKeyboard():
    global angle
    while True:
        key=readkey()
        if key=='w':
            Move(10, angle, 0)
            #rawMoveForward(35)
        elif key=='a':
            lock.acquire()
            angle -= 5
            if angle < 0:
                angle += 360
            lock.release()
            Move(30, angle, 0)
        elif key=='s':
            Move(10, angle, 1)
            #rawMoveReverse(35)
        elif key=='d':
            lock.acquire()
            angle += 5
            if angle >= 360:
                angle -= 360
            lock.release()
            Move(30, angle, 0)
        elif key=='o':
            table_forward()
        elif key=='p':
            table_backward()
        elif key=='l':
            stop_table()
        elif key=='q':
            break


def controlByVoice():
    global angle
    while True:
        my_record()
        rec_text = listen()
        if "听好" not in rec_text:
            continue
        if "急转" in rec_text:
            turningAngle = 45
        else:
            turningAngle = 10
        if "快" in rec_text:
            speed1 = 40
            speed2 = 20
        else:
            speed1 = 20
            speed2 = 10
        if "后" in rec_text:
            Move(speed2, angle, 1)
            #rawMoveReverse(speed2)
        if "前" in rec_text:
            Move(speed2, angle, 0)
            #rawMoveForward(speed2)
        if "左" in rec_text:
            lock.acquire()
            angle -= turningAngle
            if angle < 0:
                angle += 360
            lock.release()
            Move(speed1, angle, 0)
        if "右" in rec_text:
            lock.acquire()
            angle += turningAngle
            if angle >= 360:
                angle -= 360
            lock.release()
            Move(speed1, angle, 0)
        if "中文歌" in rec_text:
            os.system("mplayer ~/Music/ccp.mp3")
        if "英文歌" in rec_text:
            os.system("mplayer ~/Music/pop.mp3")

cap = cv2.VideoCapture(0)
def diggingLoop():
    while True:
        # object detection and digging
        ret, frame = cap.read()
        if not ret:
            print("No signal!")
            break
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_green = np.array([50, 50, 50])
        upper_green = np.array([70, 255, 255])

        mask_green = cv2.inRange(hsv, lower_green, upper_green)

        kernel = np.ones((5, 5), np.uint8)
        mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)
        mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)
        area_green = cv2.countNonZero(mask_green)
        proportion_green = area_green / frame.size
        if proportion_green >= THRESHOLD:
            print("begin dig")
            #table_forward()
            dig()
        else:
            #table_backward()
            stop_dig()

t1 = threading.Thread(target=vehicleControlByKeyboard)
t2 = threading.Thread(target=diggingLoop)
t3 = threading.Thread(target=controlByVoice)
t1.start()
t2.start()
t3.start()
t1.join()
t2.join()
t3.join()
