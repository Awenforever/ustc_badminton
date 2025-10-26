# import requirements
# local
import time
import math
import random
from datetime import datetime, timedelta

# pywin23
import win32gui
import win32api

# pyautogui
import pyautogui
# pywinauto
from pywinauto import Application
# pynput
from pynput.mouse import Controller, Button

# numpy
import numpy as np

# opencv-python
import cv2

# loguru
# from loguru import logger


BIAS = (-9, 42)  # distance from the top-left of the screen to that of the target window
SCROLL_BIAS = 1.5  # pixel offset per scroll of the mouse wheel, with one time block as the standard
BLOCK_DISTANCE = 50  # distance between the center points of two vertically / horizontally adjacent blocks


class Coordinates:
    def __init__(self, coord_dict: dict):
        super().__init__()
        for key, value in coord_dict.items():
            # key: str, value: list[tuple, tuple] | tuple[int, int]
            if 'check' in key:
                coord_dict[key][0]: tuple[int, int] = self.to_relative(value[0])

        self.coord_dict = coord_dict

    @staticmethod
    def to_relative(xy: tuple):
        return xy[0] - BIAS[0], xy[1] - BIAS[1]

    @staticmethod
    def to_absolute(xy: tuple):
        return xy[0] + BIAS[0], xy[1] + BIAS[1]

    def __getitem__(self, item: str) -> tuple[int, int] | list[tuple[int, int], tuple[int, int, int]]:
        return self.coord_dict[item]

    def __setitem__(self, key, value):
        # Handle item assignment
        self.coord_dict[key] = value  # Store the value in the dictionary


class Matcher:
    def __init__(self, win):
        super().__init__()
        self.win = win

    # @staticmethod
    def color(self, xy: tuple, target_color: tuple, threshold: float = 0.9) -> bool:
        screen_shot = self.win.capture_as_image()
        image = np.array(screen_shot)
        pixel_color = image[xy[1], xy[0]]  # height=x, width=y
        color_dist = np.linalg.norm(np.array(pixel_color) - np.array(target_color))
        max_dist = 441.67
        similarity = 1 - (color_dist / max_dist)
        if similarity >= threshold:
            return True
        else:
            return False

    def image(self, template_path, threshold=0.9, scale_factor=0.9):
        template = cv2.imread(template_path)
        target = self.win.capture_as_image()
        target = np.array(target)
        target = cv2.cvtColor(target, cv2.COLOR_BGR2RGB)

        w, h = template.shape[:2][::-1]
        wh = (w, h)
        scale = 1.0
        matches = []

        while w > 15 and h > 15:
            # match
            result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)

            # filter
            max_loc = np.unravel_index(np.argmax(result), result.shape)
            loc = np.where(np.atleast_1d(result[max_loc]) >= threshold)

            # result
            if loc == ([0],):
                matches.extend(max_loc[::-1])
                break

            # resize the template image
            scale *= scale_factor
            w = int(w * scale)
            h = int(h * scale)
            template = cv2.resize(template, (w, h))

        if len(matches) > 0:
            # for pt in zip(*loc[::-1]):  # loc[::-1] 转换成 (x, y) 格式
            #     cv2.rectangle(target, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)
            # cv2.imshow('Matches', target)
            # cv2.waitKey(0)
            return matches[0] + wh[0], matches[1] + wh[1]
        else:
            result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
            max_loc = np.unravel_index(np.argmax(result), result.shape)
            loc = np.where(np.atleast_1d(result[max_loc]) >= threshold)
            # for pt in zip(*loc[::-1]):  # loc[::-1] 转换成 (x, y) 格式
            #     cv2.rectangle(target, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)
            # cv2.imshow('Matches', target)
            # cv2.waitKey(0)

            if loc == ([0],):
                # return [(pt[0] + w // 2, pt[1] + h // 2) for pt in zip(*loc[::-1])]
                matches.extend(max_loc[::-1])
                # matches.extend(list(zip(*loc[::-1])))
                return matches[0] + wh[0], matches[1] + wh[1]
                # return matches[0][0] + wh[0], matches[0][1] + wh[1]
            return None


class AutoSnatch:
    def __init__(self, win, coord, companion, campus, today_or_tomorrow, index, start_time, num, stake_out):
        super().__init__()
        self.win = win
        self.c = coord
        self.companion = companion
        self.campus = campus
        self.tot = today_or_tomorrow
        self.idx = index
        self.start_time = start_time
        self.m = Matcher(win)
        self.num = num
        self.stake_out = stake_out
        if campus == 'west':
            if index > 8:
                self.index = random.randint(1, 8)
            self.index_untried = [1, 2, 3, 4, 5, 6, 7, 8]
            self.x_bench = coord['w1_x'][0]
        elif campus == 'east':
            if index > 6:
                index = random.randint(1, 6)
            self.index_untried = [1, 2, 3, 4, 5, 6]
            self.x_bench = coord['e1_x'][0]
        elif campus == 'middle':
            if index > 14:
                index = random.randint(1, 14)
            self.index_untried = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
            self.x_bench = coord['w1_x'][0]  # same as west campus
        else:
            raise ValueError("Right now only support `west` or `east` for @param `campus`.")
        self.index_untried.remove(index)
        self.find_companion_coord()

    @property
    def now(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    @staticmethod
    def check_time():
        now = datetime.now()
        target_time = datetime.strptime(f"{now.date()} 21:00:01", "%Y-%m-%d %H:%M:%S")
        if now >= target_time:
            return True
        else:
            return False

    def refresh(self):
        """
        Click the `appointment` button, select the companion and switch to `tomorrow` or not.
        """
        if self.tot == 'tomorrow':
            if not self.check_time():
                print(f'[{self.now}] Waiting for 21:00!')
                return False
        print(f'[{self.now}] Snatching the No.{self.idx} court '
              f'starting at {str(self.start_time)[:-2]}:{str(self.start_time)[-2:]} for {self.tot}...')

        not_stop = True
        while not_stop:
            # click 'click appointment'
            print(f'[{self.now}] Refreshing the page...')
            pyautogui.click(x=self.c['click_appointment'][0], y=self.c['click_appointment'][1])
            time.sleep(0.1)
            while True:
                pyautogui.click(x=self.c[self.campus][0], y=self.c[self.campus][1])
                if self.m.color(self.c[self.campus + '_check'][0], self.c[self.campus + '_check'][1]):
                    print(f'[{self.now}] Switched to {self.campus } campus.')
                    while True:
                        if self.m.color(self.c['companion_check'][0], self.c['companion_check'][1]):
                            print(f'[{self.now}] The first default companion is locked.')
                            break
                        pyautogui.click(x=self.c['companion'][0], y=self.c['companion'][1])
                        time.sleep(0.1)
                    break

            # chose today or tomorrow
            if self.tot == 'today':
                not_stop = False
            while self.tot == 'tomorrow':
                print(f'[{self.now}] Switching to `tomorrow`...')
                pyautogui.click(self.c['tomorrow'][0], self.c['tomorrow'][1])
                if self.m.color(self.c['tomorrow_check'][0], self.c['tomorrow_check'][1]):
                    not_stop = False
                    break
                if self.m.color(self.c['tip_check'][0], self.c['tip_check'][1]):  #
                    break
        return True

    def tot_time_conversion(self):
        """
        Convert today's start_time to equivalent standard start_time.
        """
        if self.tot == 'today':
            now = datetime.now()
            # now = datetime.strptime(f"{now.date()} 11:40:00", "%Y-%m-%d %H:%M:%S")
            minute_block = np.array([0, 15, 30, 45, 60])
            minute = now.minute - minute_block
            minute = np.min(abs(minute[minute <= 0])).astype(float)
            hours = 0
            if now.minute + minute > 45:
                hours = 1
                minute = - now.minute
            bench_time = now + timedelta(hours=hours, minutes=minute, seconds=-now.second, microseconds=-now.microsecond)
            start_time = str(self.start_time)
            start_time = datetime.strptime(f"{now.date()} {start_time[:-2]}:{start_time[-2:]}:00", "%Y-%m-%d %H:%M:%S")
            start_time = start_time - bench_time + datetime.strptime(f"{now.date()} 8:00:00", "%Y-%m-%d %H:%M:%S")
            self.start_time = int(start_time.hour * 100 + start_time.minute)

    def time2coord(self, start_time: int):
        """
        Produce the corresponding scroll numbers and y_coord through computing the loc of start_time block.
        """
        scroll_max = 15
        period_min = 800
        period_max = 2100
        assert period_min <= start_time, f"Earliest start time block is 9:00. (900), got {start_time}."
        assert period_max >= start_time, f"Latest start time block is 21:00. (2100), got {start_time}."
        time_table = np.array([
            900, 945, 1030, 1115,
            1200, 1245, 1330, 1415,
            1500, 1545, 1630, 1715,
            1800, 1845, 1930, 2000,
        ])

        time_loc = start_time - time_table  # broadcasting
        dy_scroll = np.argmin(abs(time_loc))
        diff = time_loc[dy_scroll]
        y_coord = self.c['bench_y'][1] - math.floor(dy_scroll * SCROLL_BIAS)
        if diff != 0 and diff != 100 and diff >= -45:
            y_coord += (diff // 15) * BLOCK_DISTANCE
        elif diff == 100:  # start_time = 2100
            y_coord += 4 * BLOCK_DISTANCE
        elif diff < -45:
            diff += 40  # start_time = 800, 800 - 900 = -100 -> -60
            y_coord += (diff // 15) * BLOCK_DISTANCE
        return dy_scroll, y_coord

    def locate_patch_and_select(self, scroll, x, y):  # 1012, 826
        """
        Select aimed blocks and submit.
        """
        print(f'[{self.now}] Locating time blocks ...')
        # x = 1140  # east audience
        # x = 1064  # east 6
        # y = 947 - 42
        mouse = Controller()
        # move to start block
        mouse.position = (x, y)
        mouse.scroll(0, -scroll)
        time.sleep(0.5)
        if self.stake_out:
            time.sleep(0.1)
            if not self.m.color((x - 5, y - 5), (255, 255, 255)):
                return False

        print(f'[{self.now}] Selecting ...')
        # click start block
        mouse.click(Button.left, 1)
        time.sleep(0.5)
        # mouse.click(Button.left, 1)
        # time.sleep(0.1)
        # mouse.click(Button.left, 1)

        # click end block
        mouse.position = (x, y + max(min(self.num - 1, 5), 1) * BLOCK_DISTANCE)
        time.sleep(0.1)
        mouse.click(Button.left, 1)
        time.sleep(0.5)
        # mouse.click(Button.left, 1)
        # time.sleep(0.1)

        print(f'[{self.now}] Submitting ...')
        mouse.position = self.c['submit_auto']  # todo: auto locate the submit button
        # mouse.position = coord['submit_test']
        mouse.click(Button.left, 1)
        # pyautogui.leftClick(1194, 660)
        return True

    def find_submit_coord(self):
        return self.m.image('submit_auto.png', 0.9)  # todo: check this !!!

    def find_companion_coord(self):
        if self.companion != (1, 1):
            self.c['companion'] = (
                self.c['companion'][0] + (self.companion[0] - 1) * 179,
                self.c['companion'][1] + (self.companion[1] - 1) * 80
            )
            self.c['companion_check'] = (
                (
                    self.c['companion_check'][0][0] + (self.companion[0] - 1) * 179,
                    self.c['companion_check'][0][1] + (self.companion[1] - 1) * 80
                ),
                self.c['companion_check'][1]
            )

    def __call__(self):
        self.tot_time_conversion()
        scroll, y_coord = self.time2coord(self.start_time)  # calculating the corresponding scroll number and y_coord

        cheat = True
        while cheat:
            start_time = time.perf_counter()

            x_coord = self.x_bench + (self.idx - 1) * BLOCK_DISTANCE  # locate the index

            if self.refresh():
                time.sleep(0.1)
                self.c['submit_auto'] = self.c.to_absolute(self.find_submit_coord())
                result = self.locate_patch_and_select(scroll, x_coord, y_coord)
                while result:
                    time.sleep(0.5)
                    if (
                            self.m.color(self.c['tip_check'][0], self.c['tip_check'][1]) or
                            self.m.color(self.c['tip2_check'][0], self.c['tip2_check'][1])
                    ):
                        try:
                            self.idx = random.choice(self.index_untried)
                            self.index_untried.remove(self.idx)
                            print(f'[{self.now}] Trying court of No.{self.idx}...')
                        except Exception as e:
                            cheat = False
                            print(f'[{self.now}] Try other time blocks.')
                        break
                    if not self.m.color(self.c['place_intro_check'][0], self.c['place_intro_check'][1]):
                        cheat = False
                        end_time = time.perf_counter()
                        elapsed_time = end_time - start_time
                        print(f'[{self.now}] Target time block is locked successfully within {elapsed_time:.3f} sec!')
                        break
                    if (self.m.color(self.c['notice_check'][0], self.c['notice_check'][1]) or
                            self.m.color(self.c['intercepted_check'][0], self.c['intercepted_check'][1])):
                        print(f'[{self.now}] Your account is banned or the selected blocks have been locked by others.')
                        while True:
                            pyautogui.leftClick(x=self.c['notice'][0], y=self.c['notice'][1])
                            if (not self.m.color(self.c['notice_check'][0], self.c['notice_check'][1]) and
                            not self.m.color(self.c['intercepted_check'][0], self.c['intercepted_check'][1])):
                                time.sleep(0.5)
                                break
                        break

def main(
        coord: Coordinates,
        companion: tuple[int, int],
        campus: str,
        today_or_tomorrow: str,
        index: int,
        start_time: int,
        num: int,
        stake_out: bool
):
    # get screen resolution
    w, h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(0)

    # get handle
    hwnd = win32gui.FindWindow(None, '中国科大体育运动预约管理')
    l, t, r, b = win32gui.GetWindowRect(hwnd)

    # win32gui.MoveWindow(hwnd, BIAS[0], BIAS[1], r - l, b - t, True)

    # connect window
    app = Application().connect(handle=hwnd)
    window = app.window(handle=hwnd)
    window.set_focus()

    if l > 0:
        pyautogui.hotkey('win', 'left')
        time.sleep(0.1)
        pyautogui.leftClick(34, 64)

    auto_snatch = AutoSnatch(window, coord, companion, campus, today_or_tomorrow, index, start_time, num, stake_out)

    # grabbing
    auto_snatch()


if __name__ == '__main__':
    c = Coordinates({
        'click_appointment': (396, 823),
        'place_intro_check': [(1208, 183), (0, 122, 51)],  # place introduction
        'companion': (731, 1344),  # default companion
        'companion_check': [(809, 1373), (2, 125, 255)],  # selected companion
        'submit': (936, 1550),
        'submit_3': (936, 1710),  # 2 lines companion
        'submit_0': (936, 1550),  # 1 line companion
        'submit_lja': (936, 1630),  # lja
        'submit_djy': (936, 1957),  # djy
        # 'submit1_check': (726, 1552),
        'submit_auto': (0, 0),  # auto detect the `submit` button
        'submit_test': (936, 1386),  # only used when selecting audience block
        'east': (719, 360),  # `east campus` button
        'east_check': [(666, 360), (116, 183, 140)],
        'middle': (870, 360),
        'middle_check': [(940, 360), (116, 183, 140)],
        'west': (1014, 360),
        'west_check': [(1063, 360), (116, 183, 140)],
        'high_tech': (1146, 360),
        'today': (846, 422),
        'tomorrow': (1111, 424),
        'tomorrow_check': [(1139, 423), (116, 183, 140)],
        'notice': (536, 1190),  
        'notice_check': [(536, 1190), (12, 193, 96)],  # you are banned
        'intercepted_check': [(550, 1193), (89, 206, 169)],
        'w1_x': (774, 748),  # the coordinate of the first time block on the left in `west` campus, only use the `x`
        'e1_x': (817, 530),  # first x on the left in `east` campus
        'tip_check': [(1065, 1760), (76, 76, 76)],  # at least 2 blocks
        'tip2_check': [(932, 1774), (73, 73, 73)],
        'bench_y': (925, 730)
    })
    main(c, (1, 1), 'west', 'tomorrow', 6, 2030, 6, False)
    # check if network's environment is normal
