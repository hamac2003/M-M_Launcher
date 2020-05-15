from scipy.spatial import distance as dist
from imutils import face_utils
import numpy as np
import imutils
import pickle
import dlib
import cv2
import math
import serial
import time
import sys
from loguru import logger
from sinric import Sinric

apiKey = "YourAPIKeyHere"

local_volume = 0

incrementVal = 11
decrementVal = 3 

landmarksToDraw = [17,8,26,30,39,42]
print("Loading Camera Calibration File...")
filehandler = open('calib_data_zoom.obj', 'rb') 
calib_data = pickle.load(filehandler)

count = 0

cam_calib = calib_data[0]
dist_calib = calib_data[1]
    
#2D image points. If you change the image, you need to change vector
image_points = np.array([], dtype="double")


# 3D model points.
model_points = np.array([                            
                            (0.0, 0.0, 0.0),             # Nose Tip
                            (0.0, -80.0, -30.0),         # Chin
                            (35.0, 35.0, -40.0),         # Right Eyebrow Outer Edge
                            (-35.0, 35.0, -40.0),        # Left Eyebrow Outer Edge
                            (-7.0, 16.1, -40.0),         # Left Eye Inner Corner
                            (7.0, 16.1, -40.0),          # Right Eye Inner Corner                        
                        ])


print("Loading Predictor...")
predictor = dlib.shape_predictor("../resources/shape_predictor_68_face_landmarks.dat")

print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe("deploy.prototxt.txt", "res10_300x300_ssd_iter_140000.caffemodel")

# Initialize some variables                                                                                                                                                                                                                             v b nbmb  3333333       q
rects = None
shape = None
frameNum = 0
testNum = 0
rects = []



class myGlobals:
    feederPos = 130
    on = True
    faceCenter = [0,0]
    yaw = 78
    tilt = 50
    rpm = 0

def setPowerState(did, value):
    logger.info("{} {}".format(did, value))
    if value == OFF:
        myGlobals.on = False
    else:
        myGlobals.on = True

def SetMute(did, value):
    logger.info("{} {}".format(did, value))


def AdjustVolume(did, volume, d_volume):
    logger.info("{} {} {}".format(did, volume, d_volume))
    local_volume = int(volume)
    myGlobals.feederPos = sendIt(local_volume)

def ChangeChannel(did, channel, channel_name):
    logger.info("{} {} {}".format(did, channel, channel_name))


def SkipChannels(did, channel_count):
    logger.info("{} {}".format(did, channel_count))


def Previous_Play(did, value):
    logger.info("{} {} ".format(did, value))


def SelectInput(did, value):
    logger.info("{} {} ".format(did, value))


def sendSerial(pan, tilt, RPM, feeder):
    P = "nP" + str(pan) + "\n"
    T = "nT" + str(tilt) + "\n"
    S = str(RPM) + "\n"
    F = "nF" + str(feeder) + "\n"
    print(P)
    turret.write(P.encode('utf-8'))
    line_0 = turret.readline().decode('utf-8').rstrip()
    time.sleep(0.1)

    turret.write(T.encode('utf-8'))
    line_1 = turret.readline().decode('utf-8').rstrip()
    time.sleep(0.1)

    turret.write(F.encode('utf-8'))
    line_2 = turret.readline().decode('utf-8').rstrip()
    time.sleep(0.1)

    flywheel.write(S.encode('utf-8'))
    print(line_0)
    print(line_1)
    print(line_2)

def locateUser():
    video_capture = cv2.VideoCapture(0)
    time.sleep(0.5)
    # Grab a single frame of video
    ret, frame = video_capture.read()
    height, width, channels = frame.shape
    video_capture.release()
    myFlag = False
    distance = -1

    small_frame = frame
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(small_frame, (300, 300)), 1.0,
		(300, 300), (104.0, 177.0, 123.0))
    # pass the blob through the network and obtain the detections and
    # predictions
    net.setInput(blob)
    detections = net.forward()


    if True:
        frameNum = 0
        face_locations = []
        #cv2.rectangle(frame, (0, 0), (80, 80), (255, 0, 0), -1)
        print("maybee heeeerrrre?")
        frameNum = 0
        # Find all the faces and face encodings in the current frame of video
        start = time.time()
        # detect faces in the grayscale frame
        rects = None

        # loop over the face detections
    # loop over the detections
    for i in range(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the
        # prediction
        confidence = detections[0, 0, i, 2]
        
        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence < 0.5:
            continue

        # compute the (x, y)-coordinates of the bounding box for the
        # object
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")
 
        # draw the bounding box of the face along with the associated
        # probability
        text = "{:.2f}%".format(confidence * 100)
        y = startY - 10 if startY - 10 > 10 else startY + 10
        cv2.rectangle(frame, (startX, startY), (endX, endY),
            (0, 0, 255), 2) 
        cv2.putText(frame, text, (startX, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                
        ROI_Rect = dlib.rectangle(startX,startY,endX,endY)

        shape = predictor(frame,ROI_Rect)
        shape = face_utils.shape_to_np(shape)
        
        if shape is not None:
            image_points = np.array([
                                    (0,0),
                                    (0,0),
                                    (0,0),
                                    (0,0),
                                    (0,0),
                                    (0,0),
                                    ], dtype=("double"))
            for i, index in enumerate(landmarksToDraw):
                (x,y) = shape[index]
                image_points[i][0] = np.float32(x)
                image_points[i][1] = np.float32(y)
                if False:
                    cv2.circle(frame, (x, y), 5, (255, 0, 255), -1)
                else:
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
            temp0 = image_points[3].copy()
            temp1 = image_points[0].copy()

            image_points[0] = temp0
            image_points[3] = temp1

            myGlobals.faceCenter = [(ROI_Rect.right() - ROI_Rect.left())/2 + ROI_Rect.left(), (ROI_Rect.bottom() - ROI_Rect.top())/2 + ROI_Rect.top()]

            (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, cam_calib, dist_calib, flags=cv2.SOLVEPNP_ITERATIVE)
            
            distance = (translation_vector[2]/10)/2.54
            x = abs(distance)
            myGlobals.rpm = int(0.0002 * (x * x * x) - 0.0908 * (x * x) + 21.297 * x + 525.69) + 200
            myFlag = True

    end = time.time()

    return myFlag, distance, frame
    
def sendIt(number2Send):
    flag, myDist, tempImage = locateUser()
    print(">>>>>>>>>>>>>>")
    print(flag)
    print(myDist)
    temp = myGlobals.feederPos
    if temp <= 5:
        temp = 130
        sendSerial(78,50,0,temp)
    elif flag:
        myGlobals.yaw = int((0.1171875) * (myGlobals.faceCenter[0] - 320))

        print(myGlobals.rpm)
        sendSerial(myGlobals.yaw + 78,95,myGlobals.rpm,temp)
        time.sleep(4)
        for i in range(number2Send):
            temp -= incrementVal
            sendSerial(myGlobals.yaw + 78,95,myGlobals.rpm,temp)
            time.sleep(1)
            temp += decrementVal
            sendSerial(myGlobals.yaw + 78,95,myGlobals.rpm,temp)
            time.sleep(1)
        sendSerial(0 + 78,50,0,temp)

    return temp

feederPositions = []



turret = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
turret.flush()

flywheel = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)
flywheel.flush()
time.sleep(1)

calcRPM = 0

feederSet = False

if __name__ == "__main__":
    sinric = Sinric(
        apiKey,
        callbacks={
            "setPowerState": setPowerState,
            "SetMute": SetMute,
            "AdjustVolume": AdjustVolume,
            "ChangeChannel": ChangeChannel,
            "SkipChannels": SkipChannels,
            "Previous": Previous_Play,
            "SelectInput": SelectInput,
        },
    )
    sinric.handle()
    
video_capture.release()