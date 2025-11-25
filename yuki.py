#! /usr/bin/python
# -*- coding: utf-8 -*-

from robot import Robot
import math


class yuki(Robot):

    def init(self):
        # 特攻機らしい「黒・赤」のカラーリング
        self.setColor(0, 0, 0)  # 本体は黒
        self.setGunColor(255, 0, 0)  # 銃は赤
        self.setRadarColor(255, 0, 0)  # レーダーも赤
        self.setBulletsColor(255, 50, 50)

        # 敵を逃さないよう、通常のレーダーを使用
        self.setRadarField("round")
        self.radarVisible(True)

        # 常に敵の方向を向くため、レーダーと銃をロック
        self.lockRadar("gun")

        self.target_locked = False

    def run(self):
        # 敵が見つからないときは、高速回転して探す
        self.target_locked = False
        self.stop()
        self.turn(50)
        self.gunTurn(50)
        self.stop()

    def sensors(self):
        pass

    def onTargetSpotted(self, botId, botName, botPos):
        """
        敵を見つけたら、止まらずに突っ込み、至近距離で最大火力を叩き込む
        """
        self.target_locked = True

        my_pos = self.getPosition()
        dist = self.get_distance(my_pos, botPos)

        # 1. 敵の方向を計算
        angle_to_enemy = self.get_angle(my_pos, botPos)

        # 2. 全身（本体・銃・レーダー）を敵に向ける
        # 本体を向ける
        turn_angle = angle_to_enemy - self.getHeading()
        self.turn(self.normalize_angle(turn_angle))

        # 銃を向ける（ロックしているのでレーダーも向く）
        gun_turn_angle = angle_to_enemy - self.getGunHeading()
        self.gunTurn(self.normalize_angle(gun_turn_angle))

        # 3. 特攻移動ロジック
        self.stop()  # 前の動作をキャンセル

        # 敵の位置まで移動（+50して確実にぶつかるようにする）
        self.move(dist + 50)

        # 4. 道連れ射撃ロジック（ここが重要）
        if dist < 40:
            # ほぼ接触しているなら、最大火力(10)で発射
            # 自分のHPを10削るが、当たれば20回復し、相手に30与える
            self.fire(10)
            self.rPrint("DIE!!!")
        elif dist < 100:
            # 近距離なら高火力
            self.fire(5)
        elif dist < 300:
            # 中距離なら牽制（近づくためのHPを温存したいので弱め）
            self.fire(1)

        # 遠距離では撃たない（HP温存して突撃するため）

        self.stop()

    def onRobotHit(self, robotId, robotName):
        """ロボットにぶつかった時の処理"""
        # 通常は下がるが、このロボットは下がらない。
        # むしろ、さらに押し込んでゼロ距離射撃を狙う。
        self.rPrint("Gotcha!")
        self.fire(10)  # 衝突時は確実に当たるので最大火力

        # 少しだけ下がって勢いをつけてまた突っ込む（めり込み防止対策）
        self.stop()
        self.move(-20)
        self.stop()

    def onHitWall(self):
        """壁にぶつかったら、少し下がって向き直る"""
        self.stop()
        self.move(-50)
        self.turn(100)  # 大きく回って壁から脱出
        self.stop()

    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower):
        """撃たれてもひるまず、射手の方へ向き直って突撃する"""
        self.rPrint("Target Updated: " + str(bulletBotName))
        # 撃たれた＝敵はその方向にいる。sensorsやonTargetSpottedに任せるが
        # ここで特別な回避はせず、むしろチャンスと捉えて突っ込む精神
        pass

    # --- 必須メソッド ---
    def onRobotDeath(self):
        self.rPrint("I'll be back...")

    def onBulletHit(self, botId, bulletId):
        self.rPrint("Hit!")

    def onBulletMiss(self, bulletId):
        pass

    # --- 計算用関数 ---
    def get_distance(self, p1, p2):
        dx = p1.x() - p2.x()
        dy = p1.y() - p2.y()
        return math.sqrt(dx * dx + dy * dy)

    def get_angle(self, p1, p2):
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        rad = math.atan2(-dx, dy)
        return math.degrees(rad)

    def normalize_angle(self, angle):
        while angle <= -180: angle += 360
        while angle > 180: angle -= 360
        return angle

    def onHitByRobot(self, robotId, robotName):
        """相手の方からぶつかってきた時の処理（必須）"""
        self.rPrint("You dare hit me?!")
        # ぶつかられた＝相手は目の前にいるので、遠慮なく最大火力で撃つ
        self.fire(10)