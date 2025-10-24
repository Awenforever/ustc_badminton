# import requirements
# local
import logging
import time
import math
import random
from datetime import datetime, timedelta
import ctypes
from ctypes import wintypes
# from typing import List

# pywin23
import win32gui
# import win32api

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
UNIT_SCROLL_DISTANCE = 150
SCROLL_LAST_DISTANCE_VERTICAL = 110
SCROLL_LAST_DISTANCE_HORIZONTAL_H = 12
SCROLL_LAST_DISTANCE_HORIZONTAL_M = 63
SCROLL_MAX_VERTICAL = 14
SCROLL_DISTANCE_MAX_VERTICAL = SCROLL_MAX_VERTICAL * UNIT_SCROLL_DISTANCE + SCROLL_LAST_DISTANCE_VERTICAL
COMPANION_DISTANCE_X = 179
COMPANION_DISTANCE_Y = 80

SCROLL_BIAS = 1.5
# pixel offset per scroll of the mouse wheel, with one time block as the standard
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

    def __getitem__(self, item: str) -> tuple[int, int] | list[tuple[int, int, ...]]:
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


class Place:
    def __init__(self, campus: str, idx: int):
        self.campus = campus
        self.idx = idx
        self.max_index_dict = {
            'west': 8,
            'east': 6,
            'middle': 14,
            'high_tech': 12
        }
        self.index_untried = None

    @staticmethod
    def idx_list(num: int, pop_idx: int):
        il = [i for i in range(1, num + 1)]
        il.remove(pop_idx)
        return il

    def initialize(self):
        try:
            max_idx = self.max_index_dict[self.campus]
        except KeyError:
            raise KeyError("Right now only support `west`, `east`, `middle`, and `high_tech` for @param `campus`.")
        if not self.idx <= max_idx:
            self.idx = 1
        self.index_untried = self.idx_list(max_idx, self.idx)

    def update(self):
        self.idx = random.choice(self.index_untried)
        self.index_untried.remove(self.idx)
        print(f'[{AutoSnatch.now()}] Trying court No.{self.idx}...')


class AutoSnatch:
    def __init__(self, win, coord, companion, campus, today_or_tomorrow, index, start_time, num, stake_out):
        super().__init__()
        self.win = win
        self.c = coord
        self.tot = today_or_tomorrow
        self.start_time = start_time
        self.m = Matcher(win)
        self.num = num
        self.stake_out = stake_out
        self.campus = Place(campus, index)
        self.campus.initialize()
        self.find_companion_coord(companion)

    @staticmethod
    def now() -> str:
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
                print(f'[{self.now()}] Waiting for 21:00!')
                return False
        print(f'[{self.now()}] Snatching the No.{self.campus.idx} court '
              f'starting at {self.start_time[:-2]}:{self.start_time[-2:]} for {self.tot}...')

        not_stop = True
        while not_stop:
            # click 'click appointment'
            print(f'[{self.now()}] Refreshing the page...')
            pyautogui.click(x=self.c['click_appointment'][0], y=self.c['click_appointment'][1])
            time.sleep(0.1)
            while True:
                pyautogui.click(x=self.c[self.campus.campus][0], y=self.c[self.campus.campus][1])
                if self.m.color(self.c[self.campus.campus + '_check'][0], self.c[self.campus.campus + '_check'][1]):
                    print(f'[{self.now()}] Switched to {self.campus.campus } campus.')
                    time.sleep(0.1)
                    pyautogui.click(x=self.c['companion'][0], y=self.c['companion'][1])
                    # while True:
                    #     time.sleep(0.5)
                    #     if self.m.color(self.c['companion_check'][0], self.c['companion_check'][1]):
                    #         print(f'[{self.now()}] The selected companion is locked.')
                    #         break
                    break

            # chose today or tomorrow
            if self.tot == 'today':
                not_stop = False
            while self.tot == 'tomorrow':
                print(f'[{self.now()}] Switching to `tomorrow`...')
                pyautogui.click(self.c['tomorrow'][0], self.c['tomorrow'][1])
                if self.m.color(self.c['tomorrow_check'][0], self.c['tomorrow_check'][1]):
                    not_stop = False
                    break
                if self.m.color(self.c['tip_check'][0], self.c['tip_check'][1]):
                    break
        return True

    @staticmethod
    def diff_min(time1, time2):
        return int((time1 - time2).total_seconds() // 60)

    @staticmethod
    def round(now):
        # 向上取整的分钟数
        rounded_minute = ((now.minute + 14) // 15) * 15

        # 如果到达 60，需要进位到下一小时
        if rounded_minute == 60:
            rounded_time = now.replace(hour=now.hour + 1 if now.hour + 1 != 24 else 0, minute=0, second=0, microsecond=0)
        else:
            rounded_time = now.replace(minute=rounded_minute, second=0, microsecond=0)

        return rounded_time

    def time2y(self, start_time: str) -> tuple[int, int]:
        bench_time = datetime.strptime("08:00", "%H:%M")
        start_time = datetime.strptime(f"{start_time[:-2]}:{start_time[-2:]}", "%H:%M")
        rest = SCROLL_MAX_VERTICAL
        even = False

        if self.tot == 'today':
            now = datetime.now()
            now_time = self.round(datetime.strptime(f"{now.hour}:{now.minute}", "%H:%M"))
            # last_time = datetime.strptime("22:15", "%H:%M")
            bottom_time = datetime.strptime("19:15", "%H:%M")
            if now_time < bench_time:
                now_time = bench_time
            elapsed = self.diff_min(now_time, bench_time)
            n = elapsed // 15
            even = True if n % 2 == 0 else False
            # s = 49.5 * n + (1 - (-1) ** n) / 4
            n = self.diff_min(bottom_time, now_time) // 15
            rest = 49.5 * n - (1 - (-1) ** n) / 4 if even else 49.5 * n + (1 - (-1) ** n) / 4
            rest = divmod(rest, UNIT_SCROLL_DISTANCE)[0]
            bench_time = now_time

        diff = self.diff_min(start_time, bench_time)
        n = diff // 15
        s = 49.5 * n - (1 - (-1) ** n) / 4 if even else 49.5 * n + (1 - (-1) ** n) / 4
        q, r = divmod(s, UNIT_SCROLL_DISTANCE)
        if q > rest:
            over = q - rest - 1
            r += 150 * over + (UNIT_SCROLL_DISTANCE - SCROLL_LAST_DISTANCE_VERTICAL)

        return q, int(self.c[self.campus.campus + '_lt'][1] + r)

    def index2x(self, index: int) -> tuple[int, int]:
        bench_index = 1
        max_index = self.campus.max_index_dict[self.campus.campus]
        max_n = max_index - 7
        max_s = 49.5 * max_n - (1 - (-1) ** max_n) / 4
        max_q = divmod(max_s, UNIT_SCROLL_DISTANCE)[0]
        n = index - bench_index
        s = 49.5 * n - (1 - (-1) ** n) / 4
        q, r = divmod(s, UNIT_SCROLL_DISTANCE)
        if q > max_q:
            over = q - max_q
            r += over * UNIT_SCROLL_DISTANCE
            q = max_q
        return q, int(self.c[self.campus.campus + '_lt'][0] + r)

    def locate_patch_and_select(self, x_scroll, x, y_scroll, y):  # 1012, 826
        """
        Select aimed blocks and submit.
        """
        print(f'[{self.now()}] Locating time blocks ...')
        # x = 1140  # east audience
        # x = 1064  # east 6
        # y = 947 - 42
        mouse = Controller()
        # move to start block
        mouse.position = (x, y)
        mouse.scroll(x_scroll, -y_scroll)
        time.sleep(0.5)
        if self.stake_out:
            time.sleep(0.5)
            if not self.m.color(Coordinates.to_relative((x - 5, y - 5)), (255, 255, 255)):
                return False

        print(f'[{self.now()}] Selecting ...')
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

        print(f'[{self.now()}] Submitting ...')
        mouse.position = self.c['submit_auto']  # auto locate the submit button
        # mouse.position = coord['submit_test']
        mouse.click(Button.left, 1)
        # pyautogui.leftClick(1194, 660)
        return True

    def find_submit_coord(self):
        return self.m.image('submit_auto.png', 0.9)  # todo: check this !!! || fixed √

    def find_companion_coord(self, companion: tuple[int, int]):
        if companion != (1, 1):
            self.c['companion'] = (
                self.c['companion'][0] + (companion[0] - 1) * COMPANION_DISTANCE_X,
                self.c['companion'][1] + (companion[1] - 1) * COMPANION_DISTANCE_Y
            )
            self.c['companion_check'] = (
                (
                    self.c['companion_check'][0][0] + (companion[0] - 1) * COMPANION_DISTANCE_X,
                    self.c['companion_check'][0][1] + (companion[1] - 1) * COMPANION_DISTANCE_Y
                ),
                self.c['companion_check'][1]
            )

    def __call__(self):
        # self.tot_time_conversion()
        y_scroll, y_coord = self.time2y(self.start_time)  # calculating the corresponding scroll number and y_coord

        cheat = True
        while cheat:
            start_time = time.perf_counter()
            # todo: self.shift is not updated for every loop || fixed √
            # x_coord = self.campus.x_bench + (self.campus.idx - 1) * BLOCK_DISTANCE  # locate the index
            x_scroll, x_coord = self.index2x(self.campus.idx)
            if self.refresh():
                time.sleep(0.1)
                self.c['submit_auto'] = self.c.to_absolute(self.find_submit_coord())
                result = self.locate_patch_and_select(x_scroll, x_coord, y_scroll, y_coord)
                while result:
                    time.sleep(0.5)
                    if (
                            self.m.color(self.c['tip_check'][0], self.c['tip_check'][1])
                    ):
                        print(f'[{self.now()}] Detected grey tips!')
                        try:
                            self.campus.update()
                        except Exception:
                            cheat = False
                            print(f'[{self.now()}] Try other time blocks.')
                        break
                    if not self.m.color(self.c['place_intro_check'][0], self.c['place_intro_check'][1]):
                        cheat = False
                        end_time = time.perf_counter()
                        elapsed_time = end_time - start_time
                        print(f'[{self.now()}] Target time block is locked successfully within {elapsed_time:.3f} sec!')
                        break
                    if (
                            self.m.color(self.c['notice_check'][0], self.c['notice_check'][1]) or
                            self.m.color(self.c['preempted_check'][0], self.c['preempted_check'][1])
                    ):
                        print(f'[{self.now()}] Your account is banned, or the selected blocks have been locked by others,'
                              f'or the locked companion is occupied.')
                        while True:
                            pyautogui.leftClick(x=self.c['notice'][0], y=self.c['notice'][1])
                            time.sleep(0.1)
                            pyautogui.leftClick(x=self.c['preempted'][0], y=self.c['preempted'][1])
                            if (not self.m.color(self.c['notice_check'][0], self.c['notice_check'][1]) and
                            not self.m.color(self.c['preempted_check'][0], self.c['preempted_check'][1])):
                                time.sleep(0.5)
                                break
                        try:
                            self.campus.update()
                        except Exception:
                            cheat = False
                            print(f'[{self.now()}] Try other time blocks.')
                        break


def main(
        coord: Coordinates,
        companion: tuple[int, int],
        campus: str,
        today_or_tomorrow: str,
        index: int,
        start_time: str,
        num: int,
        stake_out: bool
):
    # get screen resolution
    # w, h = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    # scale = get_dpi_scaling()
    # print(w, h, scale)
    # ! Calculating new coordinates based on resolution and scaling factor is unreliable.

    # get handle
    hwnd = win32gui.FindWindow(None, '中国科大体育运动预约管理')
    l, t, r, b = win32gui.GetWindowRect(hwnd)

    # win32gui.MoveWindow(hwnd, BIAS[0], BIAS[1], r - l, b - t, True)  # not working at all

    # connect window
    app = Application().connect(handle=hwnd)
    window = app.window(handle=hwnd)
    window.set_focus()

    if l > 0:
        pyautogui.hotkey('win', 'left')
        time.sleep(0.1)
        pyautogui.leftClick(800, 64)

    auto_snatch = AutoSnatch(window, coord, companion, campus, today_or_tomorrow, index, start_time, num, stake_out)

    # grabbing
    auto_snatch()


if __name__ == '__main__':
    c = Coordinates({
        'click_appointment': (396, 823),
        'place_intro_check': [(1208, 183), (0, 122, 51)],  # place introduction
        'companion': (731, 1344),  # default companion
        'companion_check': [(809, 1373), (2, 125, 255)],  # selected companion
        'submit_auto': (0, 0),  # auto detect the `submit` button
        # campus
        'east': (719, 360),  # `east campus` button
        'east_check': [(666, 360), (116, 183, 140)],
        'middle': (870, 360),
        'middle_check': [(940, 360), (116, 183, 140)],
        'west': (1014, 360),
        'west_check': [(1063, 360), (116, 183, 140)],
        'high_tech': (1146, 360),
        'high_tech_check': [(1210, 360), (116, 183, 140)],
        # date
        'today': (846, 422),
        'tomorrow': (1111, 424),
        'tomorrow_check': [(1139, 423), (116, 183, 140)],
        # notice
        'notice': (536, 1190),
        'notice_check': [(536, 1190), (12, 193, 96)],  # you are banned
        'preempted': (700, 1130),
        'preempted_check': [(700, 1130), (7, 193, 96)],
        'tip_check': [(1060, 1635), (76, 76, 76)],  # at least/most 2/6 blocks or at leat 1 companion
        # new
        'west_lt': (774, 530),  # center (x,y) of west left top block
        'east_lt': (716, 530),
        'middle_lt': (774, 530),
        'high_tech_lt': (774, 530),
    })
    main(c, (2, 1), 'middle', 'tomorrow', 12, '2030', 6, False)
    # check if network environment is normal
