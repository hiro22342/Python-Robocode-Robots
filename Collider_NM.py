#! /usr/bin/python
#-*- coding: utf-8 -*-

# 設計思想：
# 基本的にフィールドの真ん中を維持しつつ、周りに的がいる場合にはぶつかりに行くロボット

from robot import Robot #Import a base Robot

MOVE_STEP = 5

STATE_MOVING_UNKNOWN_DIRECTION = 0
STATE_MOVING_UP    = 1
STATE_MOVING_RIGHT = 2
STATE_MOVING_DOWN  = 3
STATE_MOVING_LEFT  = 4

class Collider_NM(Robot): #Create a Robot
    
    def init(self):    #To initialyse your robot
        
        #RGBでロボットの色を設定
        self.setColor(187, 38, 73)        # 本体：濃い赤
        self.setGunColor(239, 105, 120)   # 銃：ピンク
        self.setRadarColor(255, 255, 255)  # レーダー：白
        self.setBulletsColor(255, 255, 255) # 弾：白

        self.radarVisible(True) # レーダーを表示
        
        self.lockRadar("gun") #レーダーを銃にロック
        
    def run(self): #main loop to command the bot
        pos = self.getPosition() #get my position
        size = self.getMapSize() #get the map size
        WALL_DISTANCE_WIDTH = size.width() / 5
        WALL_DISTANCE_HEIGHT = size.height() / 5
        angle = self.getHeading() % 360 #get my heading angle
        
        # マップの端から  の範囲内をぐるぐる回る

        if pos.x() < WALL_DISTANCE_WIDTH: #左の壁に近い場合
            self.stop()         
            self.turn(90 - angle)
            self.move(MOVE_STEP)
        elif pos.x() > size.width() - WALL_DISTANCE_WIDTH  : #右の壁に近い場合
            self.stop()         
            self.turn(270 - angle) #左に向く
            self.move(MOVE_STEP)
        elif pos.y() < WALL_DISTANCE_HEIGHT: #上の壁に近い場合
            self.stop()         
            self.turn(0 - angle)   #下に向く
            self.move(MOVE_STEP)
        elif pos.y() > size.height() - WALL_DISTANCE_HEIGHT: #下の壁に近い場合
            self.stop()         
            self.turn(180 - angle) #上に向く
            self.move(MOVE_STEP)

        self.move(MOVE_STEP) # for moving (negative values go back)
        self.stop()

    def onHitWall(self):
        self.stop()      # 停止
        self.reset()     # プログラムをリセット
        self.move(-30) 
        self.turn(90)

    def sensors(self): #NECESARY FOR THE GAME
        pass
        
    def onRobotHit(self, robotId, robotName): # when My bot hit another
        self.rPrint('collision with:' + str(robotId))
        
    def onHitByRobot(self, robotId, robotName):
        self.rPrint("damn a bot collided me!")
        self.move(-50)
        self.stop()
        self.setRadarField("large") #レーダーを円形に設定 

    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower): #NECESARY FOR THE GAME
        """ When i'm hit by a bullet"""
        self.rPrint ("hit by " + str(bulletBotId) + "with power:" +str( bulletPower))
        
        self.move(-50) # for moving (negative values go back) 
        self.setRadarField("large") #レーダーを円形に設定
        
    def onBulletHit(self, botId, bulletId):#NECESARY FOR THE GAME
        """when my bullet hit a bot"""
        self.rPrint ("fire done on " +str( botId))
        self.stop()        

    def onBulletMiss(self, bulletId):#NECESARY FOR THE GAME
        """when my bullet hit a wall"""
        self.rPrint ("the bullet "+ str(bulletId) + " fail")
        
        self.gunTurn(90) #銃を90度回転        
        self.setRadarField("normal") #レーダーを通常モードに戻す
        
    def onRobotDeath(self):#NECESARY FOR THE GAME
        """When my bot die"""
        self.rPrint ("damn I'm Dead")
        
    def onTargetSpotted(self, botId, botName, botPos):#NECESARY FOR THE GAME
        "when the bot see another one"
        self.rPrint("I see the bot:" + str(botId) + "on position: x:" + str(botPos.x()) + " , y:" + str(botPos.y()))        
        self.stop()
        self.move(30)
