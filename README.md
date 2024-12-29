# Introduction
This python script is realized by utilizing win32 API python tools. 
Essentially, it's achieved by simulation of keyboard and mouse operation
along with appropriate color recognition and image retrival methods, that is,
it's not a 100% reliable tool. Because usually it depends on how good quality
of your network environment is, how fast your computer responds to mouse or keyboard
events.

# Notice
Any user should be aware that this works only after you correctly modified the 
coordinates according to your own screen resolution and UI scaling settings. 
> I finished this script on a 4K screen with 150% scaling. 

# Requirements
- python=3.11
- pywin32=305.1
- pyautogui=0.9.54
- pywinauto=0.6.8
- pynput=1.7.7
- numpy=1.26.4
- opencv-python=4.10.0.84

# Usage
1. Confirm the resolution and scaling factor of your own screen.
2. Click the mini-program page, press the shortcut key `WIN` + `LEFT`.
3. Get the left-top coordinates of the mini-program with the following codes, i.e., (-9, 42).
```python
...

hwnd = win32gui.FindWindow(None, '中国科大体育运动场馆预约')
l, t, r, b = win32gui.GetWindowRect(hwnd)

$print(l, t)
>>> -9, 42
```
4. Modify the global var `BIAS` in the first several lines of `ustc_badminton.py`
```python
BIAS = (-9, 42)
```
5. Use screenshot tool(i.e., snipaste or pixpin) to obtain the wanted screen pixels' coordinates in codes.
```python
...

c = Coordinates({
    # point: (x_coord, y_coord)
    # point_end_with_check: [(x_coord, y_coord), (r, g, b)]
    'click_appointment': (396, 823),
    'place_intro_check': [(1208, 183), (0, 122, 51)],  # place introduction
    'companion': (731, 1344),  # default companion
    'companion_check': [(809, 1373), (2, 125, 254)],  # selected companion
    'submit_auto': (0, 0),  # auto detect the `submit` button
    'submit_test': (936, 1386),  # only used when selecting audience block
    'east': (719, 360),  # `east campus` button
    'east_check': [(666, 360), (116, 183, 140)],
    'middle': (870, 360),
    'west': (1014, 360),
    'west_check': [(1063, 360), (116, 183, 140)],
    'high_tech': (1146, 360),
    'today': (846, 422),
    'tomorrow': (1111, 424),
    'tomorrow_check': [(1139, 423), (116, 183, 140)],
    'notice': (536, 1190),
    'notice_check': [(536, 1190), (12, 193, 96)],  # you are banned
    'w1_x': (774, 748),  # the coordinate of the first time block on the left in `west` campus, only use the `x`
    'e1_x': (817, 530),  # first x on the left in `east` campus
    'tip_check': [(1065, 1760), (76, 76, 76)],  # at least 2 blocks
    'tip2_check': [(932, 1774), (73, 73, 73)],
    'bench_y': (925, 730)
})
```