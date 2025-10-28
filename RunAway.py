#! /usr/bin/python
#-*- coding: utf-8 -*-

from robot import Robot #Import a base Robot

MOVE_STEP = 5
WALL_DISTANCE = 50

STATE_MOVING_UNKNOWN_DIRECTION = 0
STATE_MOVING_UP    = 1
STATE_MOVING_RIGHT = 2
STATE_MOVING_DOWN  = 3
STATE_MOVING_LEFT  = 4

class RunAway(Robot): #Create a Robot
    
    def init(self):    #To initialyse your robot
        
        #RGBでロボットの色を設定
        self.setColor(0, 150, 255)        # 本体：サイバーブルー
        self.setGunColor(100, 200, 255)   # 銃：薄青
        self.setRadarColor(0, 100, 200)   # レーダー：濃青
        self.setBulletsColor(150, 220, 255) # 弾：アイスブルー

        self.radarVisible(True) # レーダーを表示

        #get the map size
        size = self.getMapSize()
        
        self.lockRadar("gun") #レーダーを銃にロック
        
    def run(self): #main loop to command the bot
        pos = self.getPosition() #get my position
        size = self.getMapSize() #get the map size
        angle = self.getHeading() % 360 #get my heading angle
        
        if pos.x() < WALL_DISTANCE: #左の壁に近い場合
            self.stop()         
            self.turn(90 - angle)
        elif pos.x() > size.width() - WALL_DISTANCE: #右の壁に近い場合
            self.stop()         
            self.turn(270 - angle) #左に向く
        elif pos.y() < WALL_DISTANCE: #上の壁に近い場合
            self.stop()         
            self.turn(0 - angle)   #下に向く
        elif pos.y() > size.height() - WALL_DISTANCE: #下の壁に近い場合
            self.stop()         
            self.turn(180 - angle) #上に向く
        
        self.move(MOVE_STEP) # for moving (negative values go back)
        self.stop()
        self.gunTurn(45)    #銃を45度回転
        self.radarTurn(90)  #レーダーを90度回転

    def onHitWall(self):
        self.stop()      # 停止
        self.reset()     # プログラムをリセット
        self.turn(75)  # 75度回転
        self.move(75)  # 75ピクセル移動

    def sensors(self): #NECESARY FOR THE GAME
        pass
        
    def onRobotHit(self, robotId, robotName): # when My bot hit another
        self.rPrint('collision with:' + str(robotId))
        
    def onHitByRobot(self, robotId, robotName):
        self.rPrint("damn a bot collided me!")
        self.turn(75)  # 75度回転
        self.move(75)  # 75ピクセル移動

    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower): #NECESARY FOR THE GAME
        """ When i'm hit by a bullet"""
        self.rPrint ("hit by " + str(bulletBotId) + "with power:" +str( bulletPower))
        
        # 打ちつつ、逃げる
        self.setRadarField("round") #レーダーを円形に設定
        self.move(-50) # for moving (negative values go back) 
        
    def onBulletHit(self, botId, bulletId):#NECESARY FOR THE GAME
        """when my bullet hit a bot"""
        self.rPrint ("fire done on " +str( botId))
        
        # もっと攻める
        self.stop()
        # self.fire(1) #威力1で発砲

    def onBulletMiss(self, bulletId):#NECESARY FOR THE GAME
        """when my bullet hit a wall"""
        self.rPrint ("the bullet "+ str(bulletId) + " fail")
        
        self.gunTurn(45) #銃を90度回転        
        self.setRadarField("large") #レーダーを通常モードに戻す
        
    def onRobotDeath(self):#NECESARY FOR THE GAME
        """When my bot die"""
        self.rPrint ("damn I'm Dead")
        
    def onTargetSpotted(self, botId, botName, botPos):#NECESARY FOR THE GAME
        "when the bot see another one"
        self.setRadarField("round") #レーダーを円形に設定
        # self.rPrint("I see the bot:" + str(botId) + "on position: x:" + str(botPos.x()) + " , y:" + str(botPos.y()))
        self.gunTurn(30) #銃を30度回転
        self.stop()
        self.setRadarField("normal") #レーダーを通常モードに戻す
