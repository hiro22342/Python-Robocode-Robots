# -*- coding: utf-8 -*-
import math
from math import cos, sin, radians, sqrt, degrees, atan2
from robot import Robot

# WallRunner parameters
MOVE_STEP_WALL = 5
WALL_DISTANCE = 50
BULLET_POWER = 2

STATE_MOVING_UNKNOWN_DIRECTION = 0
STATE_MOVING_UP    = 1
STATE_MOVING_RIGHT = 2
STATE_MOVING_DOWN  = 3
STATE_MOVING_LEFT  = 4

# T800 parameters
MOVE_STEP = 10
MOVE_LIMIT = 50

STATE_INIT = 0
STATE_RUNNING_C0 = 1
STATE_RUNNING_C1 = 2
STATE_RUNNING_C2 = 3


class WallT800(Robot):

    def init(self):
        self.setColor(100, 255, 100)
        self.setGunColor(150, 255, 150)
        self.setRadarColor(255, 100, 0)
        self.setBulletsColor(255, 255, 200)
        self.radarVisible(True)
        self.lockRadar("gun")
        self.setRadarField("thin")

        self.MapX = self.getMapSize().width()
        self.MapY = self.getMapSize().height()
        self.runcounter = 0
        self.last_time = 0
        self.enemies = {}

        # WallRunner State
        self.wall_state = STATE_MOVING_UNKNOWN_DIRECTION
        # T-800 State
        self.state = STATE_INIT
        self.C0X = self.C0Y = self.C1X = self.C1Y = self.C2X = self.C2Y = -1
        self.radarGoingAngle = 5
        self.lookingForBot = 0
        self.angleMinBot = 0
        self.angleMaxBot = 0

    # WallRunner Mode
    def wallRun(self):
        pos = self.getPosition()
        angle = self.getHeading() % 360

        if self.wall_state == STATE_MOVING_UNKNOWN_DIRECTION:
            self.turn(-angle)
            self.gunTurn(-angle)
            self.wall_state = STATE_MOVING_DOWN

        elif self.wall_state == STATE_MOVING_UP:
            if pos.y() < WALL_DISTANCE:
                self.stop(); self.turn(90); self.gunTurn(90)
                self.wall_state = STATE_MOVING_RIGHT
            else:
                self.move(MOVE_STEP_WALL)

        elif self.wall_state == STATE_MOVING_DOWN:
            if self.MapY - WALL_DISTANCE < pos.y():
                self.stop(); self.turn(90); self.gunTurn(90)
                self.wall_state = STATE_MOVING_LEFT
            else:
                self.move(MOVE_STEP_WALL)

        elif self.wall_state == STATE_MOVING_LEFT:
            if pos.x() < WALL_DISTANCE:
                self.stop(); self.turn(90); self.gunTurn(90)
                self.wall_state = STATE_MOVING_UP
            else:
                self.move(MOVE_STEP_WALL)

        elif self.wall_state == STATE_MOVING_RIGHT:
            if self.MapX - WALL_DISTANCE < pos.x():
                self.stop(); self.turn(90); self.gunTurn(90)
                self.wall_state = STATE_MOVING_DOWN
            else:
                self.move(MOVE_STEP_WALL)

    # T800 Mode
    def MyMove(self, step: int):
        angle = self.getHeading()
        position = self.getPosition()
        myX = position.x()
        myY = position.y()
        deltaY = step * cos(radians(angle))
        deltaX = - step * sin(radians(angle))

        move_ok = True
        if (deltaX > 0) and (myX + deltaX > self.MapX - MOVE_LIMIT): move_ok = False
        if (deltaX < 0) and (myX + deltaX < MOVE_LIMIT): move_ok = False
        if (deltaY > 0) and (myY + deltaY > self.MapY - MOVE_LIMIT): move_ok = False
        if (deltaY < 0) and (myY + deltaY < MOVE_LIMIT): move_ok = False

        if move_ok: self.move(step)
        else: self.onHitWall()

    def MyComputeDestAway(self):
        x = y = r = 0
        for robot in self.enemies:
            r += 1
            x += self.enemies[robot]["x"]
            y += self.enemies[robot]["y"]
        x = x // r
        y = y // r
        position = self.getPosition()
        myX = position.x()
        myY = position.y()

        if myX > x: self.C1X = self.MapX - MOVE_LIMIT * 1.5
        else: self.C1X = MOVE_LIMIT * 1.5
        if myY > y: self.C1Y = self.MapY - MOVE_LIMIT * 1.5
        else: self.C1Y = MOVE_LIMIT * 1.5

        if abs(self.C1X - x) > abs(self.C1Y - y):
            self.C2X = self.C1X
            self.C2Y = self.MapY - self.C1Y
        else:
            self.C2Y = self.C1Y
            self.C2X = self.MapX - self.C1X

    def MyGoto(self, x, y, step, urgency_flag) -> bool:
        position = self.getPosition()
        myX = int(position.x()); myY = int(position.y())
        x = x // MOVE_LIMIT; y = y // MOVE_LIMIT
        myX = myX // MOVE_LIMIT; myY = myY // MOVE_LIMIT
        if myX == x and myY == y: return True

        angle = self.getHeading() % 360
        new_angle = -1
        if x > myX and y > myY: new_angle = 315
        if x > myX and y < myY: new_angle = 225
        if x < myX and y < myY: new_angle = 135
        if x < myX and y > myY: new_angle = 45
        if x > myX and y == myY: new_angle = 270
        if x < myX and y == myY: new_angle = 90
        if x == myX and y < myY: new_angle = 180
        if x == myX and y > myY: new_angle = 0

        delta_angle = new_angle - angle
        if delta_angle > 90: delta_angle -= 180; step = -step
        if delta_angle < -90: delta_angle += 180; step = -step
        if abs(delta_angle) > 5: turn_step = 5
        else: turn_step = 1
        if delta_angle < 0: turn_step = -turn_step; self.turn(turn_step)
        if delta_angle > 0: self.turn(turn_step)
        if urgency_flag or abs(delta_angle) < 30: self.MyMove(step)
        return False

    def MyComputeBotSearch(self, botSpotted):
        angles = {}
        e1 = len(self.getEnemiesLeft()) - 1
        e2 = len(self.enemies)
        if e1 == e2:
            pos = self.getPosition()
            my_radar_angle = self.getRadarHeading() % 360
            for botId in self.enemies:
                dx = self.enemies[botId]["x"] - pos.x()
                dy = self.enemies[botId]["y"] - pos.y()
                enemy_angle = math.degrees(math.atan2(dy, dx)) - 90
                a = enemy_angle - my_radar_angle
                if a < -180: a += 360
                elif 180 < a: a -= 360
                angles[a] = botId
            amin = min(angles.keys()); amax = max(angles.keys())
            self.angleMinBot = angles[amin]; self.angleMaxBot = angles[amax]

            if len(self.enemies) == 1:
                if amin > 0: self.radarGoingAngle = min([5, amin])
                elif amin < 0: self.radarGoingAngle = -min([5, -amin])
                else: self.radarGoingAngle = 1

                if botSpotted != 0 and abs(self.radarGoingAngle) < 1 and self.runcounter > self.last_time:
                    dx = self.enemies[angles[amin]]["x"] - pos.x()
                    dy = self.enemies[angles[amin]]["y"] - pos.y()
                    dist = math.sqrt(dx**2 + dy**2)
                    if self.runcounter - self.enemies[angles[amin]]["move"] > 2:
                        self.fire(int(1000 / dist) + 1)
                        self.last_time = self.runcounter + int(dist / 150)

    # Main
    def run(self):
        self.runcounter += 1
        enemy_count = len(self.getEnemiesLeft()) - 1

        if enemy_count >= 2:
            self.wallRun()
        else:
            # T800 Mode if enemy <= 2
            if self.state == STATE_INIT:
                position = self.getPosition()
                myX = position.x(); myY = position.y()
                if myX < self.MapX // 2: self.C0X = MOVE_LIMIT; self.radarGoingAngle = -5
                else: self.C0X = self.MapX - MOVE_LIMIT
                if myY < self.MapY // 2: self.C0Y = MOVE_LIMIT
                else: self.C0Y = self.MapY - MOVE_LIMIT
                self.setRadarField("round")
                self.state = STATE_RUNNING_C0
                self.MyGoto(self.C0X, self.C0Y, MOVE_STEP, True)

            elif self.state == STATE_RUNNING_C0:
                if self.runcounter > self.last_time + 5:
                    self.setRadarField("thin")
                self.MyComputeBotSearch(0)
                self.gunTurn(self.radarGoingAngle)
                self.MyGoto(self.C0X, self.C0Y, MOVE_STEP, True)
                if self.C1X != -1: self.state = STATE_RUNNING_C1

            elif self.state == STATE_RUNNING_C1:
                self.MyComputeBotSearch(0)
                self.gunTurn(self.radarGoingAngle)
                if self.MyGoto(self.C1X, self.C1Y, MOVE_STEP, False):
                    self.state = STATE_RUNNING_C2

            elif self.state == STATE_RUNNING_C2:
                self.MyComputeBotSearch(0)
                self.gunTurn(self.radarGoingAngle)
                if self.MyGoto(self.C2X, self.C2Y, MOVE_STEP, False):
                    self.state = STATE_RUNNING_C1

    # Events
    def onTargetSpotted(self, botId, botName, botPos):
        self.enemies[botId] = {"x": botPos.x(), "y": botPos.y(), "move": self.runcounter}
        self.fire(BULLET_POWER)

    def sensors(self):
        alive = [r["id"] for r in self.getEnemiesLeft()]
        for robot in list(self.enemies.keys()):
            if robot not in alive:
                del self.enemies[robot]

    def onHitWall(self):
        self.turn(90)
        self.move(-MOVE_STEP_WALL)

    def onRobotHit(self, robotId, robotName):  # when My bot hit another
        pass

    def onHitByRobot(self, robotId, robotName):
        pass

    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower):  # NECESARY FOR THE GAME
        pass

    def onBulletHit(self, botId, bulletId):  # NECESARY FOR THE GAME
        pass

    def onBulletMiss(self, bulletId):
        pass

    def onRobotDeath(self):
        pass