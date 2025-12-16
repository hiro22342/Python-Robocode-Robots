#! /usr/bin/python
# -*- coding: utf-8 -*-

from robot import Robot
import math


class WallShooter(Robot):

    def init(self):
        self.setColor(0, 0, 255)
        self.setGunColor(255, 0, 0)
        self.setRadarColor(0, 255, 0)
        self.setBulletsColor(255, 255, 0)

        self.radarVisible(True)
        self.setRadarField("thin")  # 細いレーダー

        self.wall_found = False

    def run(self):
        self.setRadarField("thin")

        # 移動しながらレーダーを回す
        self.move(100)
        self.radarTurn(360)
        self.stop()

    def onHitWall(self):
        self.reset()
        if self.wall_found == False:
            self.move(-10)
            self.turn(90)
            self.stop()
            self.wall_found = True
        else:
            self.move(-10)
            self.turn(180)
            self.stop()

    def onTargetSpotted(self, botId, botName, botPos):

        # 1. 敵への角度計算
        my_pos = self.getPosition()
        dx = botPos.x() - my_pos.x()
        dy = botPos.y() - my_pos.y()
        angle_rad = math.atan2(-dx, dy)
        target_angle = math.degrees(angle_rad)

        # 2. 銃を敵に向ける
        gun_heading = self.getGunHeading()
        gun_turn = target_angle - gun_heading
        while gun_turn > 180: gun_turn -= 360
        while gun_turn < -180: gun_turn += 360
        self.gunTurn(gun_turn)

        # 3. レーダーも敵に向ける
        radar_heading = self.getRadarHeading()
        radar_turn = target_angle - radar_heading
        while radar_turn > 180: radar_turn -= 360
        while radar_turn < -180: radar_turn += 360
        self.radarTurn(radar_turn)

        # 4. 【ここを変更】動きながら「3連射」する
        self.move(50)

        # マシンガンモード: 威力1の弾を3発予約
        # これでタタタンッ！と連射されます
        for i in range(3):
            self.fire(1)

            # --- 必須メソッド ---

    def sensors(self):
        pass

    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower):
        pass

    def onBulletMiss(self, bulletId):
        pass

    def onBulletHit(self, botId, bulletId):
        pass

    def onRobotHit(self, robotId, robotName):
        pass

    def onHitByRobot(self, robotId, robotName):
        pass

    def onRobotDeath(self):
        pass