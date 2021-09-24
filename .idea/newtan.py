#BodyGame from GitHub draws skeletons (https://github.com/Kinect/PyKinect2/blob/master/examples/PyKinectBodyGame.py)
# -*- coding:UTF-8 -*-

from flask import Flask, render_template
from numpy import arccos, double
from numpy.lib import r_, select, setdiff1d
from pykinect2 import PyKinectV2, PyKinectRuntime
import pykinect2
from pykinect2.PyKinectV2 import *
from flask import redirect, Response, url_for
from flask import request
from datetime import date

import ctypes
import _ctypes
import pygame
import math
import copy
import time
import datetime
import numpy as np
import sys
import io
import logging
import pymysql
import base64
import requests
import string
import random

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

app = Flask(__name__)

new_pw_len = 6
new_pw = ""
userEmail = ""
sec = 200

#mysql 연동
host = "database-1.cj61bbiht7nz.us-east-2.rds.amazonaws.com"
port = 3306
username = "tantan_db"
database = "tantanDB"
password = "tantan21!"

def connect_RDS(host,port,username,password,database):
    try:
        conn = pymysql.connect(host=host,user=username,passwd = password,db=database, port=port,use_unicode=True,charset ='utf8')
        curcor = conn.cursor()

    except:
        logging.error("RDS에 연결되지 않았습니다.")
        sys.exit(1)

    return conn,curcor

@app.route('/')
def index():
    variable = 000000
    return render_template('index.html', variable=variable)

@app.route('/connect')
def connect():
    conn, cursor = connect_RDS(host,port,username,password,database)

    print("랜덤 숫자", string.digits)

    global new_pw
    for i in range(new_pw_len):
        new_pw += random.choice(string.digits)

    print("\n생성된 랜덤 비밀번호", new_pw)

    query = """INSERT INTO tantanDB.connectTB (randomNum,userEmail) VALUES ('{0}','{1}');
            """.format(new_pw, '')

    cursor.execute(query)
    conn.commit()
    conn.close()

    return render_template('index.html', variable=new_pw)

@app.route('/my-link/<name>')
def my_link(name):

    #==================================
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

    left_handCnt = []
    right_handCnt = []

    leftlungeCnt = []
    rightlungeCnt = []

    goodCnt = []
    squatCnt = []
    sidebamCnt = []
    lpdCnt = []

    yogaCnt = []
    yogaside_status = True
    left_YStandCnt = []
    right_YStandCnt = []

    nextRoutine = False
    squat_status = True

    exCnt = ""

    # colors for drawing different bodies
    SKELETON_COLORS = [pygame.color.THECOLORS["red"],
                        pygame.color.THECOLORS["blue"],
                        pygame.color.THECOLORS["green"],
                        pygame.color.THECOLORS["orange"],
                        pygame.color.THECOLORS["purple"],
                        pygame.color.THECOLORS["yellow"],
                        pygame.color.THECOLORS["violet"]]

    #login=============================
    def login(variable):
        if variable != "":
            conn, cursor = connect_RDS(host,port,username,password,database)

            global userEmail
            # select_pw = ""
            # for i in variable(0,6) :
            #     select_pw = variable[i]

            sql = "SELECT userEmail FROM tantanDB.connectTB WHERE randomNum =" + variable # 실행할 SQL문

            cursor.execute(sql)
            result = cursor.fetchone()
            userEmail = result[0]

            print("\n유저 이메일", userEmail)
            print("\n생성된 랜덤 비밀번호", variable)

            conn.commit()
            conn.close()

    #add_run===========================
    def addrun(variable):
        if variable != "":
            conn, cursor = connect_RDS(host,port,username,password,database)

            global userEmail, runSub
            runTime_h, runTime_m =  time_calculate()

            sql = """INSERT INTO tantanDB.addRunTB (runDate, runTime_h, runMain, runSub, userEmail, runTime_m) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}');
            """.format(date.today().isoformat(), runTime_h, '스마트미러', runSub, userEmail, runTime_m)

            cursor.execute(sql)

            print("운동 데이터 입력 완료")

            conn.commit()
            conn.close()

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

    def feedbackFile(contents):
        with open("static/feedback.txt", "wt", encoding="UTF-8") as f:
            f.write(contents)
            f.close()

    def time_calculate():
        # print(f"{endtime - starttime:.0f} sec")
        sec = endtime - starttime
        times = str(datetime.timedelta(seconds=sec)).split(".")
        times = times[0]
        times = times.split(":")
        times_h = times[0]
        times_m = times[1]
        if times_m[0] == "0":
            times_m = times_m[1]
        print("운동 시 : ", times_h)
        print("운동 분 : ", times_m)
        print(date.today().isoformat())
        return times_h, times_m

    class GameRuntime_leg_routine(object):
        def __init__(self):
            pygame.init()

            global starttime
            starttime = time.time()
            print("하체운동 시작 시간 : ", starttime)

            global runSub
            runSub = "하체운동1"

            feedbackFile("")

            self.startScreen = False
            self.mainScreen = True
            self.time = time.strftime("%H:%M") + " " + time.strftime("%d/%m/%Y")

            self.moveNames = ["Squat","Lunge","Hip"]
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
            text = pygame.font.SysFont(None,200,True,False)
            textSurf, textRect = text_objects("KinectLift", text, (255,255,255))
            textRect.center = (int(self.screen_width/2),int(self.screen_height/2))
            self._frame_surface.blit(textSurf,textRect)

        def draw_squatSummaryPage(self):
            pygame.font.init()

            if self.squatSummaryList == []:
                text = pygame.font.SysFont(None,30,True,False)
                textSurf, textRect = text_objects("start", text)
                textRect.center = (int(self.screen_width/2),int(self.screen_height)/3)
                self._frame_surface.blit(textSurf,textRect)

            text = pygame.font.SysFont(None,30,True,False)
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
            text = pygame.font.SysFont(None,100,True,False)
            textSurf, textRect = text_objects(self.currPress, text)
            textRect.center = (int(self.screen_width/2),int(self.screen_height/6))
            self._frame_surface.blit(textSurf,textRect)

            text1 = pygame.font.SysFont(None,50,True,False)
            textSurf1, textRect1 = text_objects(str(len(squatCnt)), text1)
            textRect1.center = (int(self.screen_width/2),int(1.5* self.screen_height/6))
            self._frame_surface.blit(textSurf1,textRect1)

            if self.jointDetected == False:
                text2 = pygame.font.SysFont(None,50,True,False)
                textSurf2, textRect2 = text_objects("", text1)
                textRect2.center = (int(self.screen_width/2),int(2* self.screen_height/6))
                self._frame_surface.blit(textSurf2,textRect2)
            else:
                text2 = pygame.font.SysFont(None,50,True,False)
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

        def draw_display(self):
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            try:
                target_height = int(h_to_w * self._screen.get_width())
                surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height))
                self._screen.blit(surface_to_draw, (0,0))
                surface_to_draw = None
                pygame.display.update()
            except:
                pass

        def run_squat(self):
            self.currPress = "Squat"

            f = open("static/video_name.txt", 'w')
            f.write("squat")
            f.close()
            f = open("static/cnt_saved.txt", 'w')
            f.write("count : " + str(len(squatCnt)))
            f.close()
            feedbackFile("스쿼트 운동 시작하세요.")

            exCnt = ""
            goodCnt = []
            global endtime
            squat_status = True
            nextRoutine = False

            # -------- Main Program Loop -----------
            while not self._done:
                self.squatSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                        endtime = time.time()
                        print("스쿼트 끝 시간 : ", endtime)
                        login(new_pw)
                        addrun(userEmail)
                        print("스쿼트에서 데이터 입력")
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
                                headX = joints[PyKinectV2.JointType_Head].Position.x
                                headY = joints[PyKinectV2.JointType_Head].Position.y

                                rightWristY = joints[PyKinectV2.JointType_WristRight].Position.y
                                leftWristY  = joints[PyKinectV2.JointType_WristLeft].Position.y
                                rightWristX = joints[PyKinectV2.JointType_WristRight].Position.x
                                leftWristX  = joints[PyKinectV2.JointType_WristLeft].Position.x

                                leftHandX = joints[PyKinectV2.JointType_HandLeft].Position.x
                                leftHandY = joints[PyKinectV2.JointType_HandLeft].Position.y
                                rightHandX = joints[PyKinectV2.JointType_HandRight].Position.x
                                rightHandY = joints[PyKinectV2.JointType_HandRight].Position.y

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

                                # if you put your hands above your head, start hip abduction function.

                                if (abs(leftHandX-rightHandX)<=0.1) and (abs(leftHandY-rightHandY)<=0.1) and (abs(leftHandY-headY)<=0.25) and (abs(leftHandX-headX)<=0.1) and (nextRoutine == True) :
                                    print("start run_hip")
                                    txtCnt = "1st>> " + str(len(squatCnt)) + " / "
                                    exCnt += txtCnt
                                    self.run_hip()

                                if len(squatCnt) > 0 :
                                    nextRoutine = True

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

                                else:
                                    feedbackFile("운동이 인식되기 위해 손을 올려주세요.")

                                if len(self.wristXList) != 0 and len(self.wristYList) != 0 and len(self.kneeYList) != 0 and len(self.kneeXList) != 0 and len(self.feetList) != 0 and len(self.hipYList) != 0 and (abs(leftWristY -spineBaseY) >= 0.3):
                                    (self.minWristX, self.maxWristX) = min(self.wristXList), max(self.wristXList)
                                    (self.minWristY, self.maxWristY) = min(self.wristYList), max(self.wristYList)
                                    (self.minKneeX, self.maxKneeX) = min(self.kneeXList), max(self.kneeXList)
                                    (self.minKneeY, self.maxKneeY) = min(self.kneeYList), max(self.kneeYList)
                                    (self.minHipY, self.maxHipY) = min(self.hipYList), max(self.hipYList)

                                    if Left_Knee_angle >= 160 :
                                        print("start squat !!")
                                        feedbackFile("움직이세요.")

                                    else :

                                        if (abs(self.feetList[0] - self.maxKneeX)) <= 0.8 and 70.0 < Left_Knee_angle < 140.0 and 70.0 < Left_Hip_angle:
                                            if squat_status == True:
                                                goodCnt.append(1)
                                            print("good cnt > ",len(goodCnt))
                                            feedbackFile("좋아요!")
                                            # squat_status = False

                                            if len(goodCnt) >= 8:
                                                goodCnt = []
                                                squatCnt.append(1)
                                                fix = "Good"
                                                feedbackFile("좋아요!")
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
                                            feedbackFile("자세가 바르지 않습니다.")
                                            print("발끝 - 무릎 위치 : ", abs(self.feetList[0] - self.maxKneeX))
                                            print("왼 빵댕이 각도 {0}".format(Left_Hip_angle))
                                            print("왼쪽 무릎 각도 {0}".format(Left_Knee_angle))

                                            # 무릎을 더 굽혀주세요
                                            if Left_Knee_angle >= 115.0 :
                                                print("무릎을 더 굽혀주세요")
                                                fix = "Partial rep"
                                                feedbackFile("무릎을 더 굽혀주세요.")
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)

                                            # 무릎이 발끝을 너무 많이 넘었어요
                                            if (abs(self.feetList[0] - self.maxKneeX)) > 0.3 :
                                                print("무릎이 발끝을 너무 많이 넘었어요")
                                                fix = "Knee came too forward"
                                                feedbackFile("무릎이 발끝을 너무 많이 넘었어요.")
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)

                                            # 허리를 좀 더 세워주세요
                                            if Left_Hip_angle < 70.0 :
                                                print("허리를 좀 더 세워주세요 ")
                                                fix = "Bar is not in line with feet"
                                                feedbackFile("허리를 조금 더 세워주세요.")
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

                self.draw_display()

            # Close our Kinect sensor, close the window and quit.
            self._kinect.close()
            pygame.quit()

        def run_hip(self):
            self.currPress = "Hip"

            f = open("static/video_name.txt", 'w')
            f.write("hipLeft")
            f.close()

            nextRoutine = True
            hip_status = True
            goodCnt = []
            global exCnt
            global endtime

            squatCnt.clear()
            f = open("static/cnt_saved.txt", 'w')
            f.write("count : " + str(len(squatCnt)))
            f.close()
            feedbackFile("힙 운동 시작하세요.")

            # -------- Main Program Loop -----------
            while not self._done:
                self.squatSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                        endtime = time.time()
                        print("힙 끝 시간 : ", endtime)
                        login(new_pw)
                        addrun(userEmail)
                        print("힙에서 데이터 입력")
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

                            leftHandX = joints[PyKinectV2.JointType_HandLeft].Position.x
                            leftHandY = joints[PyKinectV2.JointType_HandLeft].Position.y
                            rightHandX = joints[PyKinectV2.JointType_HandRight].Position.x
                            rightHandY = joints[PyKinectV2.JointType_HandRight].Position.y

                            rightWristY = joints[PyKinectV2.JointType_WristRight].Position.y
                            leftWristY  = joints[PyKinectV2.JointType_WristLeft].Position.y
                            rightWristX = joints[PyKinectV2.JointType_WristRight].Position.x
                            leftWristX  = joints[PyKinectV2.JointType_WristLeft].Position.x

                            leftFootX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                            rightFootX = joints[PyKinectV2.JointType_AnkleRight].Position.x

                            spineBaseY = joints[PyKinectV2.JointType_SpineBase].Position.y
                            spineBaseX = joints[PyKinectV2.JointType_SpineBase].Position.x
                            spineBaseZ = joints[PyKinectV2.JointType_SpineBase].Position.z
                            spineMidY = joints[PyKinectV2.JointType_SpineMid].Position.y

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

                                if (abs(leftHandX-rightHandX)<=0.1) and (abs(leftHandY-rightHandY)<=0.1) and (abs(leftHandY-headY)<=0.25) and (abs(leftHandX-headX)<=0.1) and (nextRoutine == False):
                                    print("start run_lunge")
                                    txtCnt = "2nd>> " + str(len(squatCnt)) + " / "
                                    # exCnt += txtCnt
                                    self.run_lunge()

                                if (abs(leftWristY - spineMidY) <= 0.2):

                                    # print(abs(headX-spineBaseX))
                                    self.moveDetected = True

                                    if (len(left_HipCnt)>0) and (len(right_HipCnt)>0) :
                                        nextRoutine = False

                                    if(len(left_HipCnt) < 2) :
                                        if 85 <= Left_Hip_angle <= 95 :
                                            print("start left hip !!")
                                            feedbackFile("왼쪽 힙 운동하세요.")

                                        else :

                                            if (Left_Hip_angle >= 140) :
                                                if hip_status == True:
                                                    goodCnt.append(1)
                                                print("good cnt > ",len(goodCnt))
                                                print("왼쪽 성공 빵댕이 각도 {0}".format(Left_Hip_angle))
                                                feedbackFile("좋아요!")

                                                if len(goodCnt) >= 6:
                                                    goodCnt = []
                                                    left_HipCnt.append(1)
                                                    squatCnt.append(1)
                                                    fix = "Good"
                                                    feedbackFile("좋아요!")
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)
                                                    print("hip count ========================================>>>> ",len(left_HipCnt))
                                                    f = open("static/cnt_saved.txt", 'w')
                                                    f.write("count : " + str(len(squatCnt)))
                                                    f.close()
                                                    hip_status = False

                                            else:
                                                goodCnt = []
                                                hip_status = True
                                                print("Bad!")
                                                print("왼쪽 빵댕이 각도 {0}".format(Left_Hip_angle))
                                                feedbackFile("자세가 바르지 않아요.")

                                                # 허리를 좀 더 세워주세요 + 머리 뒤로 넘기지 마세요
                                                if abs(headX-spineBaseX) > 0.2 and abs(headZ-spineBaseZ) > 0.2 :
                                                    print("허리를 좀 더 세워주세요 ")
                                                    fix = "Bar is not in line with feet"
                                                    feedbackFile("허리를 조금 더 세워주세요.")
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 엉덩이를 더 높이 올리세요
                                                if Left_Hip_angle < 140 :
                                                    print("왼쪽 엉덩이를 더 높이 올리세요")
                                                    fix = "Knee came too forward"
                                                    feedbackFile("왼쪽 엉덩이를 더 높이 올리세요.")
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                    else :
                                        f = open("static/video_name.txt", 'w')
                                        f.write("hipRight")
                                        f.close()

                                        if 85 <= Right_Hip_angle <= 95 :
                                            print("start right hip !!")
                                            feedbackFile("오른쪽 힙 운동하세요.")

                                        else :

                                            if (Right_Hip_angle >= 140) :
                                                if hip_status == True:
                                                    goodCnt.append(1)
                                                print("good cnt > ",len(goodCnt))
                                                print("오른쪽 성공 빵댕이 각도 {0}".format(Right_Hip_angle))
                                                feedbackFile("좋아요!")
                                                # squat_status = False

                                                if len(goodCnt) >= 6:
                                                    goodCnt = []
                                                    right_HipCnt.append(1)
                                                    squatCnt.append(1)
                                                    fix = "Good"
                                                    feedbackFile("좋아요!")
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)
                                                    print("hip count ========================================>>>> ",len(right_HipCnt))
                                                    f = open("static/cnt_saved.txt", 'w')
                                                    f.write("count : " + str(len(squatCnt)))
                                                    f.close()
                                                    hip_status = False

                                            else:
                                                goodCnt = []
                                                hip_status = True
                                                print("Bad!")
                                                feedbackFile("자세가 바르지 않아요.")
                                                print("오른쪽 빵댕이 각도 {0}".format(Right_Hip_angle))

                                                # 허리를 좀 더 세워주세요
                                                if abs(headX-spineBaseX) > 0.2 and abs(headZ-spineBaseZ) > 0.2 :
                                                    print("허리를 좀 더 세워주세요 ")
                                                    fix = "Bar is not in line with feet"
                                                    feedbackFile("허리를 조금 더 세워주세요.")
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 엉덩이를 더 높이 올리세요
                                                if Right_Hip_angle < 140 :
                                                    print("오른쪽 엉덩이를 더 높이 올리세요")
                                                    fix = "Knee came too forward"
                                                    feedbackFile("오른쪽 엉덩이를 더 높이 올리세요.")
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                else:
                                    feedbackFile("운동이 인식되기 위해 손을 올려주세요.")

                self.draw_squatSummaryPage()

                # Draw graphics
                if self.startScreen == True:
                    self.draw_title()
                elif self.currPress != "Main":
                    if self.currPress == "SquatSummary":
                        self.draw_squatSummaryPage()
                    else:
                        self.draw_moveScr()

                self.draw_display()

            # # Close our Kinect sensor, close the window and quit.
            self._kinect.close()
            pygame.quit()

        def run_lunge(self):
            self.currPress = "Lunge"

            f = open("static/video_name.txt", 'w')
            f.write("lungeLeft")
            f.close()

            nextRoutine = False
            squat_status = True
            goodCnt = []
            global exCnt
            global endtime

            squatCnt.clear()
            f = open("static/cnt_saved.txt", 'w')
            f.write("count : " + str(len(squatCnt)))
            f.close()
            feedbackFile("런지 운동 시작하세요.")

            # -------- Main Program Loop -----------
            while not self._done:
                self.squatSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                        endtime = time.time()
                        print("런지 끝 시간 : ", endtime)
                        login(new_pw)
                        addrun(userEmail)
                        print("런지에서 데이터 입력")
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

                            leftHandX = joints[PyKinectV2.JointType_HandLeft].Position.x
                            leftHandY = joints[PyKinectV2.JointType_HandLeft].Position.y
                            rightHandX = joints[PyKinectV2.JointType_HandRight].Position.x
                            rightHandY = joints[PyKinectV2.JointType_HandRight].Position.y

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

                                # leg routine ending
                                if (abs(leftHandX-rightHandX)<=0.1) and (abs(leftHandY-rightHandY)<=0.1) and (abs(leftHandY-headY)<=0.25) and (abs(leftHandX-headX)<=0.1) and (nextRoutine == True):
                                    print("Last routine")
                                    txtCnt = "3rd>> " + str(len(squatCnt))
                                    #exCnt += txtCnt
                                    # sys.exit()

                                if len(leftlungeCnt) > 0 or len(rightlungeCnt) > 0 :
                                    nextRoutine = True

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

                                else:
                                    feedbackFile("운동이 인식되기 위해 손을 올려주세요.")

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
                                            feedbackFile("왼쪽 다리 런지 운동하세요.")

                                        else :
                                            if (abs(self.feetList[0] - self.maxKneeX)) <= 0.8 and 70.0 <= Left_Knee_angle <= 120.0 and abs(headX-spineBaseX) <= 0.2 and abs(headZ-spineBaseZ) <= 0.2:
                                                if squat_status == True:
                                                    goodCnt.append(1)
                                                print("good cnt > ",len(goodCnt))
                                                feedbackFile("좋아요!")
                                                # squat_status = False

                                                if len(goodCnt) >= 7:
                                                    goodCnt = []
                                                    leftlungeCnt.append(1)
                                                    squatCnt.append(1)
                                                    fix = "Good"
                                                    feedbackFile("좋아요!")
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)
                                                    print("left lunge count ========================================>>>> ",len(leftlungeCnt))
                                                    f = open("static/cnt_saved.txt", 'w')
                                                    f.write("count : " + str(len(squatCnt)))
                                                    f.close()
                                                    squat_status = False

                                            else:
                                                goodCnt = []
                                                squat_status = True
                                                print("Bad!")
                                                feedbackFile("자세가 바르지 않아요.")

                                                # 앞무릎을 더 굽혀주세요
                                                if 70.0 > Left_Knee_angle or Left_Knee_angle > 120.0 :
                                                    print("왼무릎을 더 굽혀주세요")
                                                    fix = "Partial rep"
                                                    feedbackFile("왼쪽 무릎을 더 굽혀주세요.")
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 뒷무릎을 더 굽혀주세요
                                                # if 80 > Right_Knee_angle or Right_Knee_angle > 160.0 :
                                                #     print("오른무릎을 더 굽혀주세요")
                                                #     fix = "Partial rep"
                                                #     feedbackFile("오른쪽 무릎을 더 굽혀주세요.")
                                                #     if fix not in self.squatSummaryList:
                                                #         self.squatSummaryList.append(fix)

                                                # 무릎이 발끝을 너무 많이 넘었어요
                                                if (abs(self.feetList[0] - self.maxKneeX)) > 0.8 :
                                                    print("무릎이 발끝을 너무 많이 넘었어요")
                                                    fix = "Knee came too forward"
                                                    feedbackFile("무릎이 발끝을 너무 많이 넘었어요.")
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 허리를 좀 더 세워주세요
                                                if abs(headX-spineBaseX) > 0.2 and abs(headZ-spineBaseZ) > 0.2 :
                                                    print("허리를 좀 더 세워주세요 ")
                                                    fix = "Bar is not in line with feet"
                                                    feedbackFile("허리를 조금 더 세워주세요.")
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                    # 오른쪽 다리 앞으로
                                    else :
                                        f = open("static/video_name.txt", 'w')
                                        f.write("lungeRight")
                                        f.close()

                                        if Right_Knee_angle >= 160 :
                                            print("start right lunge !!")
                                            feedbackFile("오른쪽 다리 런지 운동하세요.")

                                        else :
                                            if (abs(self.feetList[0] - self.maxKneeX)) <= 0.8 and 70.0 <= Right_Knee_angle <= 120.0 and abs(headX-spineBaseX) <= 0.2 and abs(headZ-spineBaseZ) <= 0.2:
                                                if squat_status == True:
                                                    goodCnt.append(1)
                                                print("good cnt > ",len(goodCnt))
                                                feedbackFile("좋아요!")
                                                # squat_status = False

                                                if len(goodCnt) >= 7:
                                                    goodCnt = []
                                                    rightlungeCnt.append(1)
                                                    squatCnt.append(1)
                                                    fix = "Good"
                                                    feedbackFile("좋아요!")
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)
                                                    print("right lunge count ========================================>>>> ",len(rightlungeCnt))
                                                    f = open("static/cnt_saved.txt", 'w')
                                                    f.write("count : " + str(len(squatCnt)))
                                                    f.close()
                                                    squat_status = False

                                            else:
                                                goodCnt = []
                                                squat_status = True
                                                print("Bad!")
                                                feedbackFile("자세가 바르지 않아요.")

                                                # 앞무릎을 더 굽혀주세요
                                                if 70.0 > Right_Knee_angle or Right_Knee_angle > 120.0 :
                                                    print("오른무릎을 더 굽혀주세요")
                                                    fix = "Partial rep"
                                                    feedbackFile("오른쪽 무릎을 더 굽혀주세요.")
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 뒷무릎을 더 굽혀주세요
                                                # if 80 > Left_Knee_angle or Left_Knee_angle > 160.0 :
                                                #     print("왼무릎을 더 굽혀주세요")
                                                #     fix = "Partial rep"
                                                #     feedbackFile("왼쪽 무릎을 더 굽혀주세요.")
                                                #     if fix not in self.squatSummaryList:
                                                #         self.squatSummaryList.append(fix)

                                                # 무릎이 발끝을 너무 많이 넘었어요
                                                if (abs(self.feetList[0] - self.maxKneeX)) > 0.8 :
                                                    print("무릎이 발끝을 너무 많이 넘었어요")
                                                    fix = "Knee came too forward"
                                                    feedbackFile("무릎이 발끝을 너무 많이 넘었어요.")
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 허리를 좀 더 세워주세요
                                                if abs(headX-spineBaseX) > 0.2 and abs(headY-spineBaseY) > 0.2 :
                                                    print("허리를 좀 더 세워주세요 ")
                                                    fix = "Bar is not in line with feet"
                                                    feedbackFile("허리를 조금 더 세워주세요.")
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

                self.draw_display()

            self._kinect.close()
            pygame.quit()



    class GameRuntime_upperBodyRoutine(object):
        def __init__(self):
            pygame.init()

            global starttime
            starttime = time.time()
            print("상체운동 시작 시간 : ", starttime)

            global runSub
            runSub = "상체운동1"

            feedbackFile("")

            self.startScreen = False
            self.mainScreen = True
            self.time = time.strftime("%H:%M") + " " + time.strftime("%d/%m/%Y")
            self.moveNames = ["LatPullDown","KickBack","SideLateralRaise"]

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
            text = pygame.font.SysFont(None,200,True,False)
            textSurf, textRect = text_objects("KinectLift", text, (255,255,255))
            textRect.center = (int(self.screen_width/2),int(self.screen_height/2))
            self._frame_surface.blit(textSurf,textRect)


        def draw_latPullDownSummaryPage(self):
            pygame.font.init()

            if self.latPullDownSummaryList == []:
                text = pygame.font.SysFont(None,30,True,False)
                textSurf, textRect = text_objects("", text)
                textRect.center = (int(self.screen_width/2),int(self.screen_height)/3)
                self._frame_surface.blit(textSurf,textRect)

            text = pygame.font.SysFont(None,30,True,False)
            textSurf1, textRect1 = text_objects("Click to return to main menu..", text)
            textRect1.center = (int(self.screen_width - self.screen_width/6.5),int(self.screen_height - self.screen_height/20))
            self._frame_surface.blit(textSurf1,textRect1)

            for i in range(len(self.latPullDownSummaryList)):
                move = self.latPullDownSummaryList[i]
                # lat pull down
                if move == "Hands should be in a straight line":
                    move = " Hands should be in a straight line"
                if move == "Armpits should be spaced apart":
                    move = "Armpits should be spaced apart"
                # kickback
                if move == "Your left elbows should be pushed back further.":
                    move = "Your left elbows should be pushed back further."
                if move == "Your right elbows should be pushed back further.":
                    move = "Your right elbows should be pushed back further."
                if move == "You need to extend your left elbows more.":
                    move = "You need to extend your left elbows more."
                if move == "You need to extend your right elbows more.":
                    move = "You need to extend your right elbows more."
                # side lateral raise
                if move == "Arm Pos" :
                    move = "Arm Pos"
                if move == "Right Arm Unfold" :
                    move = "Right Arm Unfold"
                if move == "Left Arm Unfold" :
                    move = "Left Arm Unfold"
                if move == "Right Arm Down" :
                    move = "Right Arm Down"
                if move == "Left Arm Down" :
                    move = "Left Arm Down"
                if move == "Right Arm Up" :
                    move = "Right Arm Up"
                if move == "Left Arm Up" :
                    move = "Left Arm Up"
                if move == "Bar is not in line with feet" :
                    move = "Bar is not in line with feet"

                if move == "Good":
                    move = "Good"
                textSurf1, textRect1 = text_objects(move, text)
                textRect1.center = (int(self.screen_width/2),100 +int(self.screen_height/5)+100*i)
                self._frame_surface.blit(textSurf1,textRect1)

        def draw_moveScr(self):
            text = pygame.font.SysFont(None,100,True,False)
            textSurf, textRect = text_objects(self.currPress, text)
            textRect.center = (int(self.screen_width/2),int(self.screen_height/6))
            self._frame_surface.blit(textSurf,textRect)

            text1 = pygame.font.SysFont(None,50,True,False)
            textSurf1, textRect1 = text_objects(str(len(lpdCnt)), text1)
            textRect1.center = (int(self.screen_width/2),int(1.5* self.screen_height/6))
            self._frame_surface.blit(textSurf1,textRect1)

            if self.jointDetected == False:
                text2 = pygame.font.SysFont(None,50,True,False)
                textSurf2, textRect2 = text_objects("", text1)
                textRect2.center = (int(self.screen_width/2),int(2* self.screen_height/6))
                self._frame_surface.blit(textSurf2,textRect2)
            else:
                text2 = pygame.font.SysFont(None,50,True,False)
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

        def draw_display(self):
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            try:
                target_height = int(h_to_w * self._screen.get_width())
                surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height))
                self._screen.blit(surface_to_draw, (0,0))
                surface_to_draw = None
                pygame.display.update()
            except:
                pass

        def run_lpd(self):
            f = open("static/video_name.txt", 'w')
            f.write("lpd")
            f.close()

            squat_status = True
            goodCnt = []

            exCnt = ""
            nextRoutine = False
            global endtime

            f = open("static/cnt_saved.txt", 'w')
            f.write("count : " + str(len(lpdCnt)))
            f.close()

            feedbackFile("렛풀다운 운동 시작하세요.")

            # -------- Main Program Loop -----------
            while not self._done:
                self.latPullDownSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                        endtime = time.time()
                        print("lpd 끝 시간 : ", endtime)
                        login(new_pw)
                        addrun(userEmail)
                        print("lpd에서 데이터 입력")
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

                                leftHandX = joints[PyKinectV2.JointType_HandLeft].Position.x
                                leftHandY = joints[PyKinectV2.JointType_HandLeft].Position.y
                                rightHandX = joints[PyKinectV2.JointType_HandRight].Position.x
                                rightHandY = joints[PyKinectV2.JointType_HandRight].Position.y

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

                                spineBaseY = joints[PyKinectV2.JointType_SpineBase].Position.y
                                spineBaseX = joints[PyKinectV2.JointType_SpineBase].Position.x
                                spineBaseZ = joints[PyKinectV2.JointType_SpineBase].Position.z

                                rightKneeX = joints[PyKinectV2.JointType_KneeRight].Position.x
                                leftKneeX = joints[PyKinectV2.JointType_KneeLeft].Position.x

                                leftFootX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                                rightFootX = joints[PyKinectV2.JointType_AnkleRight].Position.x

                                Left_Armpit_angle = get_angle_v3(spineShouldX, spineShouldY, leftShoulderX , leftShoulderY, leftElbowX, leftElbowY)

                                self.curX = (leftWristX, leftKneeX)
                                self.curY = (leftWristY, leftFootX)

                                if (abs(leftHandX-rightHandX)<=0.1) and (abs(leftHandY-rightHandY)<=0.1) and (abs(leftHandY-headY)<=0.25) and (abs(leftHandX-headX)<=0.1) and (nextRoutine == True) :
                                    print("start run_kickback")
                                    txtCnt = "1st>> " + str(len(lpdCnt)) + " / "
                                    exCnt += txtCnt
                                    self.run_kickBack()

                                if len(lpdCnt) > 0 :
                                    nextRoutine = True

                                # start point
                                # 왼쪽 손목과 오른쪽 손목이 spineBase Y보다 높을 경우 moveDetected를 True로 변경
                                if (abs(leftWristY -spineBaseY) >= 0.3) and (abs(rightWristY -spineBaseY) >= 0.3):
                                    self.moveDetected = True
                                else:
                                    self.moveDetected = False
                                    feedbackFile("운동이 인식되기 위해 손을 올려주세요.")


                                # 손목 배열이 잘 들어가고 & 손목 Y가 머리 Y보다 낮을 경우 운동 시작
                                # 손목 Y가 머리 Y보다 높아지는 경우 cnt 시작하기
                                if self.moveDetected == True :

                                    print("start latPullDown___________here !!")

                                    if (leftWristY < headY and rightWristY < headY) :
                                        print("start latPullDown !!")
                                        feedbackFile("렛풀다운 운동하세요.")

                                    else :
                                        print("겨드랑이 각도 >> ", Left_Armpit_angle)
                                        print("머리 높이 - 손목 높이 >> ", round(headY - rightWristY,2))

                                        if (abs(headY - rightWristY) <= 0.2) and (abs(headY - leftWristY) <= 0.2) and Left_Armpit_angle > 30.0 :
                                            if squat_status == True:
                                                goodCnt.append(1)
                                            print("good cnt > ",len(goodCnt))
                                            feedbackFile("좋아요!")
                                            # squat_status = False

                                            if len(goodCnt) >= 10:
                                                goodCnt = []
                                                lpdCnt.append(1)
                                                fix = "Good"
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)
                                                print("latPullDown count ========================================>>>> ",len(lpdCnt))
                                                f = open("static/cnt_saved.txt", 'w')
                                                f.write("count : " + str(len(lpdCnt)))
                                                f.close()
                                                feedbackFile("좋아요!")
                                                squat_status = False

                                        else:
                                            goodCnt = []
                                            squat_status = True
                                            print("Bad!")
                                            feedbackFile("자세가 바르지 않아요.")

                                            # 허리를 좀 더 세워주세요
                                            if abs(headX-spineBaseX) > 0.2 or abs(headZ-spineBaseZ) > 0.2 :
                                                print("허리를 좀 더 세워주세요 ")
                                                fix = "Bar is not in line with feet"
                                                feedbackFile("허리를 조금 더 세워주세요.")
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)

                                            # 겨드랑이 간격을 벌려야합니다.
                                            if Left_Armpit_angle <= 30.0 :
                                                print("겨드랑이 간격을 벌려야합니다.")
                                                fix = "Armpits should be spaced apart"
                                                feedbackFile("겨드랑이 간격을 벌려야합니다.")
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

                self.draw_display()

            # Close our Kinect sensor, close the window and quit.
            self._kinect.close()
            # pygame.quit()

        def run_kickBack(self):
            self.currPress = "KickBack"

            f = open("static/video_name.txt", 'w')
            f.write("kb")
            f.close()

            squat_status = True
            nextRoutine = True
            global exCnt
            global endtime

            lpdCnt.clear()
            goodCnt = []
            f = open("static/cnt_saved.txt", 'w')
            f.write("count : " + str(len(lpdCnt)))
            f.close()

            feedbackFile("킥백 운동 시작하세요.")

            # -------- Main Program Loop -----------
            while not self._done:
                self.latPullDownSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                        endtime = time.time()
                        print("kickback 끝 시간 : ", endtime)
                        login(new_pw)
                        addrun(userEmail)
                        print("kickback에서 데이터 입력")
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
                            if self.currPress == "KickBack":
                                headX = joints[PyKinectV2.JointType_Head].Position.x
                                headY = joints[PyKinectV2.JointType_Head].Position.y
                                headZ = joints[PyKinectV2.JointType_Head].Position.z

                                leftHandX = joints[PyKinectV2.JointType_HandLeft].Position.x
                                leftHandY = joints[PyKinectV2.JointType_HandLeft].Position.y
                                rightHandX = joints[PyKinectV2.JointType_HandRight].Position.x
                                rightHandY = joints[PyKinectV2.JointType_HandRight].Position.y

                                rightWristY = joints[PyKinectV2.JointType_WristRight].Position.y
                                leftWristY  = joints[PyKinectV2.JointType_WristLeft].Position.y
                                rightWristX = joints[PyKinectV2.JointType_WristRight].Position.x
                                leftWristX  = joints[PyKinectV2.JointType_WristLeft].Position.x

                                leftShoulderX = joints[PyKinectV2.JointType_ShoulderLeft].Position.x
                                rightShoulderX = joints[PyKinectV2.JointType_ShoulderRight].Position.x
                                leftShoulderY = joints[PyKinectV2.JointType_ShoulderLeft].Position.y
                                rightShoulderY = joints[PyKinectV2.JointType_ShoulderRight].Position.y

                                leftElbowX = joints[PyKinectV2.JointType_ElbowLeft].Position.x
                                leftElbowY = joints[PyKinectV2.JointType_ElbowLeft].Position.y
                                rightElbowX = joints[PyKinectV2.JointType_ElbowRight].Position.x
                                rightElbowY = joints[PyKinectV2.JointType_ElbowRight].Position.y

                                spinMidX = joints[PyKinectV2.JointType_SpineMid].Position.x

                                spineBaseX = joints[PyKinectV2.JointType_SpineBase].Position.x
                                spineBaseZ = joints[PyKinectV2.JointType_SpineBase].Position.z

                                rightKneeX = joints[PyKinectV2.JointType_KneeRight].Position.x
                                leftKneeX = joints[PyKinectV2.JointType_KneeLeft].Position.x

                                leftFootX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                                rightFootX = joints[PyKinectV2.JointType_AnkleRight].Position.x

                                Left_Elbow_angle = get_angle_v3(leftShoulderX , leftShoulderY, leftElbowX, leftElbowY, leftWristX, leftWristY)
                                Right_Elbow_angle = get_angle_v3(rightShoulderX , rightShoulderY, rightElbowX, rightElbowY, rightWristX, rightWristY)

                                self.curX = (leftWristX, leftKneeX)
                                self.curY = (leftWristY, leftFootX)

                                if (abs(leftHandX-rightHandX)<=0.1) and (abs(leftHandY-rightHandY)<=0.1) and (abs(leftHandY-headY)<=0.25) and (abs(leftHandX-headX)<=0.1) and (nextRoutine == False) :
                                    print("start run_slr")
                                    txtCnt = "2nd>> " + str(len(lpdCnt)) + " / "
                                    # exCnt += txtCnt
                                    self.run_slr()

                                if len(lpdCnt) > 0 :
                                    nextRoutine = False

                                # start point
                                # 양쪽 팔꿈치가 spinMid보다 뒤에 있는 경우 운동 시작
                                if (leftElbowX < spinMidX and rightElbowX > spinMidX):
                                    self.moveDetected = True
                                    if  abs(leftWristX - rightWristX) < 0.1:
                                        self.wristXList.append(self.curX[0])
                                    self.wristYList.append(self.curY[0])
                                else:
                                    feedbackFile("운동이 인식되기 위해 팔꿈치를 뒤로 밀어주세요.")

                                # 손목 배열이 잘 들어가고, moveetected가 true인 경우 시작
                                # Elbow각도가 180정도 펴져있으면 cnt
                                if len(self.wristXList) != 0 and len(self.wristYList) != 0 :
                                    (self.minWristX, self.maxWristX) = min(self.wristXList), max(self.wristXList)
                                    (self.minWristY, self.maxWristY) = min(self.wristYList), max(self.wristYList)

                                    if (leftElbowX < spinMidX and rightElbowX > spinMidX) :
                                        print("start KickBack !!")
                                        feedbackFile("킥백 운동하세요.")

                                    else :
                                        print("left elbow x >> ", round(leftElbowX,2))
                                        print("spinMid X >> ", round(spinMidX,2))
                                        print("왼쪽 팔꿈치 각도 >> ", round(Left_Elbow_angle,2))
                                        print("오른쪽 팔꿈치 각도 >> ", round(Right_Elbow_angle,2))

                                        if (Left_Elbow_angle > 150.0 and Right_Elbow_angle > 150.0):
                                            if squat_status == True:
                                                goodCnt.append(1)
                                            print("good cnt > ",len(goodCnt))
                                            feedbackFile("좋아요!")
                                            # squat_status = False

                                            if len(goodCnt) >= 10:
                                                goodCnt = []
                                                lpdCnt.append(1)
                                                fix = "Good"
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)
                                                print("KickBack count ========================================>>>> ",len(lpdCnt))
                                                f = open("static/cnt_saved.txt", 'w')
                                                f.write("count : " + str(len(lpdCnt)))
                                                f.close()
                                                feedbackFile("좋아요!")
                                                squat_status = False

                                        else:
                                            goodCnt = []
                                            squat_status = True
                                            print("Bad!")
                                            feedbackFile("자세가 바르지 않아요.")

                                            # 허리를 좀 더 세워주세요
                                            if abs(headX-spineBaseX) > 0.2 or abs(headZ-spineBaseZ) > 0.2 :
                                                print("허리를 좀 더 세워주세요 ")
                                                fix = "Bar is not in line with feet"
                                                feedbackFile("허리를 조금 더 세워주세요.")
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)

                                            # 팔꿈치를 더 펴야합니다.
                                            if Left_Elbow_angle <= 150.0 :
                                                print("왼쪽 팔꿈치를 더 펴야합니다.")
                                                fix = "You need to extend your left elbows more."
                                                feedbackFile("왼쪽 팔꿈치를 더 펴주세요.")
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)

                                            if Right_Elbow_angle <= 150.0 :
                                                print("오른쪽 팔꿈치를 더 펴야합니다.")
                                                fix = "You need to extend your right elbows more."
                                                feedbackFile("오른쪽 팔꿈치를 더 펴주세요.")
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

                self.draw_display()

            # Close our Kinect sensor, close the window and quit.
            self._kinect.close()
            # pygame.quit()

        def run_slr(self):
            self.currPress = "SideLateralRaise"

            f = open("static/video_name.txt", 'w')
            f.write("slr")
            f.close()

            global squat_status
            nextRoutine = False
            global exCnt
            global endtime

            lpdCnt.clear()
            goodCnt = []
            f = open("static/cnt_saved.txt", 'w')
            f.write("count : " + str(len(lpdCnt)))
            f.close()

            feedbackFile("사이드레터럴레이즈 운동 시작하세요.")

            # -------- Main Program Loop -----------
            while not self._done:
                self.latPullDownSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                        endtime = time.time()
                        print("slr 끝 시간 : ", endtime)
                        login(new_pw)
                        addrun(userEmail)
                        print("slr에서 데이터 입력")
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

                            leftHandX = joints[PyKinectV2.JointType_HandLeft].Position.x
                            leftHandY = joints[PyKinectV2.JointType_HandLeft].Position.y
                            rightHandX = joints[PyKinectV2.JointType_HandRight].Position.x
                            rightHandY = joints[PyKinectV2.JointType_HandRight].Position.y

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

                            leftsholderX = joints[PyKinectV2.JointType_ShoulderLeft].Position.x
                            leftsholderY = joints[PyKinectV2.JointType_ShoulderLeft].Position.y
                            rightsholderX = joints[PyKinectV2.JointType_ShoulderRight].Position.x
                            rightsholderY = joints[PyKinectV2.JointType_ShoulderRight].Position.y
                            leftelbowX= joints[PyKinectV2.JointType_ElbowLeft].Position.x
                            leftelbowY= joints[PyKinectV2.JointType_ElbowLeft].Position.y
                            rightelbowX= joints[PyKinectV2.JointType_ElbowRight].Position.x
                            rightelbowY= joints[PyKinectV2.JointType_ElbowRight].Position.y

                            # Side Lateral Raise
                            if self.currPress == "SideLateralRaise":

                                Left_inArm_angle = get_angle_v3(leftelbowX, leftelbowY, leftsholderX, leftsholderY, spineShouldX, spineShouldY)
                                Right_inArm_angle = get_angle_v3(rightelbowX, rightelbowY, rightsholderX, rightsholderY, spineShouldX, spineShouldY)
                                Left_outArm_angle = get_angle_v3(leftWristX, leftWristY, leftelbowX, leftelbowY, leftsholderX, leftsholderY)
                                Right_outArm_angle = get_angle_v3(rightWristX, rightWristY, rightelbowX, rightelbowY, rightsholderX, rightsholderY)

                                self.curX = (leftWristX, leftKneeX)
                                self.curY = (leftWristY, leftFootX)

                                if (abs(leftHandX-rightHandX)<=0.1) and (abs(leftHandY-rightHandY)<=0.1) and (abs(leftHandY-headY)<=0.25) and (abs(leftHandX-headX)<=0.1) and (nextRoutine == True) :
                                    print("Last routine")
                                    txtCnt = "3rd>> " + str(len(lpdCnt))
                                    # exCnt += txtCnt
                                    # sys.exit()

                                if len(lpdCnt) > 0 :
                                    nextRoutine = True

                                # if abs(leftelbowY - leftWristY) <= 0.16 :
                                if Left_inArm_angle > 140 or Right_inArm_angle > 140 :
                                    self.moveDetected = True

                                    # start point
                                    if Left_inArm_angle < 150 or Right_inArm_angle < 150 :
                                        print("start SideLateralRaise !!")
                                        feedbackFile("사이드레터럴레이즈 운동하세요.")

                                    else :

                                        if abs(leftWristZ - spineBaseZ) <= 0.2 and abs(rightWristZ - spineBaseZ) <= 0.2 and 155 <= Left_inArm_angle <= 180 and 155 <= Right_inArm_angle <= 180 \
                                        and 155 <= Left_outArm_angle <= 185 and 155 <= Right_outArm_angle <= 185 and abs(headX-spineBaseX) <= 0.2 and abs(headZ-spineBaseZ) <= 0.2:
                                            if squat_status == True:
                                                goodCnt.append(1)
                                            print("good cnt > ",len(goodCnt))
                                            feedbackFile("좋아요!")
                                            # squat_status = False

                                            if len(goodCnt) >= 7:
                                                goodCnt = []
                                                lpdCnt.append(1)
                                                fix = "Good"
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)
                                                print("slr count ========================================>>>> ",len(lpdCnt))
                                                f = open("static/cnt_saved.txt", 'w')
                                                f.write("count : " + str(len(lpdCnt)))
                                                f.close()
                                                feedbackFile("좋아요!")
                                                squat_status = False

                                            print("Good!")

                                        else:
                                            goodCnt = []
                                            squat_status = True
                                            print("Bad!")
                                            feedbackFile("자세가 바르지 않아요.")

                                            # 왼쪽 팔을 더 올려주세요
                                            if 155 > Left_inArm_angle :
                                                print("왼쪽 팔을 더 올려주세요")
                                                fix = "Left Arm Up"
                                                feedbackFile("왼쪽 팔을 더 올려주세요.")
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)

                                            # 왼쪽 팔을 조금 내려주세요
                                            if Left_inArm_angle > 180 :
                                                print("왼쪽 팔을 조금 내려주세요")
                                                fix = "Left Arm Down"
                                                feedbackFile("왼쪽 팔을 조금 내려주세요.")
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)

                                            # 오른쪽 팔을 더 올려주세요
                                            if 155 > Right_inArm_angle :
                                                print("오른쪽 팔을 더 올려주세요")
                                                fix = "Right Arm Up"
                                                feedbackFile("오른쪽 팔을 더 올려주세요.")
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)

                                            # 오른쪽 팔을 조금 내려주세요
                                            if Right_inArm_angle > 180 :
                                                print("오른쪽 팔을 조금 내려주세요")
                                                fix = "Right Arm Down"
                                                feedbackFile("오른쪽 팔을 조금 내려주세요.")
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)

                                            # 왼쪽 팔을 펴주세요
                                            if 155 > Left_outArm_angle :
                                                print("왼쪽 팔을 펴주세요")
                                                fix = "Left Arm Unfold"
                                                feedbackFile("왼쪽 팔을 펴주세요.")
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)

                                            # 오른쪽 팔을 펴주세요
                                            if 155 > Right_outArm_angle :
                                                print("오른쪽 팔을 펴주세요")
                                                fix = "Right Arm Unfold"
                                                feedbackFile("오른쪽 팔을 펴주세요.")
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)

                                            # 팔이 앞으로/뒤로 너무 나왔어요
                                            if abs(leftWristZ - spineBaseZ) > 0.2 or abs(rightWristZ - spineBaseZ) > 0.2:
                                                print("팔이 앞으로/뒤로 너무 나왔어요")
                                                fix = "Arm Pos"
                                                feedbackFile("팔이 앞으로/뒤로 너무 나왔어요.")
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)

                                            # 허리를 좀 더 세워주세요
                                            if abs(headX-spineBaseX) > 0.2 or abs(headZ-spineBaseZ) > 0.2 :
                                                print("허리를 좀 더 세워주세요 ")
                                                fix = "Bar is not in line with feet"
                                                feedbackFile("허리를 조금 더 세워주세요.")
                                                if fix not in self.latPullDownSummaryList:
                                                    self.latPullDownSummaryList.append(fix)

                                else:
                                    feedbackFile("운동이 인식되기 위해 팔을 올려주세요.")

                self.draw_latPullDownSummaryPage()

                # Draw graphics
                if self.startScreen == True:
                    self.draw_title()
                elif self.currPress != "Main":
                    if self.currPress == "SquatSummary":
                        self.draw_latPullDownSummaryPage()
                    else:
                        self.draw_moveScr()

                self.draw_display()

            # Close our Kinect sensor, close the window and quit.
            self._kinect.close()
            pygame.quit()

    class GameRuntime_WholeBodyRoutine(object):
        def __init__(self):
            pygame.init()

            global starttime
            starttime = time.time()
            print("전신운동 시작 시간 : ", starttime)

            global runSub
            runSub = "전신운동1"

            feedbackFile("")

            self.startScreen = False
            self.mainScreen = True
            self.time = time.strftime("%H:%M") + " " + time.strftime("%d/%m/%Y")
            self.moveNames = ["Side","KneeKick","WideSquat"]

            self.currPress = "Side"

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
            text = pygame.font.SysFont(None,200,True,False)
            textSurf, textRect = text_objects("KinectLift", text, (255,255,255))
            textRect.center = (int(self.screen_width/2),int(self.screen_height/2))
            self._frame_surface.blit(textSurf,textRect)

        def draw_squatSummaryPage(self):
            pygame.font.init()

            if self.squatSummaryList == []:
                text = pygame.font.SysFont(None,30,True,False)
                textSurf, textRect = text_objects("", text)
                textRect.center = (int(self.screen_width/2),int(self.screen_height)/3)
                self._frame_surface.blit(textSurf,textRect)

            text = pygame.font.SysFont(None,30,True,False)
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
            text = pygame.font.SysFont(None,100,True,False)
            textSurf, textRect = text_objects(self.currPress, text)
            textRect.center = (int(self.screen_width/2),int(self.screen_height/6))
            self._frame_surface.blit(textSurf,textRect)

            if self.currPress == "WideSquat" :
                text1 = pygame.font.SysFont(None,50,True,False)
                textSurf1, textRect1 = text_objects(str(len(squatCnt)), text1)
                textRect1.center = (int(self.screen_width/2),int(1.5* self.screen_height/6))
                self._frame_surface.blit(textSurf1,textRect1)

            else:
                # left count
                text1 = pygame.font.SysFont(None,50,True,False)
                textSurf1, textRect1 = text_objects("left >> " + str(len(left_handCnt)), text1)
                textRect1.center = (int(self.screen_width/2),int(1.5* self.screen_height/6))
                self._frame_surface.blit(textSurf1,textRect1)

                # right count
                text3 = pygame.font.SysFont(None,50,True,False)
                textSurf1, textRect1 = text_objects("right >> " + str(len(right_handCnt)), text1)
                textRect1.center = (int(self.screen_width/2),int(2.0* self.screen_height/6))
                self._frame_surface.blit(textSurf1,textRect1)

            if self.jointDetected == False:
                text2 = pygame.font.SysFont(None,50,True,False)
                textSurf2, textRect2 = text_objects("", text1)
                textRect2.center = (int(self.screen_width/2),int(2* self.screen_height/6))
                self._frame_surface.blit(textSurf2,textRect2)
            else:
                text2 = pygame.font.SysFont(None,50,True,False)
                textSurf2, textRect2 = text_objects(str(len(sidebamCnt)), text1)
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

        def draw_display(self):
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            try:
                target_height = int(h_to_w * self._screen.get_width())
                surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height))
                self._screen.blit(surface_to_draw, (0,0))
                surface_to_draw = None
                pygame.display.update()
            except:
                pass


        def run_side(self):
            right_handCnt.clear()
            left_handCnt.clear()
            nextRoutine = False
            global side_status
            global exCnt
            global endtime

            f = open("static/video_name.txt", 'w')
            f.write("hip")
            f.close()
            f = open("static/cnt_saved.txt", 'w')
            f.write("count : " + str(len(sidebamCnt)))
            f.close()

            feedbackFile("사이드밤 운동 시작하세요.")

            exCnt = ""
            # -------- Main Program Loop -----------
            while not self._done:
                self.squatSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                        endtime = time.time()
                        print("side 끝 시간 : ", endtime)
                        login(new_pw)
                        addrun(userEmail)
                        print("side에서 데이터 입력")
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

                            leftHandX = joints[PyKinectV2.JointType_HandLeft].Position.x
                            leftHandY = joints[PyKinectV2.JointType_HandLeft].Position.y
                            rightHandX = joints[PyKinectV2.JointType_HandRight].Position.x
                            rightHandY = joints[PyKinectV2.JointType_HandRight].Position.y

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

                            spineShouldX =joints[PyKinectV2.JointType_SpineShoulder].Position.x
                            spineShouldY =joints[PyKinectV2.JointType_SpineShoulder].Position.y
                            spineShouldZ =joints[PyKinectV2.JointType_SpineShoulder].Position.z

                            leftShoulderX = joints[PyKinectV2.JointType_ShoulderLeft].Position.x
                            rightShoulderX = joints[PyKinectV2.JointType_ShoulderRight].Position.x
                            leftShoulderY = joints[PyKinectV2.JointType_ShoulderLeft].Position.y
                            rightShoulderY = joints[PyKinectV2.JointType_ShoulderRight].Position.y

                            leftElbowX = joints[PyKinectV2.JointType_ElbowLeft].Position.x
                            leftElbowY = joints[PyKinectV2.JointType_ElbowLeft].Position.y
                            rightElbowX = joints[PyKinectV2.JointType_ElbowRight].Position.x
                            rightElbowY = joints[PyKinectV2.JointType_ElbowRight].Position.y

                            leftankleX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                            leftankleY = joints[PyKinectV2.JointType_AnkleLeft].Position.y
                            rightankleX = joints[PyKinectV2.JointType_AnkleRight].Position.x
                            rightankleY = joints[PyKinectV2.JointType_AnkleRight].Position.y

                             # save the hand positions
                            if self.currPress == "Side":

                                #왼팔, 오른팔 각도
                                Left_Arms_angle = get_angle_v3(leftShoulderX, leftShoulderY, leftElbowX, leftElbowY, leftWristX, leftWristY)
                                Right_Arms_angle = get_angle_v3(rightShoulderX, rightShoulderY, rightElbowX, rightElbowY, rightWristX, rightWristY)

                                #왼발, 오른발 각도
                                Left_Knee_angle = get_angle_v3(leftHipX, leftHipY, leftKneeX, leftKneeY, leftankleX, leftankleY)
                                Right_Knee_angle = get_angle_v3(rightHipX, rightHipY, rightKneeX, rightKneeY, rightankleX, rightankleY)

                                self.curX = (leftWristX, leftKneeX)
                                self.curY = (leftWristY, leftFootX)

                                if (abs(leftHandX-rightHandX)<=0.1) and (abs(leftHandY-rightHandY)<=0.1) and (abs(leftHandY-headY)<=0.25) and (abs(leftHandX-headX)<=0.1) and (nextRoutine == True) :
                                    print("start run_kneekick")
                                    txtCnt = "1st>> " + str(len(left_handCnt)) + ", " + str(len(right_handCnt)) + " / "
                                    exCnt += txtCnt
                                    self.run_kneekick()

                                if len(left_handCnt) > 0 :
                                    nextRoutine = True

                                # start point
                                # 왼쪽 손목과 오른쪽 손목이 spineShould Y보다 높을 경우 moveDetected를 True로 변경
                                if (leftWristY > spineShouldY and rightWristY > spineShouldY):
                                    self.moveDetected = True
                                    if  abs(leftWristX - rightWristX) < 0.1:
                                        self.wristXList.append(self.curX[0])
                                    self.wristYList.append(self.curY[0])

                                    if(len(left_handCnt) < 1) :
                                        if Left_Arms_angle > 110 and Right_Arms_angle > 110 and Left_Knee_angle > 160 and Right_Knee_angle > 160:
                                            print("start left side bam !!")
                                            feedbackFile("왼쪽 사이드밤 운동하세요.")

                                        else :

                                            #왼쪽 사이드 밤 성공조건
                                            if (Left_Arms_angle <= 105 and Right_Arms_angle <= 105 and Left_Knee_angle <= 100 and Right_Knee_angle >= 160 and leftKneeY > spineBaseY) :

                                                if side_status == True:
                                                    goodCnt.append(1)
                                                print("good cnt > ",len(goodCnt))
                                                feedbackFile("좋아요!")

                                                if len(goodCnt) >= 7:
                                                    goodCnt = []
                                                    left_handCnt.append(1)
                                                    sidebamCnt.append(1)
                                                    fix = "Good"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)
                                                    print("left side count ========================================>>>> ",len(left_handCnt))
                                                    f = open("static/cnt_saved.txt", 'w')
                                                    f.write("count : " + str(len(sidebamCnt)))
                                                    f.close()
                                                    feedbackFile("좋아요!")
                                                    side_status = False

                                            else:
                                                goodCnt = []
                                                side_status = True
                                                print("Bad!")
                                                print("왼쪽 실패 왼팔 각도 {0}".format(Left_Arms_angle))
                                                print("왼쪽 실패 오른무릎 각도 {0}".format(Left_Knee_angle))
                                                feedbackFile("자세가 바르지 않아요.")

                                                # 무릎을 더 높게 올려주세요
                                                if leftKneeY < spineBaseY:
                                                    print("무릎을 더 높게 올려주세요")
                                                    fix = "Knee came too forward"
                                                    feedbackFile("무릎을 더 높게 올려주세요.")
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                    else :
                                        if Left_Arms_angle > 110 and Right_Arms_angle > 110 and Left_Knee_angle > 160 and Right_Knee_angle > 160:
                                            print("start right side bam !!")
                                            feedbackFile("오른쪽 사이드밤 운동하세요.")

                                        else :
                                            #오른쪽 사이드 밤 성공조건
                                            if (Left_Arms_angle <= 105 and Right_Arms_angle <= 105 and Right_Knee_angle <= 100 and Left_Knee_angle >= 160 and rightKneeY > spineBaseY) :

                                                if side_status == True:
                                                    goodCnt.append(1)
                                                    feedbackFile("좋아요!")
                                                print("good cnt > ",len(goodCnt))

                                                if len(goodCnt) >= 7:
                                                    goodCnt = []
                                                    sidebamCnt.append(1)
                                                    right_handCnt.append(1)
                                                    fix = "Good"
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)
                                                    print("right side count ========================================>>>> ",len(right_handCnt))
                                                    f = open("static/cnt_saved.txt", 'w')
                                                    f.write("count : " + str(len(sidebamCnt)))
                                                    f.close()
                                                    feedbackFile("좋아요!")
                                                    side_status = False

                                            else:
                                                goodCnt = []
                                                side_status = True
                                                print("Bad!")
                                                print("오른쪽 실패 오른팔 각도 {0}".format(Right_Arms_angle))
                                                print("오른쪽 실패 왼무릎 각도 {0}".format(Left_Knee_angle))
                                                feedbackFile("자세가 바르지 않아요.")

                                                # 무릎을 더 높게 올려주세요
                                                if abs(rightKneeY) < abs(spineBaseY):
                                                    print("무릎을 더 높게 올려주세요")
                                                    fix = "Knee came too forward"
                                                    feedbackFile("무릎을 더 높게 올려주세요.")
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                else:
                                    feedbackFile("운동이 인식되기 위해 손을 올려주세요.")


                self.draw_squatSummaryPage()

                # Draw graphics
                if self.startScreen == True:
                    self.draw_title()
                elif self.currPress != "Main":
                    if self.currPress == "SquatSummary":
                        self.draw_squatSummaryPage()
                    else:
                        self.draw_moveScr()

                self.draw_display()

            # Close our Kinect sensor, close the window and quit.
            self._kinect.close()
            pygame.quit()

        def run_kneekick(self):
            self.currPress = "KneeKick"

            f = open("static/video_name.txt", 'w')
            f.write("kb")
            f.close()

            global goodCnt
            global exCnt
            global endtime
            nextRoutine = True
            right_handCnt.clear()
            left_handCnt.clear()

            sidebamCnt.clear()
            f = open("static/cnt_saved.txt", 'w')
            f.write("count : " + str(len(sidebamCnt)))
            f.close()

            feedbackFile("니킥 운동 시작하세요.")

            # -------- Main Program Loop -----------
            while not self._done:
                self.SquatSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                        endtime = time.time()
                        print("kneekick 끝 시간 : ", endtime)
                        login(new_pw)
                        addrun(userEmail)
                        print("kneekick에서 데이터 입력")
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
                            if self.currPress == "KneeKick":
                                headX = joints[PyKinectV2.JointType_Head].Position.x
                                headY = joints[PyKinectV2.JointType_Head].Position.y

                                rightWristY = joints[PyKinectV2.JointType_WristRight].Position.y
                                leftWristY  = joints[PyKinectV2.JointType_WristLeft].Position.y
                                rightWristX = joints[PyKinectV2.JointType_WristRight].Position.x
                                leftWristX  = joints[PyKinectV2.JointType_WristLeft].Position.x

                                leftHandX = joints[PyKinectV2.JointType_HandLeft].Position.x
                                leftHandY = joints[PyKinectV2.JointType_HandLeft].Position.y
                                rightHandX = joints[PyKinectV2.JointType_HandRight].Position.x
                                rightHandY = joints[PyKinectV2.JointType_HandRight].Position.y

                                leftFootX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                                rightFootX = joints[PyKinectV2.JointType_AnkleRight].Position.x

                                spineBaseY = joints[PyKinectV2.JointType_SpineBase].Position.y
                                spineBaseX = joints[PyKinectV2.JointType_SpineBase].Position.x

                                leftElbowX = joints[PyKinectV2.JointType_ElbowLeft].Position.x
                                leftElbowY = joints[PyKinectV2.JointType_ElbowLeft].Position.y
                                rightElbowX = joints[PyKinectV2.JointType_ElbowRight].Position.x
                                rightElbowY = joints[PyKinectV2.JointType_ElbowRight].Position.y

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

                                Left_Knee_angle = get_angle_v3(leftHipX, leftHipY, leftKneeX, leftKneeY, leftankleX, leftankleY)
                                right_knee_angle = get_angle_v3(rightHipX,rightHipY, rightKneeX,rightKneeY, rightankleX,rightankleY)

                                self.curX = (leftWristX, leftKneeX)
                                self.curY = (leftWristY, leftFootX)

                                if (abs(leftHandX-rightHandX)<=0.1) and (abs(leftHandY-rightHandY)<=0.1) and (abs(leftHandY-headY)<=0.25) and (abs(leftHandX-headX)<=0.1) and (nextRoutine == False) :
                                    print("start run_squat")
                                    txtCnt = "2nd>> " + str(len(left_handCnt)) + ", " + str(len(right_handCnt)) + " / "
                                    exCnt += txtCnt
                                    self.run_squat()

                                if len(left_handCnt) > 0 or len(right_handCnt) > 0:
                                    nextRoutine = False

                                if (abs(leftWristY -spineBaseY) >= 0.3):
                                    self.moveDetected = True
                                    print("start!!")
                                    self.kneeXList.append(self.curX[1])
                                    self.kneeYList.append(leftKneeY)
                                else:
                                    feedbackFile("운동이 인식되기 위해 손을 올려주세요.")

                                if len(self.kneeYList) != 0 and len(self.kneeXList) != 0 and (abs(leftWristY -spineBaseY) >= 0.3):
                                    (self.minKneeX, self.maxKneeX) = min(self.kneeXList), max(self.kneeXList)
                                    (self.minKneeY, self.maxKneeY) = min(self.kneeYList), max(self.kneeYList)


                                    if right_knee_angle >= 160 :
                                        print("오른쪽 무릎 각도")
                                        print("start right KneeKick !!")
                                        feedbackFile("오른쪽 니킥 운동하세요.")

                                    else :
                                        print("success 무릎 - 팔꿈치 : ", abs(rightKneeY - leftElbowY))
                                        if (abs(rightKneeY - leftElbowY)) <= 0.3 :
                                            if squat_status == True:
                                                goodCnt.append(1)
                                            print("good cnt > ",len(goodCnt))
                                            feedbackFile("좋아요!")

                                            if len(goodCnt) >= 5:
                                                goodCnt = []
                                                sidebamCnt.append(1)
                                                left_handCnt.append(1)
                                                fix = "Good"
                                                if fix not in self.SquatSummaryList:
                                                    self.SquatSummaryList.append(fix)
                                                print("KneeKick count ========================================>>>> ",len(left_handCnt))
                                                f = open("static/cnt_saved.txt", 'w')
                                                f.write("count : " + str(len(sidebamCnt)))
                                                f.close()
                                                feedbackFile("좋아요!")
                                                squat_status = False

                                        else:
                                            goodCnt = []
                                            squat_status = True
                                            print("Bad!")
                                            print("fail 무릎 - 팔꿈치 : ", abs(rightKneeY - leftElbowY))
                                            feedbackFile("자세가 바르지 않아요.")


                                if len(self.kneeYList) != 0 and len(self.kneeXList) != 0 and (abs(rightWristY -spineBaseY) >= 0.3):
                                    (self.minKneeX, self.maxKneeX) = min(self.kneeXList), max(self.kneeXList)
                                    (self.minKneeY, self.maxKneeY) = min(self.kneeYList), max(self.kneeYList)


                                    if Left_Knee_angle >= 160 :
                                        print("왼쪽 무릎 각도")
                                        print("start left KneeKick !!")
                                        feedbackFile("왼쪽 니킥 운동하세요.")

                                    else :
                                        print("success 무릎 - 팔꿈치 : ", abs(leftKneeY - rightElbowY))
                                        if (abs(leftKneeY - rightElbowY)) <= 0.3 :
                                            if squat_status == True:
                                                goodCnt.append(1)
                                            print("good cnt > ",len(goodCnt))
                                            feedbackFile("좋아요!")

                                            if len(goodCnt) >= 5:
                                                goodCnt = []
                                                sidebamCnt.append(1)
                                                right_handCnt.append(1)
                                                fix = "Good"
                                                if fix not in self.SquatSummaryList:
                                                    self.SquatSummaryList.append(fix)
                                                print("KneeKick count ========================================>>>> ",len(right_handCnt))
                                                f = open("static/cnt_saved.txt", 'w')
                                                f.write("count : " + str(len(sidebamCnt)))
                                                f.close()
                                                feedbackFile("좋아요!")
                                                squat_status = False

                                        else:
                                            goodCnt = []
                                            squat_status = True
                                            print("Bad!")
                                            print("fail 무릎 - 팔꿈치 : ", abs(leftKneeY - rightElbowY))
                                            feedbackFile("자세가 바르지 않아요.")


                self.draw_squatSummaryPage()

                # Draw graphics
                if self.startScreen == True:
                    self.draw_title()
                elif self.currPress != "Main":
                    if self.currPress == "SquatSummary":
                        self.draw_squatSummaryPage()
                    else:
                        self.draw_moveScr()

                self.draw_display()

            # Close our Kinect sensor, close the window and quit.
            self._kinect.close()
            pygame.quit()

        def run_squat(self):
            self.currPress = "WideSquat"

            f = open("static/video_name.txt", 'w')
            f.write("lpd")
            f.close()

            global exCnt
            global endtime
            squat_status = True
            nextRoutine = False

            goodCnt = []
            squatCnt = []
            sidebamCnt = []
            f = open("static/cnt_saved.txt", 'w')
            f.write("count : " + str(len(sidebamCnt)))
            f.close()

            feedbackFile("와이드스쿼트 운동 시작하세요.")

            # -------- Main Program Loop -----------
            while not self._done:
                self.squatSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                        endtime = time.time()
                        print("squat 끝 시간 : ", endtime)
                        login(new_pw)
                        addrun(userEmail)
                        print("squat에서 데이터 입력")
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
                            if self.currPress == "WideSquat":
                                headX = joints[PyKinectV2.JointType_Head].Position.x
                                headY = joints[PyKinectV2.JointType_Head].Position.y

                                leftHandX = joints[PyKinectV2.JointType_HandLeft].Position.x
                                leftHandY = joints[PyKinectV2.JointType_HandLeft].Position.y
                                rightHandX = joints[PyKinectV2.JointType_HandRight].Position.x
                                rightHandY = joints[PyKinectV2.JointType_HandRight].Position.y

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

                                if (abs(leftHandX-rightHandX)<=0.1) and (abs(leftHandY-rightHandY)<=0.1) and (abs(leftHandY-headY)<=0.25) and (abs(leftHandX-headX)<=0.1) and (nextRoutine == True):
                                    print("Last routine")
                                    txtCnt = "3rd>> " + str(len(squatCnt))
                                    exCnt += txtCnt
                                    sys.exit(exCnt)

                                if len(squatCnt) > 0 :
                                    nextRoutine = True

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
                                else:
                                    feedbackFile("운동이 인식되기 위해 손을 올려주세요.")

                                if len(self.wristXList) != 0 and len(self.wristYList) != 0 and len(self.kneeYList) != 0 and len(self.kneeXList) != 0 and len(self.feetList) != 0 and len(self.hipYList) != 0 and (abs(leftWristY -spineBaseY) >= 0.3):
                                    (self.minWristX, self.maxWristX) = min(self.wristXList), max(self.wristXList)
                                    (self.minWristY, self.maxWristY) = min(self.wristYList), max(self.wristYList)
                                    (self.minKneeX, self.maxKneeX) = min(self.kneeXList), max(self.kneeXList)
                                    (self.minKneeY, self.maxKneeY) = min(self.kneeYList), max(self.kneeYList)
                                    (self.minHipY, self.maxHipY) = min(self.hipYList), max(self.hipYList)

                                    if Left_Knee_angle >= 160 :
                                        print("start squat !!")
                                        feedbackFile("와이드스쿼트 운동하세요.")

                                    else :

                                        if (abs(self.feetList[0] - self.maxKneeX)) <= 0.8 and 70.0 < Left_Knee_angle < 140.0 and 70.0 < Left_Hip_angle:
                                            if squat_status == True:
                                                goodCnt.append(1)
                                                feedbackFile("좋아요!")

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
                                                feedbackFile("좋아요!")
                                                squat_status = False

                                        else:
                                            goodCnt = []
                                            squat_status = True
                                            print("Bad!")
                                            print("발끝 - 무릎 위치 : ", abs(self.feetList[0] - self.maxKneeX))
                                            print("왼 빵댕이 각도 {0}".format(Left_Hip_angle))
                                            print("왼쪽 무릎 각도 {0}".format(Left_Knee_angle))
                                            feedbackFile("자세가 바르지 않아요.")

                                            # 무릎을 더 굽혀주세요
                                            if Left_Knee_angle >= 115.0 :
                                                print("무릎을 더 굽혀주세요")
                                                fix = "Partial rep"
                                                feedbackFile("무릎을 더 굽혀주세요.")
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)

                                            # 무릎이 발끝을 너무 많이 넘었어요
                                            if (abs(self.feetList[0] - self.maxKneeX)) > 0.3 :
                                                print("무릎이 발끝을 너무 많이 넘었어요")
                                                fix = "Knee came too forward"
                                                feedbackFile("무릎이 발끝을 너무 많이 넘었어요.")
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)

                                            # 허리를 좀 더 세워주세요
                                            if Left_Hip_angle < 70.0 :
                                                print("허리를 좀 더 세워주세요 ")
                                                fix = "Bar is not in line with feet"
                                                feedbackFile("허리를 조금 더 세워주세요.")
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

                self.draw_display()

            # Close our Kinect sensor, close the window and quit.
            self._kinect.close()
            pygame.quit()

    class GameRuntime_yoga(object):
        def __init__(self):
            pygame.init()

            global starttime
            starttime = time.time()
            print("요가운동 시작 시간 : ", starttime)

            global runSub
            runSub = "요가운동1"

            feedbackFile("")
            self.startScreen = False
            self.mainScreen = True
            self.time = time.strftime("%H:%M") + " " + time.strftime("%d/%m/%Y")
            self.moveNames = ["Yoga_StandSide","yoga_Stand","yoga_Side"]

            self.currPress = "Yoga_StandSide"

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
            text = pygame.font.SysFont(None,200,True,False)
            textSurf, textRect = text_objects("KinectLift", text, (255,255,255))
            textRect.center = (int(self.screen_width/2),int(self.screen_height/2))
            self._frame_surface.blit(textSurf,textRect)

        def draw_squatSummaryPage(self):
            pygame.font.init()

            if self.squatSummaryList == []:
                text = pygame.font.SysFont(None,30,True,False)
                textSurf, textRect = text_objects("", text)
                textRect.center = (int(self.screen_width/2),int(self.screen_height)/3)
                self._frame_surface.blit(textSurf,textRect)

            text = pygame.font.SysFont(None,30,True,False)
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
            text = pygame.font.SysFont(None,100,True,False)
            textSurf, textRect = text_objects(self.currPress, text)
            textRect.center = (int(self.screen_width/2),int(self.screen_height/6))
            self._frame_surface.blit(textSurf,textRect)

            text1 = pygame.font.SysFont(None,50,True,False)
            textSurf1, textRect1 = text_objects(str(sec), text1)
            textRect1.center = (int(self.screen_width/2),int(1.5* self.screen_height/6))
            self._frame_surface.blit(textSurf1,textRect1)

            if self.jointDetected == False:
                text2 = pygame.font.SysFont(None,50,True,False)
                textSurf2, textRect2 = text_objects("", text1)
                textRect2.center = (int(self.screen_width/2),int(2* self.screen_height/6))
                self._frame_surface.blit(textSurf2,textRect2)
            else:
                text2 = pygame.font.SysFont(None,50,True,False)
                textSurf2, textRect2 = text_objects(str(sec), text1)
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

        def draw_display(self):
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            try:
                target_height = int(h_to_w * self._screen.get_width())
                surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height))
                self._screen.blit(surface_to_draw, (0,0))
                surface_to_draw = None
                pygame.display.update()
            except:
                pass

        #1
        def run_standside(self):
            left_YStandCnt = []
            right_YStandCnt = []

            global sec
            sec = 200

            global nextRoutine
            global endtime
            #exCnt = ""

            nextRoutine = True

            f = open("static/video_name.txt", 'w')
            f.write("standside")
            f.close()
            feedbackFile("운동을 시작합니다.")

            # -------- Main Program Loop -----------
            while not self._done:
                self.squatSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                        endtime = time.time()
                        print("standside 끝 시간 : ", endtime)
                        login(new_pw)
                        addrun(userEmail)
                        print("standside에서 데이터 입력")
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

                            leftHandX = joints[PyKinectV2.JointType_HandLeft].Position.x
                            leftHandY = joints[PyKinectV2.JointType_HandLeft].Position.y
                            rightHandX = joints[PyKinectV2.JointType_HandRight].Position.x
                            rightHandY = joints[PyKinectV2.JointType_HandRight].Position.y

                            rightWristY = joints[PyKinectV2.JointType_WristRight].Position.y
                            leftWristY  = joints[PyKinectV2.JointType_WristLeft].Position.y
                            rightWristX = joints[PyKinectV2.JointType_WristRight].Position.x
                            leftWristX  = joints[PyKinectV2.JointType_WristLeft].Position.x

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

                            leftElbowX = joints[PyKinectV2.JointType_ElbowLeft].Position.x
                            leftElbowY = joints[PyKinectV2.JointType_ElbowLeft].Position.y
                            rightElbowX = joints[PyKinectV2.JointType_ElbowRight].Position.x
                            rightElbowY = joints[PyKinectV2.JointType_ElbowRight].Position.y

                            leftankleX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                            leftankleY = joints[PyKinectV2.JointType_AnkleLeft].Position.y
                            rightankleX = joints[PyKinectV2.JointType_AnkleRight].Position.x
                            rightankleY = joints[PyKinectV2.JointType_AnkleRight].Position.y

                            # save the hand positions
                            if self.currPress == "Yoga_StandSide":

                                #왼발, 오른발 각도
                                Left_Knee_angle = get_angle_v3(leftHipX, leftHipY, leftKneeX, leftKneeY, leftankleX, leftankleY)
                                Right_Knee_angle = get_angle_v3(rightHipX, rightHipY, rightKneeX, rightKneeY, rightankleX, rightankleY)

                                self.curX = (leftWristX, leftKneeX)
                                self.curY = (leftWristY, leftFootX)

                                # next routine
                                if (abs(leftHandX-rightHandX)<=0.1) and (abs(leftHandY-rightHandY)<=0.1) and (abs(leftHandY-headY)<=0.25) and (abs(leftHandX-headX)<=0.1) and (nextRoutine == True):
                                    print("start yoga_stand")
                                    #txtCnt = "1st>> O / "
                                    #exCnt += txtCnt
                                    self.run_stand()

                                # start point
                                # 왼쪽 손목과 오른쪽 손목이 spineShould Y보다 높을 경우 moveDetected를 True로 변경
                                if (leftWristY >= spineShouldX and rightWristY >= spineShouldY):
                                    self.moveDetected = True
                                    if  abs(leftWristX - rightWristX) < 0.1:
                                        self.wristXList.append(self.curX[0])
                                    self.wristYList.append(self.curY[0])

                                    if(len(left_YStandCnt) < 1) :
                                        if Left_Knee_angle > 160 and Right_Knee_angle > 160:
                                            print("start left yoga stand side !!")
                                            feedbackFile("움직이세요")

                                        else :
                                            # start = time.time()
                                            #왼쪽 스탠드 사이드 성공조건

                                            #while은 반복문으로 sec가 0이 되면 반복을 멈춰라
                                            if (sec > 100):

                                                if (90 < Left_Knee_angle < 150 and Right_Knee_angle > 150):
                                                    print("good")
                                                    feedbackFile("good baby")
                                                    sec = sec-1

                                                else:
                                                    print("bad")
                                                    feedbackFile("자세가 바르지 않아요!")

                                                    # 무릎을 더 굽혀주세요
                                                    if Left_Knee_angle >= 150:
                                                        print("무릎을 더 굽혀주세요")
                                                        fix = "무릎을 더 굽혀주세요"
                                                        feedbackFile(fix)
                                                        if fix not in self.squatSummaryList:
                                                            self.squatSummaryList.append(fix)

                                                    # 허리를 일자로 세워주세요
                                                    if abs(headX - spineBaseX) > 0.1 and abs(headZ - spineBaseZ) > 0.1:
                                                        print("허리를 일자로 세워주세요")
                                                        fix = "허리를 일자로 세워주세요"
                                                        feedbackFile(fix)
                                                        if fix not in self.squatSummaryList:
                                                            self.squatSummaryList.append(fix)
                                    print(sec)
                                    if (sec == 100) :
                                        left_YStandCnt.append(1)
                                        feedbackFile("오른쪽 자세로 넘어가세요.")
                                        time.sleep(3)
                                        sec -= 1

                                    if(len(left_YStandCnt) >= 1) and (sec > 0):
                                        if Left_Knee_angle > 160 and Right_Knee_angle > 160:
                                            print("start right yoga stand side !!")
                                            feedbackFile("오른쪽 요가 스탠드 운동하세요.")

                                        else :
                                            #오른쪽 스탠드 사이드 성공조건
                                            if (90 < Right_Knee_angle < 150 and Left_Knee_angle > 150) :
                                                sec = sec-1
                                                feedbackFile("오른쪽 자세가 좋아요.")

                                            else:
                                                print("right Bad!")
                                                feedbackFile("오른쪽 자세가 바르지 않아요.")

                                                # 무릎을 더 굽혀주세요
                                                if Right_Knee_angle >= 150:
                                                    print("오른쪽 무릎을 더 굽혀주세요")
                                                    fix = "오른쪽 무릎을 더 굽혀주세요"
                                                    feedbackFile(fix)
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 허리를 일자로 세워주세요
                                                if abs(headX - spineBaseX) > 0.1 and abs(headZ - spineBaseZ) > 0.1:
                                                    print("허리를 일자로 세워주세요")
                                                    fix = "오른쪽 허리를 일자로 세워주세요"
                                                    feedbackFile(fix)
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)
                                    if (sec <= 0) :
                                        sec = 0
                                        feedbackFile("다음 자세로 넘어갑니다.")

                                else:
                                    feedbackFile("운동이 인식되기 위해 손을 올려주세요.")
                                    if 90 < Right_Knee_angle < 150 or 90 < Left_Knee_angle < 150:
                                        fix = "손 드세요"
                                        feedbackFile(fix)
                                    if (sec <= 0):
                                        feedbackFile("다음 자세로 넘어갑니다.")

                self.draw_squatSummaryPage()

                # Draw graphics
                if self.startScreen == True:
                    self.draw_title()
                elif self.currPress != "Main":
                    if self.currPress == "SquatSummary":
                        self.draw_squatSummaryPage()
                    else:
                        self.draw_moveScr()

                self.draw_display()

            # Close our Kinect sensor, close the window and quit.
            self._kinect.close()
            pygame.quit()

        #2
        def run_stand(self):
            self.currPress = "Yoga_Stand"

            global nextRoutine
            left_YStandCnt = []
            right_YStandCnt = []
            global exCnt
            global endtime

            global sec
            sec = 200
            left_YStandCnt.clear()
            right_YStandCnt.clear()

            f = open("static/video_name.txt", 'w')
            f.write("stand")
            f.close()
            feedbackFile("요가 스탠드 시작하세요.")


            # -------- Main Program Loop -----------
            while not self._done:
                self.squatSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                        endtime = time.time()
                        print("stand 끝 시간 : ", endtime)
                        login(new_pw)
                        addrun(userEmail)
                        print("stand에서 데이터 입력")
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

                            leftHandX = joints[PyKinectV2.JointType_HandLeft].Position.x
                            leftHandY = joints[PyKinectV2.JointType_HandLeft].Position.y
                            rightHandX = joints[PyKinectV2.JointType_HandRight].Position.x
                            rightHandY = joints[PyKinectV2.JointType_HandRight].Position.y

                            rightWristY = joints[PyKinectV2.JointType_WristRight].Position.y
                            leftWristY  = joints[PyKinectV2.JointType_WristLeft].Position.y
                            rightWristX = joints[PyKinectV2.JointType_WristRight].Position.x
                            leftWristX  = joints[PyKinectV2.JointType_WristLeft].Position.x

                            leftFootX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                            rightFootX = joints[PyKinectV2.JointType_AnkleRight].Position.x

                            spineBaseY = joints[PyKinectV2.JointType_SpineBase].Position.y
                            spineBaseX = joints[PyKinectV2.JointType_SpineBase].Position.x
                            spineBaseZ = joints[PyKinectV2.JointType_SpineBase].Position.z

                            spineMidY = joints[PyKinectV2.JointType_SpineMid].Position.y

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

                            leftElbowX = joints[PyKinectV2.JointType_ElbowLeft].Position.x
                            leftElbowY = joints[PyKinectV2.JointType_ElbowLeft].Position.y
                            rightElbowX = joints[PyKinectV2.JointType_ElbowRight].Position.x
                            rightElbowY = joints[PyKinectV2.JointType_ElbowRight].Position.y

                            leftankleX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                            leftankleY = joints[PyKinectV2.JointType_AnkleLeft].Position.y
                            rightankleX = joints[PyKinectV2.JointType_AnkleRight].Position.x
                            rightankleY = joints[PyKinectV2.JointType_AnkleRight].Position.y

                            # save the hand positions
                            if self.currPress == "Yoga_Stand":

                                #왼발, 오른발 각도
                                Left_Knee_angle = get_angle_v3(leftHipX, leftHipY, leftKneeX, leftKneeY, leftankleX, leftankleY)
                                Right_Knee_angle = get_angle_v3(rightHipX, rightHipY, rightKneeX, rightKneeY, rightankleX, rightankleY)


                                self.curX = (leftWristX, leftKneeX)
                                self.curY = (leftWristY, leftFootX)

                                # next routine
                                if (abs(leftHandX-rightHandX)<=0.1) and (abs(leftHandY-rightHandY)<=0.1) and (abs(leftHandY-headY)<=0.25) and (abs(leftHandX-headX)<=0.1) and (nextRoutine == False) :
                                    print("start run_side")
                                    # txtCnt = "2st>> O / "
                                    # exCnt += txtCnt
                                    self.run_side()

                                if sec < 199 :
                                    nextRoutine = False

                                # start point
                                # 왼쪽 손목과 오른쪽 손목이 어깨보다 아래에 있을 때 moveDetected = True
                                if (spineMidY <= leftWristY <= spineShouldY and spineMidY <= rightWristY <= spineShouldY):
                                    self.moveDetected = True
                                    if  abs(leftWristX - rightWristX) < 0.1:
                                        self.wristXList.append(self.curX[0])
                                    self.wristYList.append(self.curY[0])

                                    if(len(left_YStandCnt) < 1) :
                                        if Left_Knee_angle > 150 and Right_Knee_angle > 150:
                                            print("start left stand yoga !!")
                                            feedbackFile("왼쪽 스탠드 요가 운동하세요")

                                        else :
                                            # start = time.time()

                                            #while은 반복문으로 sec가 0이 되면 반복을 멈춰라
                                            if (sec > 100):

                                                #왼쪽 스탠드 성공조건
                                                if (Left_Knee_angle < 100 and Right_Knee_angle > 150 and rightKneeY <= leftankleY and leftWristY > spineBaseY and rightWristY > spineBaseY) :

                                                    print("good")
                                                    sec = sec-1
                                                    feedbackFile("왼쪽 자세가 좋아요")

                                                else:
                                                    print("bad")
                                                    feedbackFile("왼쪽 자세가 바르지 않아요!")

                                                    # 무릎을 더 굽혀주세요
                                                    if Left_Knee_angle >= 100:
                                                        print("왼쪽 무릎을 더 굽혀주세요.")
                                                        fix = "왼쪽 무릎을 더 굽혀주세요."
                                                        feedbackFile(fix)
                                                        if fix not in self.squatSummaryList:
                                                            self.squatSummaryList.append(fix)

                                                    # 허리를 일자로 세워주세요
                                                    if abs(headX - spineBaseX) > 0.1 and abs(headZ - spineBaseZ) > 0.1:
                                                        print("허리를 일자로 세워주세요.")
                                                        fix = "왼쪽 허리를 일자로 세워주세요."
                                                        feedbackFile(fix)
                                                        if fix not in self.squatSummaryList:
                                                            self.squatSummaryList.append(fix)

                                                    # 손을 명치쪽으로 올려주세요. (손을 가운데에 위치하게 하기위함)
                                                    # if leftWristY <= spineBaseY and rightWristY <= spineBaseY:
                                                    #     print("손을 명치쪽으로 올려주세요")
                                                    #     fix = "손을 명치쪽으로 올려주세요"
                                                    #     feedbackFile(fix)
                                                    #     if fix not in self.squatSummaryList:
                                                    #         self.squatSummaryList.append(fix)
                                    print(sec)
                                    if (sec == 100) :
                                        left_YStandCnt.append(1)
                                        feedbackFile("오른쪽 자세로 넘어갑니다.")
                                        time.sleep(3)
                                        sec -= 1

                                    if(len(left_YStandCnt) >= 1) and (sec > 0):
                                        if Left_Knee_angle > 170 and Right_Knee_angle > 170:
                                            print("start right yoga stand !!")
                                            feedbackFile("오른쪽 스탠드 요가 운동하세요.")

                                        else :
                                            #오른쪽 스탠드 성공조건
                                            if (Right_Knee_angle < 100 and Left_Knee_angle > 150 and leftKneeY <= rightankleY) :
                                                sec = sec-1
                                                feedbackFile("오른쪽 자세가 좋아요.")

                                            else:
                                                print("right Bad!")
                                                feedbackFile("오른쪽 자세가 바르지 않아요!")

                                                # 무릎을 더 굽혀주세요
                                                if Right_Knee_angle >= 100:
                                                    print("오른쪽 무릎을 더 굽혀주세요")
                                                    fix = "오른쪽 무릎을 더 굽혀주세요."
                                                    feedbackFile(fix)
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 허리를 일자로 세워주세요
                                                if abs(headX - spineBaseX) > 0.1 and abs(headZ - spineBaseZ) > 0.1:
                                                    print("허리를 일자로 세워주세요")
                                                    fix = "오른쪽 허리를 일자로 세워주세요."
                                                    feedbackFile(fix)
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 손을 명치쪽으로 올려주세요. (손을 가운데에 위치하게 하기위함)
                                                if leftWristY < spineMidY and rightWristY < spineMidY:
                                                    print("손을 명치쪽으로 올려주세요")
                                                fix = "손을 명치쪽으로 올려주세요"
                                                feedbackFile(fix)
                                                if fix not in self.squatSummaryList:
                                                    self.squatSummaryList.append(fix)

                                    if (sec < 0) :
                                        sec = 0
                                        right_YStandCnt.append(1)
                                        feedbackFile("다음 자세로 넘어갑니다.")
                                else:
                                    if (sec > 0) :
                                        feedbackFile("손을 가슴쪽으로 놔주세요.")
                                    else :
                                        feedbackFile("다음 자세로 넘어갑니다.")


                self.draw_squatSummaryPage()

                # Draw graphics
                if self.startScreen == True:
                    self.draw_title()
                elif self.currPress != "Main":
                    if self.currPress == "SquatSummary":
                        self.draw_squatSummaryPage()
                    else:
                        self.draw_moveScr()

                self.draw_display()

            # Close our Kinect sensor, close the window and quit.
            self._kinect.close()
            pygame.quit()

        #3
        def run_side(self):
            self.currPress = "Yoga_Side"

            global nextRoutine
            left_YStandCnt = []
            right_YStandCnt = []
            global exCnt
            global endtime

            global sec
            sec = 200
            left_YStandCnt.clear()
            right_YStandCnt.clear()

            f = open("static/video_name.txt", 'w')
            f.write("side")
            f.close()
            feedbackFile("요가 사이드 운동을 시작합니다.")

            # -------- Main Program Loop -----------
            while not self._done:
                self.squatSummaryList = []

                # --- Main event loop
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        self._done = True # Flag that we are done so we exit this loop
                        endtime = time.time()
                        print("side 끝 시간 : ", endtime)
                        login(new_pw)
                        addrun(userEmail)
                        print("side에서 데이터 입력")
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

                            leftHandX = joints[PyKinectV2.JointType_HandLeft].Position.x
                            leftHandY = joints[PyKinectV2.JointType_HandLeft].Position.y
                            rightHandX = joints[PyKinectV2.JointType_HandRight].Position.x
                            rightHandY = joints[PyKinectV2.JointType_HandRight].Position.y

                            rightWristY = joints[PyKinectV2.JointType_WristRight].Position.y
                            leftWristY  = joints[PyKinectV2.JointType_WristLeft].Position.y
                            rightWristX = joints[PyKinectV2.JointType_WristRight].Position.x
                            leftWristX  = joints[PyKinectV2.JointType_WristLeft].Position.x

                            leftFootX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                            rightFootX = joints[PyKinectV2.JointType_AnkleRight].Position.x

                            spineBaseY = joints[PyKinectV2.JointType_SpineBase].Position.y
                            spineBaseX = joints[PyKinectV2.JointType_SpineBase].Position.x
                            spineBaseZ = joints[PyKinectV2.JointType_SpineBase].Position.z

                            leftElbowX = joints[PyKinectV2.JointType_ElbowLeft].Position.x
                            leftElbowY = joints[PyKinectV2.JointType_ElbowLeft].Position.y
                            rightElbowX = joints[PyKinectV2.JointType_ElbowRight].Position.x
                            rightElbowY = joints[PyKinectV2.JointType_ElbowRight].Position.y

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
                            spineShouldZ =joints[PyKinectV2.JointType_SpineShoulder].Position.z

                            leftankleX = joints[PyKinectV2.JointType_AnkleLeft].Position.x
                            leftankleY = joints[PyKinectV2.JointType_AnkleLeft].Position.y
                            rightankleX = joints[PyKinectV2.JointType_AnkleRight].Position.x
                            rightankleY = joints[PyKinectV2.JointType_AnkleRight].Position.y

                            # save the hand positions
                            if self.currPress == "Yoga_Side":

                                #왼발, 오른발 각도
                                Left_Knee_angle = get_angle_v3(leftHipX, leftHipY, leftKneeX, leftKneeY, leftankleX, leftankleY)
                                Right_Knee_angle = get_angle_v3(rightHipX, rightHipY, rightKneeX, rightKneeY, rightankleX, rightankleY)


                                self.curX = (leftWristX, leftKneeX)
                                self.curY = (leftWristY, leftFootX)

                                # Last routine
                                if (abs(leftHandX-rightHandX)<=0.1) and (abs(leftHandY-rightHandY)<=0.1) and (abs(leftHandY-headY)<=0.25) and (abs(leftHandX-headX)<=0.1) and (nextRoutine == True):
                                    print("Last routine")
                                    # txtCnt = "3rd>> O"
                                    #exCnt += txtCnt
                                    #sys.exit(exCnt)

                                if sec < 199 :
                                    nextRoutine = True

                                # start point
                                # 오른쪽 무릎과 왼쪽 무릎 거리가 10cm 이상 일때 moveDetected = True
                                if (rightKneeX - leftKneeX > 0.1 ):
                                    self.moveDetected = True

                                    if(len(left_YStandCnt) < 1) :
                                        if (Left_Knee_angle > 160 and Right_Knee_angle > 160 and leftHandY < spineBaseY and rightHandY < spineBaseY):
                                            print("start yoga ]eft side!!")
                                            feedbackFile("왼쪽 요가 사이드 운동하세요")

                                        else :
                                            #while은 반복문으로 sec가 0이 되면 반복을 멈춰라

                                            if (sec > 100):

                                                if (Left_Knee_angle >= 160 and Right_Knee_angle >= 160 and leftWristY <= spineBaseY and rightWristY >= headY and spineBaseX - headX > 0.05):
                                                    sec = sec - 1
                                                    print("good")
                                                    feedbackFile("왼쪽 자세가 좋아요.")

                                                else:
                                                    print("bad")
                                                    feedbackFile("왼쪽 자세가 바르지 않아요!")

                                                    # 무릎을 더 펴주세요
                                                    if Left_Knee_angle < 160 and Right_Knee_angle < 160:
                                                        print("왼쪽 무릎을 더 펴주세요.")
                                                        fix = "왼쪽 무릎을 더 펴주세요."
                                                        feedbackFile(fix)
                                                        if fix not in self.squatSummaryList:
                                                            self.squatSummaryList.append(fix)

                                                    # 허리를 더 숙여주세요
                                                    if abs(abs(headX) - spineBaseX) < 0.1:
                                                        print("왼쪽 허리를 더 숙여주세요.")
                                                        fix = "왼쪽 허리를 더 숙여주세요."
                                                        feedbackFile(fix)
                                                        if fix not in self.squatSummaryList:
                                                            self.squatSummaryList.append(fix)
                                    print(sec)
                                    if (sec == 100) :
                                        left_YStandCnt.append(1)
                                        feedbackFile("오른쪽 자세로 넘어갑니다.")
                                        time.sleep(3)
                                        sec -= 1

                                    if(len(left_YStandCnt) >= 1) and (sec > 0) :
                                        if Left_Knee_angle > 170 and Right_Knee_angle > 170:
                                            print("start yoga right side !!")
                                            feedbackFile("오른쪽 요가 사이드 운동하세요.")

                                        else :
                                            #오른쪽 사이드 밤 성공조건
                                            if (Left_Knee_angle >= 160 and Right_Knee_angle >= 160 and rightWristY <= spineBaseY and leftWristY >= headY and headX - spineBaseX > 0.05) :
                                                sec = sec-1
                                                print("right good!")
                                                feedbackFile("오른쪽 자세가 좋아요.")

                                            else:
                                                print("right Bad!")
                                                feedbackFile("오른쪽 자세가 바르지 않아요!")

                                                # 무릎을 더 굽혀주세요
                                                if Left_Knee_angle < 160 and Right_Knee_angle < 160:
                                                    print("오른쪽 무릎을 더 굽혀주세요.")
                                                    fix = "오른쪽 무릎을 더 굽혀주세요."
                                                    feedbackFile(fix)
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)

                                                # 허리를 더 숙여주세요
                                                if abs(abs(headX) - spineBaseX) < 0.1:
                                                    print("오른쪽 허리를 더 숙여주세요.")
                                                    fix = "오른쪽 허리를 더 숙여주세요."
                                                    feedbackFile(fix)
                                                    if fix not in self.squatSummaryList:
                                                        self.squatSummaryList.append(fix)
                                    if (sec <= 0) :
                                        sec = 0
                                        right_YStandCnt.append(1)
                                        feedbackFile("요가 운동을 마칩니다.")
                                else:
                                    if (sec > 0) :
                                        feedbackFile("운동 인식안됩니다.")
                                    else :
                                        feedbackFile("요가 운동을 마칩니다.")

                self.draw_squatSummaryPage()

                # Draw graphics
                if self.startScreen == True:
                    self.draw_title()
                elif self.currPress != "Main":
                    if self.currPress == "SquatSummary":
                        self.draw_squatSummaryPage()
                    else:
                        self.draw_moveScr()

                self.draw_display()

            # Close our Kinect sensor, close the window and quit.
            self._kinect.close()
            pygame.quit()

    print("\n ======================================")
    print("  운동에 해당하는 숫자를 입력해주세요. ")
    print(" --------------------------------------")
    print("  1. 하체루틴 실행")
    print("  ▶ 스쿼트 > 힙 어브덕션 > 런지")
    print(" --------------------------------------")
    print("  2. 상체루틴 실행")
    print("  ▶ 렛풀다운 > 킥백 > 사이드레터럴레이즈")
    print(" --------------------------------------")
    print("  3. 전신루틴 실행")
    print("  ▶ 사이드 밤 > 니 킥 > 와이드 스쿼트")
    print(" --------------------------------------")
    print("  4. 요가루틴 실행")
    print("  ▶ stand side > stand > side")
    print(" ======================================")

    # selectNum = int(input(">>  "))

    if name == "하체" :
        print("하체루틴을 실행합니다.")
        game = GameRuntime_leg_routine()
        game.run_squat()
    elif name == "상체" :
        print("상체루틴을 실행합니다.")
        game = GameRuntime_upperBodyRoutine()
        game.run_lpd()
    elif name == "전신":
        print("전신루틴을 실행합니다.")
        game = GameRuntime_WholeBodyRoutine()
        game.run_side()
    elif name == "요가":
        print("요가루틴을 실행합니다.")
        game = GameRuntime_yoga()
        game.run_standside()

    return redirect("/")

if __name__ == '__main__':
    # server = Server(app.wsgi_app)
    # server.serve()
    app.run(debug=True)