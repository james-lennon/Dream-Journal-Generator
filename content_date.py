import random
import time

TIME_FORMAT = "%d.%m.%Y"


def generate_date(previous):
    start_time = time.mktime(time.strptime(previous, TIME_FORMAT))
    ptime = start_time + random.randrange(24*3600, 90*3600)

    return time.strftime(TIME_FORMAT, time.localtime(ptime))


if __name__ == '__main__':
    cur_time = time.strftime("%d.%m.%Y")
    print generate_date(cur_time)
