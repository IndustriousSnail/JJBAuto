import datetime
import random


def get_today_timestamp():
    ctime = datetime.datetime.now()
    timestamp = int(
        datetime.datetime.strptime("%s-%s-%s" % (ctime.year, ctime.month, ctime.day), "%Y-%m-%d").timestamp())
    return timestamp


def get_random():
    return str(random.random())[:-2]