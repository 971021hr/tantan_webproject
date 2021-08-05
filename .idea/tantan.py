from flask import Flask, render_template
from numpy import arccos, double
from numpy.lib import r_
from pykinect2 import PyKinectV2, PyKinectRuntime
import pykinect2
from pykinect2.PyKinectV2 import *
from flask import redirect, Response, url_for
from flask import request
from livereload import Server

import ctypes
import _ctypes
import pygame
import sys
import math
import copy
import time
import numpy as np
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/my-link/')
def my_link():
    # pygame window 실행

    #BodyGame from GitHub draws skeletons (https://github.com/Kinect/PyKinect2/blob/master/examples/PyKinectBodyGame.py)
    # -*- coding:UTF-8 -*-

    #==================================
    pose_list = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]
    action_status = True
    action_count = [0,0,0]
    status = -1
    is_running = False
    #==================================
    result_list = []
    #==================================
    left_HipCnt = []
    right_HipCnt = []

    leftlungeCnt = []
    rightlungeCnt = []

    goodCnt = []
    squatCnt = []

    lpdCnt = []
    slrCnt = []

    squat_status = True

    # colors for drawing different bodies
    SKELETON_COLORS = [pygame.color.THECOLORS["red"],
                       pygame.color.THECOLORS["blue"],
                       pygame.color.THECOLORS["green"],
                       pygame.color.THECOLORS["orange"],
                       pygame.color.THECOLORS["purple"],
                       pygame.color.THECOLORS["yellow"],
                       pygame.color.THECOLORS["violet"]]

    #==================================
    def get_angle_v3(p1_1, p1_2, p2_1, p2_2, p3_1, p3_2):
        a = math.sqrt(pow(p1_1-p3_1,2) + pow(p1_2-p3_2, 2))
        b = math.sqrt(pow(p1_1-p2_1,2) + pow(p1_2-p2_2, 2))
        c = math.sqrt(pow(p2_1-p3_1,2) + pow(p2_2-p3_2, 2))

        temp = (pow(b,2) + pow(c,2) - pow(a,2))/(2*b*c)

        Angle = np.arccos(temp)
        Angle = Angle*(180 / math.pi)

        return Angle + 180 if Angle > 180 else Angle

    def text_objects(text,font, color = (0,0,0)):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()

    def mousePressed(event,self):
        (x,y) = event.pos
        if self.startScreen == True:
            if x in range(int(self.screen_width/2)//2-100, (int(self.screen_width/2)//2 +100)):
                if y in range(int(self.screen_height - self.screen_height/4-100)//2,(int(self.screen_height - self.screen_height/4)+100)//2):
                    self.startScreen = False
                    self.currPress = "Squat"
                if y in range(int(self.screen_height - self.screen_height/8-100)//2,(int(self.screen_height - self.screen_height/8)+100)//2):
                    self.startScreen = False
                    self.currPress = "Saved"

        elif self.currPress != "Main" and self.currPress != "SquatSummary" and self.moveDetected == True and self.jointDetected == True:
            if y in range(int(self.screen_height - self.screen_height/4)//2,(int(self.screen_height - self.screen_height/4)+100)//2):
                if x in range(int(self.screen_width/5)//2, (int(self.screen_width/5)//2 +100)):
                    self.currPress = "Main"
                if x in range(int(self.screen_width/5), (int(self.screen_width/5) +100)):
                    if self.currPress == "Squat":
                        self.currPress = "SquatSummary"
                    self.moveDetected = False
                    self.jointDetected = False

    def readFile(path):
        with open(path, "rt") as f:
            return f.read()

    def writeFile(path, contents):
        with open(path, "wt") as f:
            f.write(contents)

    class GameRuntime(object):
        def __init__(self):
            pygame.init()
            self.startScreen = False
            self.mainScreen = True
            self.time = time.strftime("%H:%M") + " " + time.strftime("%d/%m/%Y")
            self.moveNames = ["Squat"]

            self.currPress = "Squat"

            self.screen_width = 1920

            self.screen_height = 1080

            self.profile = "Left"

            self.squatSummaryList = []
            self.summaryList = []
            self.wristXList = []
            self.wristYList = []
            self.elbowList = []
            self.feetList = []
            self.kneeYList = []
            self.kneeXList = []
            self.spineBaseYList = []
            self.hipYList = []
            self.minspineBaseY = None
            self.maxspineBaseY = None
            self.minKneeY = None
            self.maxKnee = None
            self.minWristX = None
            self.maxWristX = None
            self.minWristY = None
            self.maxWristY = None
            self.minElbowX = None
            self.maxElbowX = None
            self.minFeetY = None
            self.maxFeetY = None
            self.minHipY = None
            self.maxHipY = None
            self.minKneeX = None
            self.maxKneeX = None
            self.curX = (None, None)
            self.curY = (None, None)


            self.moveDetected = False
            self.jointDetected = False


            # Used to manage how fast the screen updates
            self._clock = pygame.time.Clock()

            # Set the width and height of the window [width/2, height/2]
            self._screen = pygame.display.set_mode((960,540), pygame.HWSURFACE|pygame.DOUBLEBUF, 32)

            # Loop until the user clicks the close button.
            self._done = False

            # Kinect runtime object, we want color and body frames
            self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)

            # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
            self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)

            # here we will store skeleton data
            self._bodies = None

        def initialize(self):
            self.squatSummaryList = []
            self.summaryList = []
            self.wristXList = []
            self.wristYList = []
            self.elbowList = []
            self.feetList = []
            self.kneeYList = []
            self.kneeXList = []
            self.spineBaseYList = []
            self.hipYList = []
            self.minspineBaseY = None
            self.maxspineBaseY = None
            self.minKneeY = None
            self.maxKnee = None
            self.minWristX = None
            self.maxWristX = None
            self.minWristY = None
            self.maxWristY = None
            self.minElbowX = None
            self.maxElbowX = None
            self.minFeetY = None
            self.maxFeetY = None
            self.minHipY = None
            self.maxHipY = None
            self.minKneeX = None
            self.maxKneeX = None
            self.curX = (None, None)
            self.curY = (None, None)
            self.l_angle = None
            self.r_angle = None

            self.moveDetected = False
            self.jointDetected = False

        def draw_title(self):
            text = pygame.font.Font("freesansbold.ttf",200)
            textSurf, textRect = text_objects("KinectLift", text, (255,255,255))
            textRect.center = (int(self.screen_width/2),int(self.screen_height/2))
            self._frame_surface.blit(textSurf,textRect)


        def draw_squatSummaryPage(self):

            if self.squatSummaryList == []:
                text = pygame.font.Font("freesansbold.ttf",30)
                textSurf, textRect = text_objects("", text)
                textRect.center = (int(self.screen_width/2),int(self.screen_height)/3)
                self._frame_surface.blit(textSurf,textRect)

            text = pygame.font.Font("freesansbold.ttf",30)
            textSurf1, textRect1 = text_objects("Click to return to main menu..", text)
            textRect1.center = (int(self.screen_width - self.screen_width/6.5),int(self.screen_height - self.screen_height/20))
            self._frame_surface.blit(textSurf1,textRect1)

            for i in range(len(self.squatSummaryList)):
                move = self.squatSummaryList[i]
                if move == "Knee came too forward":
                    move = " Knee came too forward"
                if move == "Partial rep":
                    move = " Partial rep"
                if move == "Bar is not in line with feet":
                    move = "Bar is not in line with feet "
                if move == "Good":
                    move = "Good"
                textSurf1, textRect1 = text_objects(move, text)
                textRect1.center = (int(self.screen_width/2),100 +int(self.screen_height/5)+100*i)
                self._frame_surface.blit(textSurf1,textRect1)

        def draw_moveScr(self):
            text = pygame.font.Font("freesansbold.ttf",100)
            textSurf, textRect = text_objects(self.currPress, text)
            textRect.center = (int(self.screen_width/2),int(self.screen_height/6))
            self._frame_surface.blit(textSurf,textRect)

            text1 = pygame.font.Font("freesansbold.ttf",50)
            textSurf1, textRect1 = text_objects(str(len(squatCnt)), text1)
            textRect1.center = (int(self.screen_width/2),int(1.5* self.screen_height/6))
            self._frame_surface.blit(textSurf1,textRect1)

            if self.jointDetected == False:
                text2 = pygame.font.Font("freesansbold.ttf",50)
                textSurf2, textRect2 = text_objects("", text1)
                textRect2.center = (int(self.screen_width/2),int(2* self.screen_height/6))
                self._frame_surface.blit(textSurf2,textRect2)
            else:
                text2 = pygame.font.Font("freesansbold.ttf",50)
                textSurf2, textRect2 = text_objects(str(len(squatCnt)), text1)
                textRect2.center = (int(self.screen_width/2),int(2* self.screen_height/6))
                self._frame_surface.blit(textSurf2,textRect2)


        def draw_body_bone(self, joints, jointPoints, color , joint0, joint1):
            joint0State = joints[joint0].TrackingState
            joint1State = joints[joint1].TrackingState

            # both joints are not tracked
            if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint1State == PyKinectV2.TrackingState_NotTracked):
                return

            # both joints are not *really* tracked
            if (joint0State == PyKinectV2.TrackingState_Inferred) and (joint1State == PyKinectV2.TrackingState_Inferred):
                return

            # ok, at least one is good
            start = (jointPoints[joint0].x, jointPoints[joint0].y)
            end = (jointPoints[joint1].x, jointPoints[joint1].y)

            try:
                pygame.draw.line(self._frame_surface, color, start, end, 8)
            except: # need to catch it due to possible invalid positions (with inf)
                pass

        def draw_body(self, joints, jointPoints, color):
            # Torso
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft)

            # Right Arm
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_HandRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandRight, PyKinectV2.JointType_HandTipRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_ThumbRight)

            # Left Arm
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_HandLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandLeft, PyKinectV2.JointType_HandTipLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_ThumbLeft)

            # Right Leg
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleRight, PyKinectV2.JointType_FootRight)

            # Left Leg
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleLeft, PyKinectV2.JointType_FootLeft)


        def draw_color_frame(self, frame, target_surface):
            target_surface.lock()
            address = self._kinect.surface_as_array(target_surface.get_buffer())
            ctypes.memmove(address, frame.ctypes.data, frame.size)
            del address
            target_surface.unlock()


        def run(self):
            # -------- Main Program Loop -----------
            while not self._done:
                self.squatSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mousePressed(event,self)

                # We have a color frame. Fill out back buffer surface with frame's data
                if self._kinect.has_new_color_frame():
                    frame = self._kinect.get_last_color_frame()
                    self.draw_color_frame(frame, self._frame_surface)
                    frame = None


                # We have a body frame, so can get skeletons
                if self._kinect.has_new_body_frame() and self.currPress != "Main":
                    self._bodies = self._kinect.get_last_body_frame()

                    if self._bodies is not None:

                        for i in range(0, self._kinect.max_body_count):
                            body = self._bodies.bodies[i]
                            if not body.is_tracked:
                                continue

                            joints = body.joints
                            # convert joint coordinates to color space
                            joint_points = self._kinect.body_joints_to_color_space(joints)
                            self.draw_body(joints, joint_points, SKELETON_COLORS[i])

                            joints = body.joints

                            # save the hand positions
                            if self.currPress == "Squat":
                                rightWristY = joints[PyKinectV2.JointType_WristRight].Position.y
                                leftWristY  = joints[PyKinectV2.JointType_WristLeft].Position.y
                                rightWristX = joints[PyKinectV2.JointType_WristRight].Position.x
                                leftWristX  = joints[PyKinectV2.JointType_WristLeft].Position.x

                                leftFootX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                                rightFootX = joints[PyKinectV2.JointType_AnkleRight].Position.x

                                spineBaseY = joints[PyKinectV2.JointType_SpineBase].Position.y
                                spineBaseX = joints[PyKinectV2.JointType_SpineBase].Position.x

                                rightKneeX = joints[PyKinectV2.JointType_KneeRight].Position.x
                                leftKneeX = joints[PyKinectV2.JointType_KneeLeft].Position.x
                                rightKneeY = joints[PyKinectV2.JointType_KneeRight].Position.y
                                leftKneeY = joints[PyKinectV2.JointType_KneeLeft].Position.y

                                rightHipY = joints[PyKinectV2.JointType_HipRight].Position.y
                                rightHipX = joints[PyKinectV2.JointType_HipRight].Position.x
                                leftHipY = joints[PyKinectV2.JointType_HipLeft].Position.y
                                leftHipX = joints[PyKinectV2.JointType_HipLeft].Position.x

                                spineShouldX =joints[PyKinectV2.JointType_SpineShoulder].Position.x
                                spineShouldY =joints[PyKinectV2.JointType_SpineShoulder].Position.y

                                leftankleX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                                leftankleY = joints[PyKinectV2.JointType_AnkleLeft].Position.y
                                rightankleX = joints[PyKinectV2.JointType_AnkleRight].Position.x
                                rightankleY = joints[PyKinectV2.JointType_AnkleRight].Position.y

                                Left_Knee_angle = get_angle_v3(leftHipX, leftHipY, leftKneeX, leftKneeY, leftankleX, leftankleY)
                                Left_Hip_angle = get_angle_v3(leftKneeX, leftKneeY, spineBaseX, spineBaseY, spineShouldX, spineShouldY)

                                self.curX = (leftWristX, leftKneeX)
                                self.curY = (leftWristY, leftFootX)
                                if (abs(leftWristY -spineBaseY) >= 0.3):
                                    self.moveDetected = True
                                    if  abs(leftWristX - rightWristX) < 0.1:
                                        self.wristXList.append(self.curX[0])
                                    self.wristYList.append(self.curY[0])
                                    self.kneeXList.append(self.curX[1])
                                    self.feetList.append(self.curY[1])
                                    if leftHipY > leftKneeY +.10:
                                        self.hipYList.append(leftHipY)
                                    self.kneeYList.append(leftKneeY)

                                if len(self.wristXList) != 0 and len(self.wristYList) != 0 and len(self.kneeYList) != 0 and len(self.kneeXList) != 0 and len(self.feetList) != 0 and len(self.hipYList) != 0 and (abs(leftWristY -spineBaseY) >= 0.3):
                                    (self.minWristX, self.maxWristX) = min(self.wristXList), max(self.wristXList)
                                    (self.minWristY, self.maxWristY) = min(self.wristYList), max(self.wristYList)
                                    (self.minKneeX, self.maxKneeX) = min(self.kneeXList), max(self.kneeXList)
                                    (self.minKneeY, self.maxKneeY) = min(self.kneeYList), max(self.kneeYList)
                                    (self.minHipY, self.maxHipY) = min(self.hipYList), max(self.hipYList)

                                    if Left_Knee_angle >= 160 :
                                        print("start squat !!")

                                    else :

                                        if (abs(self.feetList[0] - self.maxKneeX)) <= 0.8 and 70.0 < Left_Knee_angle < 140.0 and 70.0 < Left_Hip_angle:
                                            if squat_status == True:
                                                goodCnt.append(1)
                                            print("good cnt > ",len(goodCnt))
                                            # squat_status = False

                                            if len(goodCnt) >= 10:
                                                goodCnt = []
                                                squatCnt.append(1)
                                                fix = "Good"
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)
                                                print("squat count ========================================>>>> ",len(squatCnt))
                                                squat_status = False

                                        else:
                                            goodCnt = []
                                            squat_status = True
                                            print("Bad!")
                                            print("발끝 - 무릎 위치 : ", abs(self.feetList[0] - self.maxKneeX))
                                            print("왼 빵댕이 각도 {0}".format(Left_Hip_angle))
                                            print("왼쪽 무릎 각도 {0}".format(Left_Knee_angle))

                                            # 무릎을 더 굽혀주세요
                                            if Left_Knee_angle >= 115.0 :
                                                print("무릎을 더 굽혀주세요")
                                                fix = "Partial rep"
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)

                                            # 무릎이 발끝을 너무 많이 넘었어요
                                            if (abs(self.feetList[0] - self.maxKneeX)) > 0.3 :
                                                print("무릎이 발끝을 너무 많이 넘었어요")
                                                fix = "Knee came too forward"
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)

                                            # 허리를 좀 더 세워주세요
                                            if Left_Hip_angle < 70.0 :
                                                print("허리를 좀 더 세워주세요 ")
                                                fix = "Bar is not in line with feet"
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)

                self.draw_squatSummaryPage()

                # Draw graphics
                if self.startScreen == True:
                    self.draw_title()
                elif self.currPress != "Main":
                    if self.currPress == "SquatSummary":
                        self.draw_squatSummaryPage()
                    else:
                        self.draw_moveScr()

                h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
                target_height = int(h_to_w * self._screen.get_width())
                surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height))
                self._screen.blit(surface_to_draw, (0,0))
                surface_to_draw = None
                pygame.display.update()

            # Close our Kinect sensor, close the window and quit.
            self._kinect.close()
            pygame.quit()

    class GameRuntime_Lunge(object):
        def __init__(self):
            pygame.init()
            self.startScreen = False
            self.mainScreen = True
            self.time = time.strftime("%H:%M") + " " + time.strftime("%d/%m/%Y")
            self.moveNames = ["Lunge"]

            self.currPress = "Lunge"

            self.screen_width = 1920

            self.screen_height = 1080

            self.profile = "Left"

            self.squatSummaryList = []
            self.summaryList = []
            self.wristXList = []
            self.wristYList = []
            self.elbowList = []
            self.feetList = []
            self.kneeYList = []
            self.kneeXList = []
            self.spineBaseYList = []
            self.hipYList = []
            self.minspineBaseY = None
            self.maxspineBaseY = None
            self.minKneeY = None
            self.maxKnee = None
            self.minWristX = None
            self.maxWristX = None
            self.minWristY = None
            self.maxWristY = None
            self.minElbowX = None
            self.maxElbowX = None
            self.minFeetY = None
            self.maxFeetY = None
            self.minHipY = None
            self.maxHipY = None
            self.minKneeX = None
            self.maxKneeX = None
            self.curX = (None, None)
            self.curY = (None, None)


            self.moveDetected = False
            self.jointDetected = False


            # Used to manage how fast the screen updates
            self._clock = pygame.time.Clock()

            # Set the width and height of the window [width/2, height/2]
            self._screen = pygame.display.set_mode((960,540), pygame.HWSURFACE|pygame.DOUBLEBUF, 32)

            # Loop until the user clicks the close button.
            self._done = False

            # Kinect runtime object, we want color and body frames
            self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)

            # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
            self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)

            # here we will store skeleton data
            self._bodies = None

        def initialize(self):
            self.squatSummaryList = []
            self.summaryList = []
            self.wristXList = []
            self.wristYList = []
            self.elbowList = []
            self.feetList = []
            self.kneeYList = []
            self.kneeXList = []
            self.spineBaseYList = []
            self.hipYList = []
            self.minspineBaseY = None
            self.maxspineBaseY = None
            self.minKneeY = None
            self.maxKnee = None
            self.minWristX = None
            self.maxWristX = None
            self.minWristY = None
            self.maxWristY = None
            self.minElbowX = None
            self.maxElbowX = None
            self.minFeetY = None
            self.maxFeetY = None
            self.minHipY = None
            self.maxHipY = None
            self.minKneeX = None
            self.maxKneeX = None
            self.curX = (None, None)
            self.curY = (None, None)
            self.l_angle = None
            self.r_angle = None

            self.moveDetected = False
            self.jointDetected = False

        def draw_title(self):

            text = pygame.font.Font("freesansbold.ttf",200)
            textSurf, textRect = text_objects("KinectLift", text, (255,255,255))
            textRect.center = (int(self.screen_width/2),int(self.screen_height/2))
            self._frame_surface.blit(textSurf,textRect)

        def draw_squatSummaryPage(self):

            if self.squatSummaryList == []:
                text = pygame.font.Font("freesansbold.ttf",30)
                textSurf, textRect = text_objects("", text)
                textRect.center = (int(self.screen_width/2),int(self.screen_height)/3)
                self._frame_surface.blit(textSurf,textRect)

            text = pygame.font.Font("freesansbold.ttf",30)
            textSurf1, textRect1 = text_objects("Click to return to main menu..", text)
            textRect1.center = (int(self.screen_width - self.screen_width/6.5),int(self.screen_height - self.screen_height/20))
            self._frame_surface.blit(textSurf1,textRect1)

            for i in range(len(self.squatSummaryList)):
                move = self.squatSummaryList[i]
                if move == "Knee came too forward":
                    move = " Knee came too forward"
                if move == "Partial rep":
                    move = " Partial rep"
                if move == "Bar is not in line with feet":
                    move = "Bar is not in line with feet "
                if move == "Good":
                    move = "Good"
                textSurf1, textRect1 = text_objects(move, text)
                textRect1.center = (int(self.screen_width/2),100 +int(self.screen_height/5)+100*i)
                self._frame_surface.blit(textSurf1,textRect1)

        def draw_moveScr(self):
            text = pygame.font.Font("freesansbold.ttf",100)
            textSurf, textRect = text_objects(self.currPress, text)
            textRect.center = (int(self.screen_width/2),int(self.screen_height/6))
            self._frame_surface.blit(textSurf,textRect)

            text1 = pygame.font.Font("freesansbold.ttf",50)
            textSurf1, textRect1 = text_objects(str(len(squatCnt)), text1)
            textRect1.center = (int(self.screen_width/2),int(1.5* self.screen_height/6))
            self._frame_surface.blit(textSurf1,textRect1)

            if self.jointDetected == False:
                text2 = pygame.font.Font("freesansbold.ttf",50)
                textSurf2, textRect2 = text_objects("", text1)
                textRect2.center = (int(self.screen_width/2),int(2* self.screen_height/6))
                self._frame_surface.blit(textSurf2,textRect2)
            else:
                text2 = pygame.font.Font("freesansbold.ttf",50)
                textSurf2, textRect2 = text_objects(str(len(squatCnt)), text1)
                textRect2.center = (int(self.screen_width/2),int(2* self.screen_height/6))
                self._frame_surface.blit(textSurf2,textRect2)


        def draw_body_bone(self, joints, jointPoints, color , joint0, joint1):
            joint0State = joints[joint0].TrackingState
            joint1State = joints[joint1].TrackingState

            # both joints are not tracked
            if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint1State == PyKinectV2.TrackingState_NotTracked):
                return

            # both joints are not *really* tracked
            if (joint0State == PyKinectV2.TrackingState_Inferred) and (joint1State == PyKinectV2.TrackingState_Inferred):
                return

            # ok, at least one is good
            start = (jointPoints[joint0].x, jointPoints[joint0].y)
            end = (jointPoints[joint1].x, jointPoints[joint1].y)

            try:
                pygame.draw.line(self._frame_surface, color, start, end, 8)
            except: # need to catch it due to possible invalid positions (with inf)
                pass

        def draw_body(self, joints, jointPoints, color):
            # Torso
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft)

            # Right Arm
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_HandRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandRight, PyKinectV2.JointType_HandTipRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_ThumbRight)

            # Left Arm
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_HandLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandLeft, PyKinectV2.JointType_HandTipLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_ThumbLeft)

            # Right Leg
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleRight, PyKinectV2.JointType_FootRight)

            # Left Leg
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleLeft, PyKinectV2.JointType_FootLeft)


        def draw_color_frame(self, frame, target_surface):
            target_surface.lock()
            address = self._kinect.surface_as_array(target_surface.get_buffer())
            ctypes.memmove(address, frame.ctypes.data, frame.size)
            del address
            target_surface.unlock()


        def run(self):
            # -------- Main Program Loop -----------
            while not self._done:
                self.squatSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mousePressed(event,self)

                # We have a color frame. Fill out back buffer surface with frame's data
                if self._kinect.has_new_color_frame():
                    frame = self._kinect.get_last_color_frame()
                    self.draw_color_frame(frame, self._frame_surface)
                    frame = None


                # We have a body frame, so can get skeletons
                if self._kinect.has_new_body_frame() and self.currPress != "Main":
                    self._bodies = self._kinect.get_last_body_frame()

                    if self._bodies is not None:

                        for i in range(0, self._kinect.max_body_count):
                            body = self._bodies.bodies[i]
                            if not body.is_tracked:
                                continue

                            joints = body.joints
                            # convert joint coordinates to color space
                            joint_points = self._kinect.body_joints_to_color_space(joints)
                            self.draw_body(joints, joint_points, SKELETON_COLORS[i])

                            joints = body.joints

                            # 관절 좌표 변수
                            headX = joints[PyKinectV2.JointType_Head].Position.x
                            headY = joints[PyKinectV2.JointType_Head].Position.y
                            headZ = joints[PyKinectV2.JointType_Head].Position.z

                            rightWristY = joints[PyKinectV2.JointType_WristRight].Position.y
                            leftWristY  = joints[PyKinectV2.JointType_WristLeft].Position.y
                            rightWristX = joints[PyKinectV2.JointType_WristRight].Position.x
                            leftWristX  = joints[PyKinectV2.JointType_WristLeft].Position.x

                            leftFootX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                            rightFootX = joints[PyKinectV2.JointType_AnkleRight].Position.x

                            spineBaseY = joints[PyKinectV2.JointType_SpineBase].Position.y
                            spineBaseX = joints[PyKinectV2.JointType_SpineBase].Position.x
                            spineBaseZ = joints[PyKinectV2.JointType_SpineBase].Position.z

                            rightKneeX = joints[PyKinectV2.JointType_KneeRight].Position.x
                            leftKneeX = joints[PyKinectV2.JointType_KneeLeft].Position.x
                            rightKneeY = joints[PyKinectV2.JointType_KneeRight].Position.y
                            leftKneeY = joints[PyKinectV2.JointType_KneeLeft].Position.y

                            rightHipY = joints[PyKinectV2.JointType_HipRight].Position.y
                            rightHipX = joints[PyKinectV2.JointType_HipRight].Position.x
                            leftHipY = joints[PyKinectV2.JointType_HipLeft].Position.y
                            leftHipX = joints[PyKinectV2.JointType_HipLeft].Position.x

                            leftankleX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                            leftankleY = joints[PyKinectV2.JointType_AnkleLeft].Position.y
                            rightankleX = joints[PyKinectV2.JointType_AnkleRight].Position.x
                            rightankleY = joints[PyKinectV2.JointType_AnkleRight].Position.y

                            # Lunge
                            if self.currPress == "Lunge":

                                Left_Knee_angle = get_angle_v3(leftHipX, leftHipY, leftKneeX, leftKneeY, leftankleX, leftankleY)
                                Right_Knee_angle = get_angle_v3(rightHipX, rightHipY, rightKneeX, rightKneeY, rightankleX, rightankleY)

                                self.curX = (leftWristX, leftKneeX)
                                self.curY = (leftWristY, leftFootX)
                                if (abs(leftWristY -spineBaseY) >= 0.3):
                                    self.moveDetected = True
                                    if  abs(leftWristX - rightWristX) < 0.1:
                                        self.wristXList.append(self.curX[0])
                                    self.wristYList.append(self.curY[0])
                                    self.kneeXList.append(self.curX[1])
                                    self.feetList.append(self.curY[1])
                                    if leftHipY > leftKneeY +.10:
                                        self.hipYList.append(leftHipY)
                                    self.kneeYList.append(leftKneeY)

                                if len(self.wristXList) != 0 and len(self.wristYList) != 0 and len(self.kneeYList) != 0 and len(self.kneeXList) != 0 and len(self.feetList) != 0 and len(self.hipYList) != 0 and (abs(leftWristY -spineBaseY) >= 0.3):
                                    (self.minWristX, self.maxWristX) = min(self.wristXList), max(self.wristXList)
                                    (self.minWristY, self.maxWristY) = min(self.wristYList), max(self.wristYList)
                                    (self.minKneeX, self.maxKneeX) = min(self.kneeXList), max(self.kneeXList)
                                    (self.minKneeY, self.maxKneeY) = min(self.kneeYList), max(self.kneeYList)
                                    (self.minHipY, self.maxHipY) = min(self.hipYList), max(self.hipYList)

                                    # 왼쪽 다리 앞으로
                                    if (len(leftlungeCnt) < 1):
                                        if Left_Knee_angle >= 160 :
                                            print("start left lunge !!")

                                        else :
                                            if (abs(self.feetList[0] - self.maxKneeX)) <= 0.8 and 70.0 <= Left_Knee_angle <= 120.0 and abs(headX-spineBaseX) <= 0.2 and abs(headZ-spineBaseZ) <= 0.2:
                                                if squat_status == True:
                                                    goodCnt.append(1)
                                                print("good cnt > ",len(goodCnt))
                                                # squat_status = False

                                                if len(goodCnt) >= 7:
                                                    goodCnt = []
                                                    leftlungeCnt.append(1)
                                                    squatCnt.append(1)
                                                    fix = "Good"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)
                                                    print("left lunge count ========================================>>>> ",len(leftlungeCnt))
                                                    squat_status = False

                                            else:
                                                goodCnt = []
                                                squat_status = True
                                                print("Bad!")
                                                print("발끝 - 무릎 위치 : ", abs(self.feetList[0] - self.maxKneeX))
                                                print("왼쪽 무릎 각도 {0}".format(Left_Knee_angle))
                                                print("오른쪽 무릎 각도 {0}".format(Right_Knee_angle))
                                                print("허리1 <= 0.2 ?", abs(headX-spineBaseX))
                                                print("허리2 <= 0.2 ?", abs(headZ-spineBaseZ))

                                                # 앞무릎을 더 굽혀주세요
                                                if 70.0 > Left_Knee_angle or Left_Knee_angle > 120.0 :
                                                    print("왼무릎을 더 굽혀주세요")
                                                    fix = "Partial rep"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 뒷무릎을 더 굽혀주세요
                                                if 80 > Right_Knee_angle or Right_Knee_angle > 160.0 :
                                                    print("오른무릎을 더 굽혀주세요")
                                                    fix = "Partial rep"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 무릎이 발끝을 너무 많이 넘었어요
                                                if (abs(self.feetList[0] - self.maxKneeX)) > 0.8 :
                                                    print("무릎이 발끝을 너무 많이 넘었어요")
                                                    fix = "Knee came too forward"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 허리를 좀 더 세워주세요
                                                if abs(headX-spineBaseX) > 0.2 and abs(headZ-spineBaseZ) > 0.2 :
                                                    print("허리를 좀 더 세워주세요")
                                                    fix = "Bar is not in line with feet"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                    # 오른쪽 다리 앞으로
                                    else :
                                        if Right_Knee_angle >= 160 :
                                            print("start right lunge !!")

                                        else :
                                            if (abs(self.feetList[0] - self.maxKneeX)) <= 0.8 and 70.0 <= Right_Knee_angle <= 120.0 and abs(headX-spineBaseX) <= 0.2 and abs(headZ-spineBaseZ) <= 0.2:
                                                if squat_status == True:
                                                    goodCnt.append(1)
                                                print("good cnt > ",len(goodCnt))
                                                # squat_status = False

                                                if len(goodCnt) >= 7:
                                                    goodCnt = []
                                                    rightlungeCnt.append(1)
                                                    squatCnt.append(1)
                                                    fix = "Good"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)
                                                    print("right lunge count ========================================>>>> ",len(rightlungeCnt))
                                                    squat_status = False

                                            else:
                                                goodCnt = []
                                                squat_status = True
                                                print("Bad!")
                                                print("발끝 - 무릎 위치 : ", abs(self.feetList[0] - self.maxKneeX))
                                                print("왼쪽 무릎 각도 {0}".format(Left_Knee_angle))
                                                print("오른쪽 무릎 각도 {0}".format(Right_Knee_angle))
                                                print("허리1 <= 0.2 ?", abs(headX-spineBaseX))
                                                print("허리2 <= 0.2 ?", abs(headZ-spineBaseZ))

                                                # 앞무릎을 더 굽혀주세요
                                                if 70.0 > Right_Knee_angle or Right_Knee_angle > 120.0 :
                                                    print("오른무릎을 더 굽혀주세요")
                                                    fix = "Partial rep"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 뒷무릎을 더 굽혀주세요
                                                if 80 > Left_Knee_angle or Left_Knee_angle > 160.0 :
                                                    print("왼무릎을 더 굽혀주세요")
                                                    fix = "Partial rep"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 무릎이 발끝을 너무 많이 넘었어요
                                                if (abs(self.feetList[0] - self.maxKneeX)) > 0.8 :
                                                    print("무릎이 발끝을 너무 많이 넘었어요")
                                                    fix = "Knee came too forward"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 허리를 좀 더 세워주세요
                                                if abs(headX-spineBaseX) > 0.2 and abs(headY-spineBaseY) > 0.2 :
                                                    print("허리를 좀 더 세워주세요 ")
                                                    fix = "Bar is not in line with feet"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)


                self.draw_squatSummaryPage()

                # Draw graphics
                if self.startScreen == True:
                    self.draw_title()
                elif self.currPress != "Main":
                    if self.currPress == "SquatSummary":
                        self.draw_squatSummaryPage()
                    else:
                        self.draw_moveScr()

                h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
                target_height = int(h_to_w * self._screen.get_width())
                surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height))
                self._screen.blit(surface_to_draw, (0,0))
                surface_to_draw = None
                pygame.display.update()

            self._kinect.close()
            pygame.quit()

    class GameRuntime_Hip(object):
        def __init__(self):
            pygame.init()
            self.startScreen = False
            self.mainScreen = True
            self.time = time.strftime("%H:%M") + " " + time.strftime("%d/%m/%Y")
            self.moveNames = ["Squat", "Lunge", "Hip"]

            self.currPress = "Hip"

            self.screen_width = 1920

            self.screen_height = 1080

            self.profile = "Left"

            self.squatSummaryList = []
            self.summaryList = []
            self.wristXList = []
            self.wristYList = []
            self.elbowList = []
            self.feetList = []
            self.kneeYList = []
            self.kneeXList = []
            self.spineBaseYList = []
            self.hipYList = []
            self.minspineBaseY = None
            self.maxspineBaseY = None
            self.minKneeY = None
            self.maxKnee = None
            self.minWristX = None
            self.maxWristX = None
            self.minWristY = None
            self.maxWristY = None
            self.minElbowX = None
            self.maxElbowX = None
            self.minFeetY = None
            self.maxFeetY = None
            self.minHipY = None
            self.maxHipY = None
            self.minKneeX = None
            self.maxKneeX = None
            self.curX = (None, None)
            self.curY = (None, None)

            self.moveDetected = False
            self.jointDetected = False

            # Used to manage how fast the screen updates
            self._clock = pygame.time.Clock()

            # Set the width and height of the window [width/2, height/2]
            self._screen = pygame.display.set_mode((960,540), pygame.HWSURFACE|pygame.DOUBLEBUF, 32)

            # Loop until the user clicks the close button.
            self._done = False

            # Kinect runtime object, we want color and body frames
            self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)

            # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
            self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)

            # here we will store skeleton data
            self._bodies = None

        def initialize(self):
            self.squatSummaryList = []
            self.summaryList = []
            self.wristXList = []
            self.wristYList = []
            self.elbowList = []
            self.feetList = []
            self.kneeYList = []
            self.kneeXList = []
            self.spineBaseYList = []
            self.hipYList = []
            self.minspineBaseY = None
            self.maxspineBaseY = None
            self.minKneeY = None
            self.maxKnee = None
            self.minWristX = None
            self.maxWristX = None
            self.minWristY = None
            self.maxWristY = None
            self.minElbowX = None
            self.maxElbowX = None
            self.minFeetY = None
            self.maxFeetY = None
            self.minHipY = None
            self.maxHipY = None
            self.minKneeX = None
            self.maxKneeX = None
            self.curX = (None, None)
            self.curY = (None, None)
            self.l_angle = None
            self.r_angle = None

            self.moveDetected = False
            self.jointDetected = False

        def draw_title(self):
            text = pygame.font.Font("freesansbold.ttf",200)
            textSurf, textRect = text_objects("KinectLift", text, (255,255,255))
            textRect.center = (int(self.screen_width/2),int(self.screen_height/2))
            self._frame_surface.blit(textSurf,textRect)

        def draw_squatSummaryPage(self):

            if self.squatSummaryList == []:
                text = pygame.font.Font("freesansbold.ttf",30)
                textSurf, textRect = text_objects("", text)
                textRect.center = (int(self.screen_width/2),int(self.screen_height)/3)
                self._frame_surface.blit(textSurf,textRect)

            text = pygame.font.Font("freesansbold.ttf",30)
            textSurf1, textRect1 = text_objects("Click to return to main menu..", text)
            textRect1.center = (int(self.screen_width - self.screen_width/6.5),int(self.screen_height - self.screen_height/20))
            self._frame_surface.blit(textSurf1,textRect1)

            for i in range(len(self.squatSummaryList)):
                move = self.squatSummaryList[i]
                if move == "Knee came too forward":
                    move = " Knee came too forward"
                if move == "Partial rep":
                    move = " Partial rep"
                if move == "Bar is not in line with feet":
                    move = "Bar is not in line with feet "
                if move == "Good":
                    move = "Good"
                textSurf1, textRect1 = text_objects(move, text)
                textRect1.center = (int(self.screen_width/2),100 +int(self.screen_height/5)+100*i)
                self._frame_surface.blit(textSurf1,textRect1)

        def draw_moveScr(self):
            text = pygame.font.Font("freesansbold.ttf",100)
            textSurf, textRect = text_objects(self.currPress, text)
            textRect.center = (int(self.screen_width/2),int(self.screen_height/6))
            self._frame_surface.blit(textSurf,textRect)

            text1 = pygame.font.Font("freesansbold.ttf",50)
            textSurf1, textRect1 = text_objects(str(len(squatCnt)), text1)
            textRect1.center = (int(self.screen_width/2),int(1.5* self.screen_height/6))
            self._frame_surface.blit(textSurf1,textRect1)

            if self.jointDetected == False:
                text2 = pygame.font.Font("freesansbold.ttf",50)
                textSurf2, textRect2 = text_objects("", text1)
                textRect2.center = (int(self.screen_width/2),int(2* self.screen_height/6))
                self._frame_surface.blit(textSurf2,textRect2)
            else:
                text2 = pygame.font.Font("freesansbold.ttf",50)
                textSurf2, textRect2 = text_objects(str(len(squatCnt)), text1)
                textRect2.center = (int(self.screen_width/2),int(2* self.screen_height/6))
                self._frame_surface.blit(textSurf2,textRect2)


        def draw_body_bone(self, joints, jointPoints, color , joint0, joint1):
            joint0State = joints[joint0].TrackingState
            joint1State = joints[joint1].TrackingState

            # both joints are not tracked
            if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint1State == PyKinectV2.TrackingState_NotTracked):
                return

            # both joints are not *really* tracked
            if (joint0State == PyKinectV2.TrackingState_Inferred) and (joint1State == PyKinectV2.TrackingState_Inferred):
                return

            # ok, at least one is good
            start = (jointPoints[joint0].x, jointPoints[joint0].y)
            end = (jointPoints[joint1].x, jointPoints[joint1].y)

            try:
                pygame.draw.line(self._frame_surface, color, start, end, 8)
            except: # need to catch it due to possible invalid positions (with inf)
                pass

        def draw_body(self, joints, jointPoints, color):
            # Torso
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft)

            # Right Arm
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_HandRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandRight, PyKinectV2.JointType_HandTipRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_ThumbRight)

            # Left Arm
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_HandLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandLeft, PyKinectV2.JointType_HandTipLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_ThumbLeft)

            # Right Leg
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleRight, PyKinectV2.JointType_FootRight)

            # Left Leg
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleLeft, PyKinectV2.JointType_FootLeft)


        def draw_color_frame(self, frame, target_surface):
            target_surface.lock()
            address = self._kinect.surface_as_array(target_surface.get_buffer())
            ctypes.memmove(address, frame.ctypes.data, frame.size)
            del address
            target_surface.unlock()


        def run(self):
            # -------- Main Program Loop -----------
            while not self._done:
                self.squatSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mousePressed(event,self)

                # We have a color frame. Fill out back buffer surface with frame's data
                if self._kinect.has_new_color_frame():
                    frame = self._kinect.get_last_color_frame()
                    self.draw_color_frame(frame, self._frame_surface)
                    frame = None


                # We have a body frame, so can get skeletons
                if self._kinect.has_new_body_frame() and self.currPress != "Main":
                    self._bodies = self._kinect.get_last_body_frame()

                    if self._bodies is not None:

                        for i in range(0, self._kinect.max_body_count):
                            body = self._bodies.bodies[i]
                            if not body.is_tracked:
                                continue

                            joints = body.joints
                            # convert joint coordinates to color space
                            joint_points = self._kinect.body_joints_to_color_space(joints)
                            self.draw_body(joints, joint_points, SKELETON_COLORS[i])

                            joints = body.joints

                            headX = joints[PyKinectV2.JointType_Head].Position.x
                            headY = joints[PyKinectV2.JointType_Head].Position.y
                            headZ = joints[PyKinectV2.JointType_Head].Position.z

                            rightWristY = joints[PyKinectV2.JointType_WristRight].Position.y
                            leftWristY  = joints[PyKinectV2.JointType_WristLeft].Position.y
                            rightWristX = joints[PyKinectV2.JointType_WristRight].Position.x
                            leftWristX  = joints[PyKinectV2.JointType_WristLeft].Position.x

                            leftFootX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                            rightFootX = joints[PyKinectV2.JointType_AnkleRight].Position.x

                            spineBaseY = joints[PyKinectV2.JointType_SpineBase].Position.y
                            spineBaseX = joints[PyKinectV2.JointType_SpineBase].Position.x
                            spineBaseZ = joints[PyKinectV2.JointType_SpineBase].Position.z

                            rightKneeX = joints[PyKinectV2.JointType_KneeRight].Position.x
                            leftKneeX = joints[PyKinectV2.JointType_KneeLeft].Position.x
                            rightKneeY = joints[PyKinectV2.JointType_KneeRight].Position.y
                            leftKneeY = joints[PyKinectV2.JointType_KneeLeft].Position.y

                            rightHipY = joints[PyKinectV2.JointType_HipRight].Position.y
                            rightHipX = joints[PyKinectV2.JointType_HipRight].Position.x
                            leftHipY = joints[PyKinectV2.JointType_HipLeft].Position.y
                            leftHipX = joints[PyKinectV2.JointType_HipLeft].Position.x

                            # Hip
                            if self.currPress == "Hip":

                                Left_Hip_angle = get_angle_v3(spineBaseX, spineBaseY, leftHipX, leftHipY, leftKneeX, leftKneeY)
                                Right_Hip_angle = get_angle_v3(spineBaseX, spineBaseY, rightHipX, rightHipY, rightKneeX, rightKneeY)

                                self.curX = (leftWristX, leftKneeX)
                                self.curY = (leftWristY, leftFootX)

                                if (abs(leftWristY -spineBaseY) >= 0.3):
                                    # print(abs(headX-spineBaseX))
                                    self.moveDetected = True

                                    global left_HipCnt, right_HipCnt
                                    if(len(left_HipCnt) < 2) :
                                        if 85 <= Left_Hip_angle <= 95 :
                                            print("start left hip !!")

                                        else :

                                            if (Left_Hip_angle >= 140) :
                                                global hip_status
                                                if hip_status == True:
                                                    goodCnt.append(1)
                                                print("good cnt > ",len(goodCnt))
                                                print("왼쪽 성공 빵댕이 각도 {0}".format(Left_Hip_angle))

                                                if len(goodCnt) >= 6:
                                                    goodCnt = []
                                                    left_HipCnt.append(1)
                                                    squatCnt.append(1)
                                                    fix = "Good"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)
                                                    print("hip count ========================================>>>> ",len(left_HipCnt))
                                                    hip_status = False

                                            else:
                                                goodCnt = []
                                                hip_status = True
                                                print("Bad!")
                                                print("왼쪽 빵댕이 각도 {0}".format(Left_Hip_angle))

                                                # 허리를 좀 더 세워주세요 + 머리 뒤로 넘기지 마세요
                                                if abs(headX-spineBaseX) > 0.2 and abs(headZ-spineBaseZ) > 0.2 :
                                                    print("허리를 좀 더 세워주세요 ")
                                                    fix = "Bar is not in line with feet"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 엉덩이를 더 높이 올리세요
                                                if Left_Hip_angle < 140 :
                                                    print("왼쪽 엉덩이를 더 높이 올리세요")
                                                    fix = "Knee came too forward"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                    else :
                                        if 85 <= Right_Hip_angle <= 95 :
                                            print("start right hip !!")

                                        else :

                                            if (Right_Hip_angle >= 140) :
                                                if hip_status == True:
                                                    goodCnt.append(1)
                                                print("good cnt > ",len(goodCnt))
                                                print("오른쪽 성공 빵댕이 각도 {0}".format(Right_Hip_angle))
                                                # squat_status = False

                                                if len(goodCnt) >= 6:
                                                    goodCnt = []
                                                    right_HipCnt.append(1)
                                                    squatCnt.append(1)
                                                    fix = "Good"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)
                                                    print("hip count ========================================>>>> ",len(right_HipCnt))
                                                    hip_status = False

                                            else:
                                                goodCnt = []
                                                hip_status = True
                                                print("Bad!")
                                                print("오른쪽 빵댕이 각도 {0}".format(Right_Hip_angle))

                                                # 허리를 좀 더 세워주세요
                                                if abs(headX-spineBaseX) > 0.2 and abs(headZ-spineBaseZ) > 0.2 :
                                                    print("허리를 좀 더 세워주세요 ")
                                                    fix = "Bar is not in line with feet"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 엉덩이를 더 높이 올리세요
                                                if Right_Hip_angle < 140 :
                                                    print("오른쪽 엉덩이를 더 높이 올리세요")
                                                    fix = "Knee came too forward"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)


                self.draw_squatSummaryPage()

                # Draw graphics
                if self.startScreen == True:
                    self.draw_title()
                elif self.currPress != "Main":
                    if self.currPress == "SquatSummary":
                        self.draw_squatSummaryPage()
                    else:
                        self.draw_moveScr()

                h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
                target_height = int(h_to_w * self._screen.get_width())
                surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height))
                self._screen.blit(surface_to_draw, (0,0))
                surface_to_draw = None
                pygame.display.update()


            # Close our Kinect sensor, close the window and quit.
            self._kinect.close()
            pygame.quit()


    class GameRuntime_latPullDown(object):
        def __init__(self):
            pygame.init()
            self.startScreen = False
            self.mainScreen = True
            self.time = time.strftime("%H:%M") + " " + time.strftime("%d/%m/%Y")
            self.moveNames = ["LatPullDown"]

            self.currPress = "LatPullDown"

            self.screen_width = 1920

            self.screen_height = 1080

            self.profile = "Left"

            #add start
            self.headYList = []
            self.shouldXList = []
            self.shouldYList = []

            self.minShouldX = []
            self.maxShouldX = []
            self.minShouldY = []
            self.maxShouldY = []
            #add end

            self.latPullDownSummaryList = []
            self.summaryList = []
            self.wristXList = []
            self.wristYList = []
            self.elbowList = []
            self.feetList = []
            self.kneeYList = []
            self.kneeXList = []
            self.spineBaseYList = []
            self.hipYList = []
            self.minspineBaseY = None
            self.maxspineBaseY = None
            self.minKneeY = None
            self.maxKnee = None
            self.minWristX = None
            self.maxWristX = None
            self.minWristY = None
            self.maxWristY = None
            self.minElbowX = None
            self.maxElbowX = None
            self.minFeetY = None
            self.maxFeetY = None
            self.minHipY = None
            self.maxHipY = None
            self.minKneeX = None
            self.maxKneeX = None
            self.curX = (None, None)
            self.curY = (None, None)


            self.moveDetected = False
            self.jointDetected = False


            # Used to manage how fast the screen updates
            self._clock = pygame.time.Clock()

            # Set the width and height of the window [width/2, height/2]
            self._screen = pygame.display.set_mode((960,540), pygame.HWSURFACE|pygame.DOUBLEBUF, 32)

            # Loop until the user clicks the close button.
            self._done = False

            # Kinect runtime object, we want color and body frames
            self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)

            # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
            self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)

            # here we will store skeleton data
            self._bodies = None

        def initialize(self):
            self.latPullDownSummaryList = []
            self.summaryList = []

            self.headYList = []

            self.wristXList = []
            self.wristYList = []
            self.elbowList = []
            self.feetList = []
            self.kneeYList = []
            self.kneeXList = []
            self.spineBaseYList = []
            self.hipYList = []
            self.minspineBaseY = None
            self.maxspineBaseY = None
            self.minKneeY = None
            self.maxKnee = None
            self.minWristX = None
            self.maxWristX = None
            self.minWristY = None
            self.maxWristY = None
            self.minElbowX = None
            self.maxElbowX = None
            self.minFeetY = None
            self.maxFeetY = None
            self.minHipY = None
            self.maxHipY = None
            self.minKneeX = None
            self.maxKneeX = None
            self.curX = (None, None)
            self.curY = (None, None)
            self.l_angle = None
            self.r_angle = None

            self.moveDetected = False
            self.jointDetected = False

        def draw_title(self):
            text = pygame.font.Font("freesansbold.ttf",200)
            textSurf, textRect = text_objects("KinectLift", text, (255,255,255))
            textRect.center = (int(self.screen_width/2),int(self.screen_height/2))
            self._frame_surface.blit(textSurf,textRect)


        def draw_latPullDownSummaryPage(self):

            if self.latPullDownSummaryList == []:
                text = pygame.font.Font("freesansbold.ttf",30)
                textSurf, textRect = text_objects("", text)
                textRect.center = (int(self.screen_width/2),int(self.screen_height)/3)
                self._frame_surface.blit(textSurf,textRect)

            text = pygame.font.Font("freesansbold.ttf",30)
            textSurf1, textRect1 = text_objects("Click to return to main menu..", text)
            textRect1.center = (int(self.screen_width - self.screen_width/6.5),int(self.screen_height - self.screen_height/20))
            self._frame_surface.blit(textSurf1,textRect1)

            for i in range(len(self.latPullDownSummaryList)):
                move = self.latPullDownSummaryList[i]
                if move == "Hands should be in a straight line":
                    move = " Hands should be in a straight line"
                if move == "Armpits should be spaced apart":
                    move = "Armpits should be spaced apart"
                if move == "Good":
                    move = "Good"
                textSurf1, textRect1 = text_objects(move, text)
                textRect1.center = (int(self.screen_width/2),100 +int(self.screen_height/5)+100*i)
                self._frame_surface.blit(textSurf1,textRect1)

        def draw_moveScr(self):
            text = pygame.font.Font("freesansbold.ttf",100)
            textSurf, textRect = text_objects(self.currPress, text)
            textRect.center = (int(self.screen_width/2),int(self.screen_height/6))
            self._frame_surface.blit(textSurf,textRect)

            text1 = pygame.font.Font("freesansbold.ttf",50)
            textSurf1, textRect1 = text_objects(str(len(lpdCnt)), text1)
            textRect1.center = (int(self.screen_width/2),int(1.5* self.screen_height/6))
            self._frame_surface.blit(textSurf1,textRect1)

            if self.jointDetected == False:
                text2 = pygame.font.Font("freesansbold.ttf",50)
                textSurf2, textRect2 = text_objects("", text1)
                textRect2.center = (int(self.screen_width/2),int(2* self.screen_height/6))
                self._frame_surface.blit(textSurf2,textRect2)
            else:
                text2 = pygame.font.Font("freesansbold.ttf",50)
                textSurf2, textRect2 = text_objects(str(len(lpdCnt)), text1)
                textRect2.center = (int(self.screen_width/2),int(2* self.screen_height/6))
                self._frame_surface.blit(textSurf2,textRect2)


        def draw_body_bone(self, joints, jointPoints, color , joint0, joint1):
            joint0State = joints[joint0].TrackingState
            joint1State = joints[joint1].TrackingState

            # both joints are not tracked
            if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint1State == PyKinectV2.TrackingState_NotTracked):
                return

            # both joints are not *really* tracked
            if (joint0State == PyKinectV2.TrackingState_Inferred) and (joint1State == PyKinectV2.TrackingState_Inferred):
                return

            # ok, at least one is good
            start = (jointPoints[joint0].x, jointPoints[joint0].y)
            end = (jointPoints[joint1].x, jointPoints[joint1].y)

            try:
                pygame.draw.line(self._frame_surface, color, start, end, 8)
            except: # need to catch it due to possible invalid positions (with inf)
                pass

        def draw_body(self, joints, jointPoints, color):
            # Torso
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft)

            # Right Arm
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_HandRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandRight, PyKinectV2.JointType_HandTipRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_ThumbRight)

            # Left Arm
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_HandLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandLeft, PyKinectV2.JointType_HandTipLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_ThumbLeft)

            # Right Leg
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleRight, PyKinectV2.JointType_FootRight)

            # Left Leg
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleLeft, PyKinectV2.JointType_FootLeft)


        def draw_color_frame(self, frame, target_surface):
            target_surface.lock()
            address = self._kinect.surface_as_array(target_surface.get_buffer())
            ctypes.memmove(address, frame.ctypes.data, frame.size)
            del address
            target_surface.unlock()


        def run(self):
            global squat_status
            global goodCnt

            # -------- Main Program Loop -----------
            while not self._done:
                self.latPullDownSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mousePressed(event,self)

                # We have a color frame. Fill out back buffer surface with frame's data
                if self._kinect.has_new_color_frame():
                    frame = self._kinect.get_last_color_frame()
                    self.draw_color_frame(frame, self._frame_surface)
                    frame = None


                # We have a body frame, so can get skeletons
                if self._kinect.has_new_body_frame() and self.currPress != "Main":
                    self._bodies = self._kinect.get_last_body_frame()

                    if self._bodies is not None:

                        for i in range(0, self._kinect.max_body_count):
                            body = self._bodies.bodies[i]
                            if not body.is_tracked:
                                continue

                            joints = body.joints
                            # convert joint coordinates to color space
                            joint_points = self._kinect.body_joints_to_color_space(joints)
                            self.draw_body(joints, joint_points, SKELETON_COLORS[i])

                            joints = body.joints

                            # save the hand positions
                            if self.currPress == "LatPullDown":
                                headX = joints[PyKinectV2.JointType_Head].Position.x
                                headY = joints[PyKinectV2.JointType_Head].Position.y
                                headZ = joints[PyKinectV2.JointType_Head].Position.z

                                rightWristY = joints[PyKinectV2.JointType_WristRight].Position.y
                                leftWristY  = joints[PyKinectV2.JointType_WristLeft].Position.y
                                rightWristX = joints[PyKinectV2.JointType_WristRight].Position.x
                                leftWristX  = joints[PyKinectV2.JointType_WristLeft].Position.x

                                spineShouldX =joints[PyKinectV2.JointType_SpineShoulder].Position.x
                                spineShouldY =joints[PyKinectV2.JointType_SpineShoulder].Position.y
                                spineShouldZ =joints[PyKinectV2.JointType_SpineShoulder].Position.z

                                leftShoulderX = joints[PyKinectV2.JointType_ShoulderLeft].Position.x
                                rightShoulderX = joints[PyKinectV2.JointType_ShoulderRight].Position.x
                                leftShoulderY = joints[PyKinectV2.JointType_ShoulderLeft].Position.y
                                rightShoulderY = joints[PyKinectV2.JointType_ShoulderRight].Position.y

                                leftElbowX = joints[PyKinectV2.JointType_ElbowLeft].Position.x
                                leftElbowY = joints[PyKinectV2.JointType_ElbowLeft].Position.y

                                spinMidX = joints[PyKinectV2.JointType_SpineMid].Position.x
                                spinMidY = joints[PyKinectV2.JointType_SpineMid].Position.y
                                spinMidZ = joints[PyKinectV2.JointType_SpineMid].Position.z

                                rightKneeX = joints[PyKinectV2.JointType_KneeRight].Position.x
                                leftKneeX = joints[PyKinectV2.JointType_KneeLeft].Position.x
                                rightKneeY = joints[PyKinectV2.JointType_KneeRight].Position.y
                                leftKneeY = joints[PyKinectV2.JointType_KneeLeft].Position.y

                                leftFootX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                                rightFootX = joints[PyKinectV2.JointType_AnkleRight].Position.x

                                Left_Armpit_angle = get_angle_v3(spineShouldX, spineShouldY, leftShoulderX , leftShoulderY, leftElbowX, leftElbowY)

                                self.curX = (leftWristX, leftKneeX)
                                self.curY = (leftWristY, leftFootX)

                                # start point
                                # 왼쪽 손목과 오른쪽 손목이 spinMid Y보다 높을 경우 moveDetected를 True로 변경
                                if (leftWristY > spinMidY and rightWristY > spinMidY):
                                    self.moveDetected = True
                                    if  abs(leftWristX - rightWristX) < 0.1:
                                        self.wristXList.append(self.curX[0])
                                    self.wristYList.append(self.curY[0])

                                # 손목 배열이 잘 들어가고 & 손목 Y가 머리 Y보다 낮을 경우 운동 시작
                                # 손목 Y가 머리 Y보다 높아지는 경우 cnt 시작하기
                                if len(self.wristXList) != 0 and len(self.wristYList) != 0 :
                                    (self.minWristX, self.maxWristX) = min(self.wristXList), max(self.wristXList)
                                    (self.minWristY, self.maxWristY) = min(self.wristYList), max(self.wristYList)


                                    if (leftWristY < headY and rightWristY < headY) :
                                        print("start latPullDown !!")

                                    else :
                                        print("겨드랑이 각도 >> ", Left_Armpit_angle)
                                        print("머리 높이 - 손목 높이 >> ", round(headY - rightWristY,2))

                                        if (abs(headY - rightWristY) <= 0.2) and (abs(headY - leftWristY) <= 0.2) and Left_Armpit_angle > 30.0 :
                                            if squat_status == True:
                                                goodCnt.append(1)
                                            print("good cnt > ",len(goodCnt))
                                            # squat_status = False

                                            if len(goodCnt) >= 10:
                                                goodCnt = []
                                                lpdCnt.append(1)
                                                fix = "Good"
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)
                                                print("latPullDown count ========================================>>>> ",len(lpdCnt))
                                                squat_status = False

                                        else:
                                            goodCnt = []
                                            squat_status = True
                                            print("Bad!")

                                            # 손목을 일직선으로 내려야합니다.
                                            if (abs(self.minWristX - self.maxWristX)) > 0.3 :
                                                print("손목을 일직선으로 내려야합니다.")
                                                fix = "Hands should be in a straight line"
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)

                                            # 겨드랑이 간격을 벌려야합니다.
                                            if Left_Armpit_angle <= 30.0 :
                                                print("겨드랑이 간격을 벌려야합니다.")
                                                fix = "Armpits should be spaced apart"
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)

                self.draw_latPullDownSummaryPage()

                # Draw graphics
                if self.startScreen == True:
                    self.draw_title()
                elif self.currPress != "Main":
                    if self.currPress == "SquatSummary":
                        self.draw_latPullDownSummaryPage()
                    else:
                        self.draw_moveScr()

                h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
                target_height = int(h_to_w * self._screen.get_width())
                surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height))
                self._screen.blit(surface_to_draw, (0,0))
                surface_to_draw = None
                pygame.display.update()

            # Close our Kinect sensor, close the window and quit.
            self._kinect.close()
            pygame.quit()

    # Side Lateral Raise
    class GameRuntime_SLR(object):
        def __init__(self):
            pygame.init()
            self.startScreen = False
            self.mainScreen = True
            self.time = time.strftime("%H:%M") + " " + time.strftime("%d/%m/%Y")
            self.moveNames = ["SLR"]

            self.currPress = "SLR"

            self.screen_width = 1920

            self.screen_height = 1080

            self.profile = "Left"

            self.squatSummaryList = []
            self.summaryList = []
            self.wristXList = []
            self.wristYList = []
            self.elbowList = []
            self.feetList = []
            self.kneeYList = []
            self.kneeXList = []
            self.spineBaseYList = []
            self.hipYList = []
            self.minspineBaseY = None
            self.maxspineBaseY = None
            self.minKneeY = None
            self.maxKnee = None
            self.minWristX = None
            self.maxWristX = None
            self.minWristY = None
            self.maxWristY = None
            self.minElbowX = None
            self.maxElbowX = None
            self.minFeetY = None
            self.maxFeetY = None
            self.minHipY = None
            self.maxHipY = None
            self.minKneeX = None
            self.maxKneeX = None
            self.curX = (None, None)
            self.curY = (None, None)


            self.moveDetected = False
            self.jointDetected = False


            # Used to manage how fast the screen updates
            self._clock = pygame.time.Clock()

            # Set the width and height of the window [width/2, height/2]
            self._screen = pygame.display.set_mode((960,540), pygame.HWSURFACE|pygame.DOUBLEBUF, 32)

            # Loop until the user clicks the close button.
            self._done = False

            # Kinect runtime object, we want color and body frames
            self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)

            # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
            self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)

            # here we will store skeleton data
            self._bodies = None

        def initialize(self):
            self.squatSummaryList = []
            self.summaryList = []
            self.wristXList = []
            self.wristYList = []
            self.elbowList = []
            self.feetList = []
            self.kneeYList = []
            self.kneeXList = []
            self.spineBaseYList = []
            self.hipYList = []
            self.minspineBaseY = None
            self.maxspineBaseY = None
            self.minKneeY = None
            self.maxKnee = None
            self.minWristX = None
            self.maxWristX = None
            self.minWristY = None
            self.maxWristY = None
            self.minElbowX = None
            self.maxElbowX = None
            self.minFeetY = None
            self.maxFeetY = None
            self.minHipY = None
            self.maxHipY = None
            self.minKneeX = None
            self.maxKneeX = None
            self.curX = (None, None)
            self.curY = (None, None)
            self.l_angle = None
            self.r_angle = None

            self.moveDetected = False
            self.jointDetected = False

        def draw_title(self):

            text = pygame.font.Font("freesansbold.ttf",200)
            textSurf, textRect = text_objects("KinectLift", text, (255,255,255))
            textRect.center = (int(self.screen_width/2),int(self.screen_height/2))
            self._frame_surface.blit(textSurf,textRect)

        def draw_squatSummaryPage(self):

            if self.squatSummaryList == []:
                text = pygame.font.Font("freesansbold.ttf",30)
                textSurf, textRect = text_objects("", text)
                textRect.center = (int(self.screen_width/2),int(self.screen_height)/3)
                self._frame_surface.blit(textSurf,textRect)

            text = pygame.font.Font("freesansbold.ttf",30)
            textSurf1, textRect1 = text_objects("Click to return to main menu..", text)
            textRect1.center = (int(self.screen_width - self.screen_width/6.5),int(self.screen_height - self.screen_height/20))
            self._frame_surface.blit(textSurf1,textRect1)

            for i in range(len(self.squatSummaryList)):
                move = self.squatSummaryList[i]
                if move == "Knee came too forward":
                    move = " Knee came too forward"
                if move == "Partial rep":
                    move = " Partial rep"
                if move == "Bar is not in line with feet":
                    move = "Bar is not in line with feet "
                if move == "Good":
                    move = "Good"
                textSurf1, textRect1 = text_objects(move, text)
                textRect1.center = (int(self.screen_width/2),100 +int(self.screen_height/5)+100*i)
                self._frame_surface.blit(textSurf1,textRect1)

        def draw_moveScr(self):
            text = pygame.font.Font("freesansbold.ttf",100)
            textSurf, textRect = text_objects(self.currPress, text)
            textRect.center = (int(self.screen_width/2),int(self.screen_height/6))
            self._frame_surface.blit(textSurf,textRect)

            text1 = pygame.font.Font("freesansbold.ttf",50)
            textSurf1, textRect1 = text_objects(str(len(squatCnt)), text1)
            textRect1.center = (int(self.screen_width/2),int(1.5* self.screen_height/6))
            self._frame_surface.blit(textSurf1,textRect1)

            if self.jointDetected == False:
                text2 = pygame.font.Font("freesansbold.ttf",50)
                textSurf2, textRect2 = text_objects("", text1)
                textRect2.center = (int(self.screen_width/2),int(2* self.screen_height/6))
                self._frame_surface.blit(textSurf2,textRect2)
            else:
                text2 = pygame.font.Font("freesansbold.ttf",50)
                textSurf2, textRect2 = text_objects(str(len(squatCnt)), text1)
                textRect2.center = (int(self.screen_width/2),int(2* self.screen_height/6))
                self._frame_surface.blit(textSurf2,textRect2)


        def draw_body_bone(self, joints, jointPoints, color , joint0, joint1):
            joint0State = joints[joint0].TrackingState
            joint1State = joints[joint1].TrackingState

            # both joints are not tracked
            if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint1State == PyKinectV2.TrackingState_NotTracked):
                return

            # both joints are not *really* tracked
            if (joint0State == PyKinectV2.TrackingState_Inferred) and (joint1State == PyKinectV2.TrackingState_Inferred):
                return

            # ok, at least one is good
            start = (jointPoints[joint0].x, jointPoints[joint0].y)
            end = (jointPoints[joint1].x, jointPoints[joint1].y)

            try:
                pygame.draw.line(self._frame_surface, color, start, end, 8)
            except: # need to catch it due to possible invalid positions (with inf)
                pass

        def draw_body(self, joints, jointPoints, color):
            # Torso
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft)

            # Right Arm
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_HandRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandRight, PyKinectV2.JointType_HandTipRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_ThumbRight)

            # Left Arm
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_HandLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandLeft, PyKinectV2.JointType_HandTipLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_ThumbLeft)

            # Right Leg
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleRight, PyKinectV2.JointType_FootRight)

            # Left Leg
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft)
            self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleLeft, PyKinectV2.JointType_FootLeft)


        def draw_color_frame(self, frame, target_surface):
            target_surface.lock()
            address = self._kinect.surface_as_array(target_surface.get_buffer())
            ctypes.memmove(address, frame.ctypes.data, frame.size)
            del address
            target_surface.unlock()


        def run(self):
            # -------- Main Program Loop -----------
            while not self._done:
                self.squatSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mousePressed(event,self)

                # We have a color frame. Fill out back buffer surface with frame's data
                if self._kinect.has_new_color_frame():
                    frame = self._kinect.get_last_color_frame()
                    self.draw_color_frame(frame, self._frame_surface)
                    frame = None


                # We have a body frame, so can get skeletons
                if self._kinect.has_new_body_frame() and self.currPress != "Main":
                    self._bodies = self._kinect.get_last_body_frame()

                    if self._bodies is not None:

                        for i in range(0, self._kinect.max_body_count):
                            body = self._bodies.bodies[i]
                            if not body.is_tracked:
                                continue

                            joints = body.joints
                            # convert joint coordinates to color space
                            joint_points = self._kinect.body_joints_to_color_space(joints)
                            self.draw_body(joints, joint_points, SKELETON_COLORS[i])

                            joints = body.joints

                            # 관절 좌표 변수
                            headX = joints[PyKinectV2.JointType_Head].Position.x
                            headY = joints[PyKinectV2.JointType_Head].Position.y
                            headZ = joints[PyKinectV2.JointType_Head].Position.z

                            rightWristY = joints[PyKinectV2.JointType_WristRight].Position.y
                            leftWristY  = joints[PyKinectV2.JointType_WristLeft].Position.y
                            rightWristX = joints[PyKinectV2.JointType_WristRight].Position.x
                            leftWristX  = joints[PyKinectV2.JointType_WristLeft].Position.x
                            rightWristZ = joints[PyKinectV2.JointType_WristRight].Position.z
                            leftWristZ  = joints[PyKinectV2.JointType_WristLeft].Position.z

                            leftFootX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                            rightFootX = joints[PyKinectV2.JointType_AnkleRight].Position.x

                            spineBaseY = joints[PyKinectV2.JointType_SpineBase].Position.y
                            spineBaseX = joints[PyKinectV2.JointType_SpineBase].Position.x
                            spineBaseZ = joints[PyKinectV2.JointType_SpineBase].Position.z

                            spineShouldX =joints[PyKinectV2.JointType_SpineShoulder].Position.x
                            spineShouldY =joints[PyKinectV2.JointType_SpineShoulder].Position.y
                            spineShouldZ =joints[PyKinectV2.JointType_SpineShoulder].Position.z

                            rightKneeX = joints[PyKinectV2.JointType_KneeRight].Position.x
                            leftKneeX = joints[PyKinectV2.JointType_KneeLeft].Position.x
                            rightKneeY = joints[PyKinectV2.JointType_KneeRight].Position.y
                            leftKneeY = joints[PyKinectV2.JointType_KneeLeft].Position.y

                            rightHipY = joints[PyKinectV2.JointType_HipRight].Position.y
                            rightHipX = joints[PyKinectV2.JointType_HipRight].Position.x
                            leftHipY = joints[PyKinectV2.JointType_HipLeft].Position.y
                            leftHipX = joints[PyKinectV2.JointType_HipLeft].Position.x

                            leftankleX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                            leftankleY = joints[PyKinectV2.JointType_AnkleLeft].Position.y
                            rightankleX = joints[PyKinectV2.JointType_AnkleRight].Position.x
                            rightankleY = joints[PyKinectV2.JointType_AnkleRight].Position.y

                            leftsholderX = joints[PyKinectV2.JointType_ShoulderLeft].Position.x
                            leftsholderY = joints[PyKinectV2.JointType_ShoulderLeft].Position.y
                            rightsholderX = joints[PyKinectV2.JointType_ShoulderRight].Position.x
                            rightsholderY = joints[PyKinectV2.JointType_ShoulderRight].Position.y
                            leftelbowX= joints[PyKinectV2.JointType_ElbowLeft].Position.x
                            leftelbowY= joints[PyKinectV2.JointType_ElbowLeft].Position.y
                            rightelbowX= joints[PyKinectV2.JointType_ElbowRight].Position.x
                            rightelbowY= joints[PyKinectV2.JointType_ElbowRight].Position.y

                            # Side Lateral Raise
                            if self.currPress == "SLR":

                                Left_inArm_angle = get_angle_v3(leftelbowX, leftelbowY, leftsholderX, leftsholderY, spineShouldX, spineShouldY)
                                Right_inArm_angle = get_angle_v3(rightelbowX, rightelbowY, rightsholderX, rightsholderY, spineShouldX, spineShouldY)
                                Left_outArm_angle = get_angle_v3(leftWristX, leftWristY, leftelbowX, leftelbowY, leftsholderX, leftsholderY)
                                Right_outArm_angle = get_angle_v3(rightWristX, rightWristY, rightelbowX, rightelbowY, rightsholderX, rightsholderY)

                                self.curX = (leftWristX, leftKneeX)
                                self.curY = (leftWristY, leftFootX)
                                # if abs(leftelbowY - leftWristY) <= 0.16 :
                                if Left_inArm_angle > 145 or Right_inArm_angle > 145 :
                                    self.moveDetected = True

                                    # 왼쪽 다리 앞으로
                                    # if Left_inArm_angle < 120 :
                                    # if abs(leftelbowY - leftWristY) > 0.16 :
                                    if Left_inArm_angle < 150 or Right_inArm_angle < 150 :
                                        print("start slr !!")

                                    else :
                                        global squat_status, goodCnt
                                        if abs(leftWristZ - spineBaseZ) <= 0.2 and abs(rightWristZ - spineBaseZ) <= 0.2 and 155 <= Left_inArm_angle <= 180 and 155 <= Right_inArm_angle <= 180 \
                                                and 155 <= Left_outArm_angle <= 185 and 155 <= Right_outArm_angle <= 185 and abs(headX-spineBaseX) <= 0.2 and abs(headZ-spineBaseZ) <= 0.2:
                                            if squat_status == True:
                                                goodCnt.append(1)
                                            print("good cnt > ",len(goodCnt))
                                            # squat_status = False

                                            if len(goodCnt) >= 7:
                                                goodCnt = []
                                                slrCnt.append(1)
                                                squatCnt.append(1)
                                                fix = "Good"
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)
                                                print("left lunge count ========================================>>>> ",len(slrCnt))
                                                squat_status = False

                                            print("Good!")
                                            print("엘보우 x축-손목 x축 : ", abs(leftelbowX - leftWristX))
                                            print("엘보우 y축-손목 y축 : ", abs(leftelbowY - leftWristY))
                                            print("손목 - 척추 위치 : ", abs(leftWristZ - spineBaseZ), " ", abs(rightWristZ - spineBaseZ))
                                            print("왼쪽 팔 안쪽 각도 {0}".format(Left_inArm_angle))
                                            print("오른쪽 팔 안쪽 각도 {0}".format(Right_inArm_angle))
                                            print("왼쪽 팔 바깥쪽 각도 {0}".format(Left_outArm_angle))
                                            print("오른쪽 팔 바깥쪽 각도 {0}".format(Right_outArm_angle))
                                            print("허리1 <= 0.2 ?", abs(headX-spineBaseX))
                                            print("허리2 <= 0.2 ?", abs(headZ-spineBaseZ))

                                        else:
                                            goodCnt = []
                                            squat_status = True
                                            print("Bad!")
                                            print("엘보우 x축-손목 x축 : ", abs(leftelbowX - leftWristX))
                                            print("엘보우 y축-손목 y축 : ", abs(leftelbowY - leftWristY))
                                            print("손목 - 척추 위치 : ", abs(leftWristZ - spineBaseZ), " ", abs(rightWristZ - spineBaseZ))
                                            print("왼쪽 팔 안쪽 각도 {0}".format(Left_inArm_angle))
                                            print("오른쪽 팔 안쪽 각도 {0}".format(Right_inArm_angle))
                                            print("왼쪽 팔 바깥쪽 각도 {0}".format(Left_outArm_angle))
                                            print("오른쪽 팔 바깥쪽 각도 {0}".format(Right_outArm_angle))
                                            print("허리1 <= 0.2 ?", abs(headX-spineBaseX))
                                            print("허리2 <= 0.2 ?", abs(headZ-spineBaseZ))

                                            # 왼쪽 팔을 더 올려주세요
                                            if 155 > Left_inArm_angle :
                                                print("왼쪽 팔을 더 올려주세요")
                                                fix = "Left Arm Up"
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)

                                            # 왼쪽 팔을 조금 내려주세요
                                            if Left_inArm_angle > 180 :
                                                print("왼쪽 팔을 조금 내려주세요")
                                                fix = "Left Arm Down"
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)

                                            # 오른쪽 팔을 더 올려주세요
                                            if 155 > Right_inArm_angle :
                                                print("오른쪽 팔을 더 올려주세요")
                                                fix = "Right Arm Up"
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)

                                            # 오른쪽 팔을 조금 내려주세요
                                            if Right_inArm_angle > 180 :
                                                print("오른쪽 팔을 조금 내려주세요")
                                                fix = "Right Arm Down"
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)

                                            # 왼쪽 팔을 펴주세요
                                            if 155 > Left_outArm_angle :
                                                print("왼쪽 팔을 펴주세요")
                                                fix = "Left Arm Unfold"
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)

                                            # 오른쪽 팔을 펴주세요
                                            if 155 > Right_outArm_angle :
                                                print("오른쪽 팔을 펴주세요")
                                                fix = "Right Arm Unfold"
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)

                                            # 팔이 앞으로/뒤로 너무 나왔어요
                                            if abs(leftWristZ - spineBaseZ) > 0.2 or abs(rightWristZ - spineBaseZ) > 0.2:
                                                print("팔이 앞으로/뒤로 너무 나왔어요")
                                                fix = "Arm Pos"
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)

                                            # 허리를 좀 더 세워주세요
                                            if abs(headX-spineBaseX) > 0.2 or abs(headZ-spineBaseZ) > 0.2 :
                                                print("허리를 좀 더 세워주세요 ")
                                                fix = "Bar is not in line with feet"
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)

                self.draw_squatSummaryPage()

                # Draw graphics
                if self.startScreen == True:
                    self.draw_title()
                elif self.currPress != "Main":
                    if self.currPress == "SquatSummary":
                        self.draw_squatSummaryPage()
                    else:
                        self.draw_moveScr()

                h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
                target_height = int(h_to_w * self._screen.get_width())
                surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height))
                self._screen.blit(surface_to_draw, (0,0))
                surface_to_draw = None
                pygame.display.update()

            # Close our Kinect sensor, close the window and quit.
            self._kinect.close()
            pygame.quit()

    # game = GameRuntime()
    # game.run()

    print("\n ======================================")
    print("  운동에 해당하는 숫자를 입력해주세요. ")
    print(" --------------------------------------")
    print("  1. 스쿼트")
    print("  2. 런지")
    print("  3. 힙어브덕션")
    print(" --------------------------------------")
    print("  4. 렛풀다운")
    print("  5. 킥백")
    print("  6. 사이드레터럴레이즈")
    print(" --------------------------------------")
    print("  7. 사이드 밤")
    print("  8. 점핑잭")
    print("  9. 버피")
    print(" --------------------------------------")
    print("  10. 스트레칭")
    print(" ======================================")

    selectNum = int(input(">>  "))

    if selectNum == 1 :
        game = GameRuntime()
        game.run()
    elif selectNum == 2:
        print("런지를 실행했습니다.")
        game = GameRuntime_Lunge()
        game.run()
    elif selectNum == 3:
        print("힙 어브덕션을 실행합니다.")
        game = GameRuntime_Hip()
        game.run()
    elif selectNum == 4:
        print("렛풀다운을 실행합니다.")
        game = GameRuntime_latPullDown()
        game.run()
    elif selectNum == 5:
        print("킥백을 실행합니다.")
    elif selectNum == 6:
        print("사이드레터럴레이즈를 실행합니다.")
        game = GameRuntime_SLR()
        game.run()
    elif selectNum == 7:
        print("사이드 밤을 실행합니다.")
    elif selectNum == 8:
        print("점핑잭을 실행합니다.")
    elif selectNum == 9:
        print("버피를 실행합니다.")
    elif selectNum == 10:
        print("스트레칭을 실행합니다.")
    else :
        print("해당 운동은 없습니다.")

    return render_template('index.html')
    #return redirect("/")

if __name__ == '__main__':
    # server = Server(app.wsgi_app)
    # server.serve()
    app.run(debug=True)