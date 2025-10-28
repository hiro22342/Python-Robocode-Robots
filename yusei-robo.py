import math
from robot import Robot
import random
import math
from math import cos, sin, radians

FIRE_DISTANCE = 500
BULLET_POWER = 5

MOVE_STEP = 10
MOVE_LIMIT = 50 

STATE_INIT = 0
STATE_RUNNING_C0 = 1
STATE_RUNNING_C1 = 2
STATE_RUNNING_C2 = 3
class yuseirobo(Robot):

    def init(self):  # To initialise your robot

        # Set the bot color in RGB
        self.setColor(0, 255, 0)
        self.setGunColor(0, 255, 0)
        self.setRadarColor(255, 0, 0)
        self.setBulletsColor(0, 255, 0)

        # get game informations
        self.MapX = self.getMapSize().width()
        self.MapY = self.getMapSize().height()

        # initialiase some variables
        #        self.move_step = MOVE_STEP
        self.state = STATE_INIT
        self.runcounter = 0     #used to record time based on game turns for our bot
        self.last_time = 0      #used to measure delays in "game turns"

        #these ugly variables keep track of corners of the gameplay we will travel to
        #repeatedly to never stay put. These are calculated based on other enemies position.
        self.C0X = -1  # will store destination C0 X we want to reach
        self.C0Y = -1  # will store destination C0 Y we want to reach
        self.C1X = -1  # will store destination C1 X we want to reach
        self.C1Y = -1  # will store destination C1 Y we want to reach
        self.C2X = -1  # will store destination C2 X we want to reach
        self.C2Y = -1  # will store destination C2 Y we want to reach

        self.radarVisible(True)     # if True the radar field is visible
        self.lockRadar("gun")       # might be "free","base" or "gun"
        self.setRadarField("round")  # might be "normal", "large, "thin", "round"    #変更部分(新規追加)
        self.radarGoingAngle = 5    # step angle for radar rotation　　#変更部分(コメントアウト)
        self.lookingForBot = 0      # botId we are looking for　　　　 #変更部分(コメントアウト)
        self.angleMinBot = 0        # botId of further bot when radar rotating ccw     #変更部分(コメントアウト)
        self.angleMaxBot = 0        # botId of further bot when radar rotating cw      #変更部分(コメントアウト)

        # self.enemies is a list of existing opponents and their last known location
        # onTargetSpotted() is used to update enemy list and their position
        # sensor() is used to delete missing opponents (dead)
        self.enemies = {}

    def MyMove(self, step: int):
        # MyMove takes care of not loosing health by not hitting walls.

        angle = self.getHeading()  # Returns the direction that the robot is facing
        position = self.getPosition()
        myX = position.x()
        myY = position.y()
        deltaY = step * cos(radians(angle))
        deltaX = - step * sin(radians(angle))

        move_ok = True

        if (deltaX > 0) and (myX + deltaX > self.MapX - MOVE_LIMIT):
            move_ok = False
        if (deltaX < 0) and (myX + deltaX < MOVE_LIMIT):
            move_ok = False
        if (deltaY > 0) and (myY + deltaY > self.MapY - MOVE_LIMIT):
            move_ok = False
        if (deltaY < 0) and (myY + deltaY < MOVE_LIMIT):
            move_ok = False

        if move_ok:
            self.move(step)
        else:
            # simulate wall hitting to launch appropriate actions
            self.rPrint("simulating wall hit, but stay calm, we stopped before !")
            self.onHitWall()
    def run(self):
        self.gunTurn(10)
            
    def onHitWall(self):
        # --- 新規追加: 壁衝突時の回避 ---
        self.setSpeed(-5)             # 後退する
        self.setTurn(random.uniform(90, 180)) # 大きく方向転換
        self.turn_timer = 50          # しばらく回避行動を継続
       

    def sensors(self): 
        pass
        
    def onRobotHit(self, robotId, robotName):
        pass
        
    def onHitByRobot(self, robotId, robotName):
        pass

    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower):
        pass
        
    def onBulletHit(self, botId, bulletId):
        pass
        
    def onBulletMiss(self, bulletId):
        pass
        
    def onRobotDeath(self):
        pass
        
    def onTargetSpotted(self, botId, botName, botPos):
        pos = self.getPosition()
        dx = botPos.x() - pos.x()
        dy = botPos.y() - pos.y()

        my_gun_angle = self.getGunHeading() % 360
        enemy_angle = math.degrees(math.atan2(dy, dx)) - 90
        a = enemy_angle - my_gun_angle
        if a < -180:
            a += 360
        elif 180 < a:
            a -= 360
        self.gunTurn(a)

        dist = math.sqrt(dx**2 + dy**2)
        if dist < FIRE_DISTANCE:
            self.fire(BULLET_POWER)