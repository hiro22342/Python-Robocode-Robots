#! /usr/bin/python
#-*- coding: utf-8 -*-

from robot import Robot #Import a base Robot

class MyRobot(Robot): #Create a Robot
    
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
        
        self.move(50) # for moving (negative values go back)
        #self.stop()
        self.gunTurn(45)    #銃を45度回転
        # self.stop() #停止


    def onHitWall(self):
        self.reset()     # プログラムをリセット
        self.pause(50)  # 50ミリ秒待機
        self.move(-100)  # 後ろに100ピクセル移動
        self.rPrint('ouch! a wall !') # メッセージ表示

    def sensors(self): #NECESARY FOR THE GAME
        pass
        
    def onRobotHit(self, robotId, robotName): # when My bot hit another
        self.rPrint('collision with:' + str(robotId))
        
    def onHitByRobot(self, robotId, robotName):
        self.rPrint("damn a bot collided me!")

    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower): #NECESARY FOR THE GAME
        """ When i'm hit by a bullet"""
        self.rPrint ("hit by " + str(bulletBotId) + "with power:" +str( bulletPower))
        
        # 打ちつつ、逃げる
        self.setRadarField("round") #レーダーを円形に設定
        self.fire(1) #威力1で発砲
        self.move(-50) # for moving (negative values go back) 
        
    def onBulletHit(self, botId, bulletId):#NECESARY FOR THE GAME
        """when my bullet hit a bot"""
        self.rPrint ("fire done on " +str( botId))
        
        # もっと攻める
        self.stop()
        self.fire(1) #威力1で発砲

        
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
        self.fire(1) #威力1で発砲

        self.setRadarField("normal") #レーダーを通常モードに戻す
