# -*- coding: utf-8 -*-
import math
import random
from robot import Robot

# == constants ==
MOVE_STEP = 6
WALL_DISTANCE = 50
WALL_TURN_MARGIN = 10
WALL_TURN = 90

SCAN_STEP = 12
BULLET_POWER = 2
GUN_RANDOM_AIM_ERROR = 2.0

STATE_MOVING_UNKNOWN_DIRECTION = 0
STATE_MOVING_UP    = 1
STATE_MOVING_RIGHT = 2
STATE_MOVING_DOWN  = 3
STATE_MOVING_LEFT  = 4


class ZERO_Advance(Robot):
    def init(self):
        # color
        self.setColor(0, 255, 255)
        self.setGunColor(200, 200, 200)
        self.setRadarColor(200, 100, 0)
        self.setBulletsColor(255, 255, 230)

        # radar
        self.radarVisible(True)
        self.lockRadar("gun")
        self.setRadarField("thin") # aiming mode

        # 状態
        self.state = STATE_MOVING_UNKNOWN_DIRECTION # start state
        self.enemy_positions = {} # enemy_id -> position
        self.last_hit_from = None # rival id
        self.hit_wall_counter = 0 # hit wall count

        # マップ
        size = self.getMapSize() # QSize
        self._map_w = size.width()
        self._map_h = size.height()

        # フラグ
        self._handling_wall = False

    # == Util ==
    @staticmethod
    def _norm_angle(a: float) -> float: # 常に角度を正規化 avoiding wrap-around
        while a > 180:
            a -= 360
        while a < -180:
            a += 360
        return a

    def _deg_diff(self, target: float, current: float) -> float:  # for minimal turn
        return self._norm_angle((target % 360) - (current % 360)) # target - current

    def _state_heading(self, state: int) -> float: # difinition of heading angle for each state
        # Down(0), Left(90), Up(180), Right(270) の座標系
        if state == STATE_MOVING_DOWN:
            return 0
        if state == STATE_MOVING_LEFT:
            return 90
        if state == STATE_MOVING_UP:
            return 180
        if state == STATE_MOVING_RIGHT:
            return 270
        return 0

    def myTurn(self, angle: float): # turn body and gun synchronously
        self.turn(angle)
        self.gunTurn(angle)

    # == Safety Play ==
    def MyMove(self, step: int) -> bool:
        # Do not be too close to the wall
        # get current angle and position
        angle = self.getHeading()
        pos = self.getPosition()
        myX, myY = pos.x(), pos.y()
        # calculate delta
        deltaY = step * math.cos(math.radians(angle))
        deltaX = -step * math.sin(math.radians(angle))
        # check wall distance
        limit = WALL_DISTANCE
        # determine if move is ok
        move_ok = True
        if (deltaX > 0) and (myX + deltaX > self._map_w - limit):
            move_ok = False
        if (deltaX < 0) and (myX + deltaX < limit):
            move_ok = False
        if (deltaY > 0) and (myY + deltaY > self._map_h - limit):
            move_ok = False
        if (deltaY < 0) and (myY + deltaY < limit):
            move_ok = False

        if move_ok:
            self.move(step)
            return True
        return False

    def _safe_move(self, step: int) -> bool:
        # Try to move with decreasing step sizes
        # Return True if moved successfully
        if step == 0:
            return False
        sgn = 1 if step > 0 else -1
        # try full step first, then smaller steps
        for ratio in (1.0, 0.6, 0.3):
            mag = int(abs(step) * ratio)
            if mag < 1:
                continue
            if self.MyMove(sgn * mag):
                return True
        return False

    def move_following_walls(self):
        # Move along the wall according to current state
        # Determine target heading
        # Rotate towards target heading
        target = self._state_heading(self.state)
        cur = self.getHeading() % 360
        da = self._deg_diff(target, cur)
        # Limit turn speed
        # Turn step between 2 and 10 degrees
        # Adjust turn speed based on angle difference
        turn_step = max(2.0, min(10.0, abs(da) / 3.0))
        turn_cmd = max(-turn_step, min(turn_step, da))
        self.turn(turn_cmd)  # turn body only
        # Move forward if angle difference is small
        if abs(da) > 90:
            self._safe_move(-MOVE_STEP)
        else:
            self._safe_move(MOVE_STEP)

    # ---------- 壁沿い周回 ----------
    def wallRun(self):
        # around the map following the wall
        # check position and decide if need to turn
        pos = self.getPosition()
        x, y = pos.x(), pos.y()
        # margin for turning before hitting wall
        margin = WALL_DISTANCE + WALL_TURN_MARGIN

        # starting direction
        # first time initialization
        # face downwards
        if self.state == STATE_MOVING_UNKNOWN_DIRECTION:
            self.myTurn(-(self.getHeading() % 360))
            self.state = STATE_MOVING_DOWN
        # check if need to turn at corners
        # turn if close to wall in current direction
        turned = False
        if self.state == STATE_MOVING_UP and y < margin:
            self.state = STATE_MOVING_RIGHT
            self.myTurn(WALL_TURN); turned = True
        elif self.state == STATE_MOVING_DOWN and self._map_h - y < margin:
            self.state = STATE_MOVING_LEFT
            self.myTurn(WALL_TURN); turned = True
        elif self.state == STATE_MOVING_LEFT and x < margin:
            self.state = STATE_MOVING_UP
            self.myTurn(WALL_TURN); turned = True
        elif self.state == STATE_MOVING_RIGHT and self._map_w - x < margin:
            self.state = STATE_MOVING_DOWN
            self.myTurn(WALL_TURN); turned = True

        if turned:
            # turn to safety play after turning
            self._safe_move(MOVE_STEP * 2)

        # never stop moving
        self.move_following_walls()

    # == Aiming ==
    # aim at given position and return angle difference
    # calculate position difference between self and target
    def aimAt(self, botPos):
        me = self.getPosition()
        dx = botPos.x() - me.x()
        dy = botPos.y() - me.y()
        target_angle = math.degrees(math.atan2(dy, dx)) - 90
        # calculate angle difference
        # always return minimal angle difference
        return self._deg_diff(target_angle, self.getGunHeading() % 360)

    # predictive fire with slight random error
    def predictiveFire(self, botPos, power=BULLET_POWER):
        # calculate angle while being attacked by bullets
        # because position could be exposed when hit by bullet
        # add random error to avoid being countered easily
        angle_error = random.uniform(-GUN_RANDOM_AIM_ERROR, GUN_RANDOM_AIM_ERROR)
        delta_angle = self.aimAt(botPos) + angle_error
        self.gunTurn(delta_angle)
        self.fire(power)

    # == Main Loop ==
    def run(self):
        # Non-stop, always move, even when firing or enemies coming
        self.sensors()
        self.gunTurn(SCAN_STEP)
        self.wallRun()

    # == Events ==
    # shots fired when target spotted or hit by bullet
    def onTargetSpotted(self, botId, botName, botPos):
        # spot enemy and fire
        self.enemy_positions[botId] = botPos
        self.predictiveFire(botPos, BULLET_POWER)

    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower):
        # being attacked and fire back
        self.last_hit_from = bulletBotId
        if bulletBotId in self.enemy_positions:
            self.predictiveFire(self.enemy_positions[bulletBotId], BULLET_POWER)
    # avoid wall getting stuck
    def onHitWall(self):
        # never stop moving just tiny moving is ok
        if self._handling_wall:
            return
        self._handling_wall = True
        try:
            self.hit_wall_counter += 1

            # if wall hit too many times, back off immediately
            self.move(-max(MOVE_STEP, 8))
            # determine next state based on current position
            pos = self.getPosition()
            x, y = pos.x(), pos.y()

            # decide next state to move away from wall
            if y < WALL_DISTANCE:
                next_state = STATE_MOVING_RIGHT
            elif self._map_h - y < WALL_DISTANCE:
                next_state = STATE_MOVING_LEFT
            elif x < WALL_DISTANCE:
                next_state = STATE_MOVING_UP
            else:
                next_state = STATE_MOVING_DOWN

            target = self._state_heading(next_state)
            delta = self._deg_diff(target, self.getHeading() % 360)
            self.myTurn(delta)
            self.state = next_state

            # try to move forward safely
            self._safe_move(MOVE_STEP * 2)
        finally:
            self._handling_wall = False

    # sensors: cleanup dead enemies
    def sensors(self):
        # do not keep dead enemies in memory
        alive = {r["id"] for r in self.getEnemiesLeft()}
        for rid in list(self.enemy_positions.keys()):
            if rid not in alive:
                del self.enemy_positions[rid]
                if self.last_hit_from == rid:
                    self.last_hit_from = None

    # skipped events
    def onRobotHit(self, robotId, robotName): pass
    def onHitByRobot(self, robotId, robotName): pass
    def onBulletHit(self, botId, bulletId): pass
    def onBulletMiss(self, bulletId): pass
    def onRobotDeath(self): pass

    """
    in a word
    常に動き続け、壁にぶつかりそうになったら回避しつつ壁沿いに移動する。
    常に角度をリセットしながら壁沿いに動くことで、壁にぶつかるリスクを減らす。
    スタックする確率も減る。
    敵を発見したら予測射撃を行い、被弾したら反撃する。
    予測射撃にはわずかなランダム誤差を加えることで、相手に簡単にカウンターされるのを防ぐ。
    これにより、安定した戦闘能力を維持しつつ、生存率を高めることができる。
    """

    # Q Learningを実装すればどうだろう