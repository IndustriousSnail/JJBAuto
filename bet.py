import math
import random
import time

import log


def get_curr_rate():
    time.sleep(3)
    left = 14 - math.log(random.Random().randint(2, 442413))
    return {
        "left": round(left, 2),
        "right": round(1 + 1/(left-1), 2),
        "is_pause": False
    }


class Bet(object):

    def __init__(self):
        self.left_bet = 0   # 左边投注
        self.right_bet = 0  # 右边投注

    def record_log(self):
        """记录投注日志"""
        pass

    def bet(self, rate):
        log.debug("左赔率：%s，右赔率：%s" % (rate['left'], rate['right']))
        if rate['left'] >= 2.5 and (self.left_bet - self.right_bet == 0):
            # 如果左赔率大于等于2.5，并且都还没压过，左边压200
            self.left_bet += 200
            log.info("左压200")

        if rate['right'] >= 2.5 and (self.left_bet - self.right_bet == 0):
            # 如果右赔率大于等于2.5，并且都还没压过，左边压200
            self.right_bet += 200
            log.info("右压200")

        if rate['left'] >= 5 and (self.left_bet - self.right_bet == 200):
            # 如果左赔率大于5，并且压的小于200，再压100
            self.left_bet += 100
            log.info("左压100")

        if rate['right'] >= 5 and (self.right_bet - self.right_bet == 200):
            # 如果右赔率大于5，并且压的小于200，再压100
            self.right_bet += 100
            log.info("右压100")

        if 8 <= rate['left'] <= 12 and (self.left_bet - self.right_bet == 300):
            self.left_bet += 100
            log.info("左压100")

        if 8 <= rate['right'] <= 12 and (self.right_bet - self.left_bet == 300):
            self.right_bet += 100
            log.info("右压100")

        if rate['left'] >= 2 and (self.right_bet > self.left_bet):
            # 如果左边赔率>2，现在右边压的钱比左边多
            log.info("左压%s" % (self.right_bet - self.left_bet))
            self.left_bet += (self.right_bet - self.left_bet)

        if rate['right'] >= 2 and (self.left_bet > self.right_bet):
            # 如果左边赔率>2，现在右边压的钱比左边多
            log.info("右压%s" % (self.left_bet - self.right_bet))
            self.right_bet += (self.left_bet - self.right_bet)

if __name__ == '__main__':
    Bet().bet()




