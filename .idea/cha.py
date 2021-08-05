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

    goodCnt = []
    squatCnt = []
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

            self.currPress = "Main"

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
            self._frame_surface.blit(arnold, (0,0))

            text = pygame.font.Font("freesansbold.ttf",200)
            textSurf, textRect = text_objects("KinectLift", text, (255,255,255))
            textRect.center = (int(self.screen_width/2),int(self.screen_height/2))
            self._frame_surface.blit(textSurf,textRect)

            text1 = pygame.font.Font("freesansbold.ttf",100)
            textSurf1, textRect1 = text_objects("Start", text1, (255,255,255))
            textRect1.center = (int(self.screen_width/2),int(self.screen_height - self.screen_height/4))
            self._frame_surface.blit(textSurf1,textRect1)

            text1 = pygame.font.Font("freesansbold.ttf",80)
            textSurf1, textRect1 = text_objects("Saved Data", text1, (255,255,255))
            textRect1.center = (int(self.screen_width/2),int(self.screen_height - self.screen_height/8))
            self._frame_surface.blit(textSurf1,textRect1)

        def draw_squatSummaryPage(self):

            if self.squatSummaryList == []:
                text = pygame.font.Font("freesansbold.ttf",30)
                textSurf, textRect = text_objects("", text)
                textRect.center = (int(self.screen_width/2),int(self.screen_height)/3)
                self._frame_surface.blit(textSurf,textRect)

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

        def draw_MainScrbuttons(self):

            mouse = pygame.mouse.get_pos()
            pygame.draw.rect(self._frame_surface, (255,255,255), (int(self.screen_width/5),int(self.screen_height - self.screen_height/4),200,100))

            text = pygame.font.Font("freesansbold.ttf",50)

            for i in range(len(self.moveNames)):
                move = self.moveNames[i]
                textSurf2, textRect2 = text_objects(move, text)
                textRect2.center = (int(self.screen_width/5)*(i+1)+100,int(self.screen_height - self.screen_height/4)+50)
                self._frame_surface.blit(textSurf2,textRect2)

        def draw_movebuttons(self):
            text = pygame.font.Font("freesansbold.ttf",50)
            textSurf, textRect = text_objects(self.currPress, text)
            textRect.center = (int(self.screen_width/2),int(self.screen_height/6))
            self._frame_surface.blit(textSurf,textRect)

            text1 = pygame.font.Font("freesansbold.ttf",100)
            textSurf1, textRect1 = text_objects(str(len(squatCnt)), text1)
            textRect1.center = (int(self.screen_width/2),int(1.5* self.screen_height/6))
            self._frame_surface.blit(textSurf1,textRect1)

            pygame.draw.rect(self._frame_surface, (255,255,255), (int(self.screen_width/4.8),int(self.screen_height - self.screen_height/4),225,100))
            pygame.draw.rect(self._frame_surface, (255,255,255), (int(self.screen_width/4.8) *2,int(self.screen_height - self.screen_height/4),260,100))

            text = pygame.font.Font("freesansbold.ttf",50)
            list = ["Main", "Summary"]
            for i in range(len(list)):
                move = list[i]
                textSurf, textRect = text_objects(move, text)
                textRect.center = (int(self.screen_width/4.6)*(i+1)+100,int(self.screen_height - self.screen_height/4)+50)
                self._frame_surface.blit(textSurf,textRect)

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

                # We have a color frame. Fill out back buffer surface with frame's data
                if self._kinect.has_new_color_frame():
                    frame = self._kinect.get_last_color_frame()
                    self.draw_color_frame(frame, self._frame_surface)
                    frame = None


                # We have a body frame, so can get skeletons
                if self._kinect.has_new_body_frame():
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
                                leftShoulderX = joints[PyKinectV2.JointType_ShoulderLeft].Position.x
                                rightShoulderX = joints[PyKinectV2.JointType_ShoulderRight].Position.x
                                leftShoulderY = joints[PyKinectV2.JointType_ShoulderLeft].Position.y
                                rightShoulderY = joints[PyKinectV2.JointType_ShoulderRight].Position.y

                                leftElbowX = joints[PyKinectV2.JointType_ElbowLeft].Position.x
                                leftElbowY = joints[PyKinectV2.JointType_ElbowLeft].Position.y

                                leftankleX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                                leftankleY = joints[PyKinectV2.JointType_AnkleLeft].Position.y
                                rightankleX = joints[PyKinectV2.JointType_AnkleRight].Position.x
                                rightankleY = joints[PyKinectV2.JointType_AnkleRight].Position.y

                                spinMidX = joints[PyKinectV2.JointType_SpineMid].Position.x
                                spinMidY = joints[PyKinectV2.JointType_SpineMid].Position.y

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

                                        if (abs(self.feetList[0] - self.maxKneeX)) <= 0.6 and 70.0 < Left_Knee_angle < 115.0 and 70.0 < Left_Hip_angle:
                                            if squat_status == True:
                                                goodCnt.append(1)
                                            print("good cnt > ",len(goodCnt))

                                            if len(goodCnt) >= 10:
                                                goodCnt = []
                                                squatCnt.append(1)
                                                fix = "Good"
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)
                                                print("squat count ========================================>>>> ",len(squatCnt))
                                                f = open("static/cnt_saved.txt", 'w')
                                                f.write("count : " + str(len(squatCnt)))
                                                f.close()
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
                    # if self.currPress == "Help":
                    #     self.draw_helpPage()
                    # if self.currPress == "Saved":
                    #     self.draw_saved()
                    # elif self.currPress == "BenchSummary":
                    #     self.draw_summaryPage()
                    if self.currPress == "SquatSummary":
                        self.draw_squatSummaryPage()
                    elif self.moveDetected:
                        self.draw_movebuttons()
                    else:
                        self.draw_moveScr()

                # Optional debugging text
                #font = pygame.font.Font(None, 36)
                #text = font.render(str(self.flap), 1, (0, 0, 0))
                #self._frame_surface.blit(text, (100,100))

                # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
                # --- (screen size may be different from Kinect's color frame size)
                h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
                target_height = int(h_to_w * self._screen.get_width())
                surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height))
                self._screen.blit(surface_to_draw, (0,0))
                surface_to_draw = None
                pygame.display.update()

                #--- Limit to 60 frames per second
                # self._clock.tick(60)
                # def count_rt():
                #     return render_template('index.html',temp01=str(len(squatCnt)))

                # def send_cnt():
                #     temp01 = str(len(squatCnt))
                #     return render_template('index.html',temp01)

            # Close our Kinect sensor, close the window and quit.
            self._kinect.close()
            pygame.quit()

    game = GameRuntime()
    game.run()

    return render_template('index.html')
    #return redirect("/")

if __name__ == '__main__':
    # server = Server(app.wsgi_app)
    # server.serve()
    app.run(debug=True)