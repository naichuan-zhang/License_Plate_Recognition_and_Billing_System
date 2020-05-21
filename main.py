import time

import cv2 as cv

import os

import pandas as pd

import pygame
from pygame.rect import Rect
from pygame.time import Clock

from buttons import Button
from ocrutil import get_license_plate_number
from timeutil import get_week_number, get_parking_time

import matplotlib.pyplot as plt

SIZE = (1000, 484)
FPS = 60
BG_COLOR = (73, 119, 142)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

TOTAL = 100

TXT1 = ''
TXT2 = ''
TXT3 = ''

income_switch = False

# init display module
pygame.display.init()

# init a screen to display
screen: pygame.Surface = pygame.display.set_mode(size=SIZE)

# load icon
icon: pygame.Surface = pygame.image.load(os.path.join('img', 'ic_launcher.png'))

# set background color
screen.fill(BG_COLOR)

# set clock
clock: Clock = pygame.time.Clock()

# init cv video capture
cap = cv.VideoCapture(0)

# create xlsx files to store data
dir = os.path.dirname(__file__)
path = dir + '/data/'
if not os.path.exists(path + "停车场车辆表.xlsx"):
    # create data directory
    os.makedirs(path)
    carnfile = pd.DataFrame(columns=['carnumber', 'date', 'price', 'state'])
    # generate xlsx files
    carnfile.to_excel(path + '停车场车辆表.xlsx', sheet_name='data')
    carnfile.to_excel(path + '停车场信息表.xlsx', sheet_name='data')


def recognize_license_plate() -> str:
    try:
        number = get_license_plate_number()
        print('识别成功！')
        return number
    except Exception as e:
        print('识别失败！', e)
        return ""


car_table = pd.read_excel(path + '停车场车辆表.xlsx', sheet_name='data')
car_info_table = pd.read_excel(path + '停车场信息表.xlsx', sheet_name='data')
cars = car_table[['carnumber', 'date', 'state']].values
car_number = len(cars)


def draw_header():
    _x, _y = 830, 70
    font = pygame.font.SysFont('SimHei', 20)
    text = '共有车位：' + str(TOTAL) + "   剩余车位：" + str(TOTAL - car_number)
    text_img = font.render(text, True, WHITE)
    text_rect: Rect = text_img.get_rect()
    text_rect.centerx = _x
    text_rect.centery = _y
    screen.blit(text_img, text_rect)


def draw_cars_info():
    global cars
    # only show info of the first 10 cars
    if car_number > 10:
        cars = pd.read_excel(path + '停车场车辆表.xlsx', skiprows=len(cars) - 10, sheet_name='data').values
    _x, _y = 820, 120
    font = pygame.font.SysFont('SimHei', 12)
    for car in cars:
        _y = _y + 20
        text = str(car[0]) + ' ' + str(car[1])
        text_img = font.render(text, True, WHITE)
        text_rect: Rect = text_img.get_rect()
        text_rect.centerx = _x
        text_rect.centery = _y
        screen.blit(text_img, text_rect)


def draw_history_and_warning_info(screen, txt1, txt2, txt3):
    # history
    xtfont = pygame.font.SysFont('SimHei', 15)
    texttxt1 = xtfont.render(txt1, True, GREEN)
    text_rect = texttxt1.get_rect()
    text_rect.centerx = 820
    text_rect.centery = 355 + 20
    screen.blit(texttxt1, text_rect)

    texttxt2 = xtfont.render(txt2, True, GREEN)
    text_rect = texttxt2.get_rect()
    text_rect.centerx = 820
    text_rect.centery = 355 + 40
    screen.blit(texttxt2, text_rect)

    texttxt3 = xtfont.render(txt3, True, GREEN)
    text_rect = texttxt3.get_rect()
    text_rect.centerx = 820
    text_rect.centery = 355 + 60
    screen.blit(texttxt3, text_rect)

    # warning -> state == 2
    kcar = car_info_table[car_info_table['state'] == 2]
    kcars = kcar.values
    week_number = 0
    for k in kcars:
        week_number = get_week_number(k)
    localtime = time.strftime('%Y-%m-%d %H:%M', time.localtime())
    week_localtime = get_week_number(localtime)

    if week_number == 0:
        if week_localtime == 6:
            show_warning(screen, '根据数据分析，明天可能出现车位紧张的情况，请提前做好调度！')
        elif week_localtime == 0:
            show_warning(screen, '根据数据分析，今天可能出现车位紧张的情况，请做好调度！')
    else:
        if week_localtime + 1 == week_number:
            show_warning(screen, '根据数据分析，明天可能出现车位紧张的情况，请提前做好调度！')
        elif week_localtime == week_number:
            show_warning(screen, '根据数据分析，今天可能出现车位紧张的情况，请做好调度！')


def show_warning(screen, week_info):
    pygame.draw.rect(screen, YELLOW, ((2, 2), (640, 40)))
    xtfont = pygame.font.SysFont('SimHei', 22)
    textweek_day = xtfont.render(week_info, True, RED)
    text_rectw = textweek_day.get_rect()
    text_rectw.centerx = 322
    text_rectw.centery = 20
    screen.blit(textweek_day, text_rectw)


def draw_total_income(screen):
    total_price = car_info_table['price'].sum()
    xtfont = pygame.font.SysFont('SimHei', 20)
    text_img = xtfont.render('共计收入：' + str(int(total_price)) + '元', True, WHITE)
    text_rect = text_img.get_rect()
    text_rect.centerx = 1200
    text_rect.centery = 30
    screen.blit(text_img, text_rect)
    image = pygame.image.load(os.path.join('img', 'income.png'))
    image = pygame.transform.scale(image, (390, 430))
    screen.blit(image, (1000, 50))


def generate_income_chart():
    x_labels = ['1月', '2月', '3月', '4月', '5月', '6月', '7月',
                '8月', '9月', '10月', '11月', '12月']
    values = []
    for month in range(len(x_labels)):
        k = month
        if month < 10:
            k = '0' + str(month)
        val = car_info_table[car_info_table['date'].str.contains('2019-' + str(k))]
        val = val['price'].sum()
        values.append(val)
    plt.figure(figsize=(3.9, 4.3))
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.bar(x_labels, values, width=0.5, color='green')
    plt.title('每月收入统计')
    plt.ylim((0, max(values) + 10))
    plt.savefig(os.path.join('img', 'income.png'))


running = True
while running:
    # capture frame by frame
    ret, frame = cap.read()

    cv.imwrite('img/test.jpg', frame)
    image: pygame.Surface = pygame.image.load(os.path.join('img', 'test.jpg'))
    screen.blit(image, (2, 2))

    # draw custom button
    button = Button(screen, (640, 480), 150, 60, BLUE, WHITE, "识别", 25)
    button.draw()

    # statistic button
    button_st = Button(screen, (990, 480), 100, 40, RED, WHITE, "收入统计", 18)
    button_st.draw()

    draw_header()
    draw_cars_info()
    draw_history_and_warning_info(screen, TXT1, TXT2, TXT3)

    if income_switch:
        draw_total_income(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            # print(event.pos)
            if ((button.rect.left + button.rect.width) >= event.pos[0] >= button.rect.left) \
                    and ((button.rect.top + button.rect.height) >= event.pos[1] >= button.rect.top):
                number = recognize_license_plate()
                if number is not None:
                    localtime = time.strftime('%Y-%m-%d %H:%M', time.localtime())
                    # check if the recognized plate number already exists in the file
                    carnumbers = car_table['carnumber'].values
                    if number in carnumbers:
                        # get parking time, save data into car_info_file and remove data from car_file
                        cars = car_table[['carnumber', 'date', 'state']].values
                        column = 0
                        parking_time = 0
                        for car in cars:
                            if car[0] == number:
                                start_time = car[1]
                                parking_time = get_parking_time(start_time, localtime)
                                break
                            column += 1
                        if parking_time == 0:
                            parking_time = 1
                        TXT1 = '车牌号：' + number
                        TXT2 = '停车费：' + str(3 * parking_time) + '元'
                        TXT3 = '出停车场时间：' + localtime
                        # remove data from car table
                        car_table = car_table.drop([column], axis=0)
                        # add data to info table
                        car_info_table = car_info_table.append(
                            {'carnumber': number, 'date': localtime, 'price': 3 * parking_time, 'state': 1},
                            ignore_index=True)
                        car_table.to_excel(path + '停车场车辆表' + '.xlsx',
                                           sheet_name='data', index=False, header=True)
                        car_info_table.to_excel(path + '停车场信息表' + '.xlsx',
                                                sheet_name='data', index=False, header=True)
                        car_number -= 1
                    else:
                        if car_number <= TOTAL:
                            car_table = car_table.append(
                                {'carnumber': number, 'date': localtime, 'state': 0}, ignore_index=True)
                            car_table.to_excel(path + '停车场车辆表' + '.xlsx', sheet_name='data', index=False, header=True)
                            if car_number < TOTAL:
                                # state等于0得时候为 停车场有车位进入停车场
                                car_info_table = car_info_table.append(
                                    {'carnumber': number, 'date': localtime, 'state': 0}, ignore_index=True)
                                car_number += 1
                            else:
                                # state等于2得时候为 停车场没有车位的时候
                                car_info_table = car_info_table.append(
                                    {'carnumber': number, 'date': localtime, 'state': 2}, ignore_index=True)
                                car_info_table.to_excel(path + '停车场信息表' + '.xlsx',
                                                        sheet_name='data', index=False, header=True)

                                TXT1 = '车牌号:' + number
                                TXT2 = '有空余车辆，可以进入停车场'
                                TXT3 = '进停车场时间：' + localtime
                        else:
                            # 停车位满了得时候提示信息
                            txt1 = '车牌号： ' + number
                            txt2 = '没有空余车位，不可以进入停车场'
                            txt3 = '时间：' + localtime

            if ((button_st.rect.left + button_st.rect.width) >= event.pos[0] >= button_st.rect.left) \
                    and ((button_st.rect.top + button_st.rect.height) >= event.pos[1] >= button_st.rect.top):
                if income_switch:
                    income_switch = False
                    size = 1000, 484
                    screen = pygame.display.set_mode(size)
                    screen.fill(BG_COLOR)
                else:
                    income_switch = True
                    size = 1400, 484
                    screen = pygame.display.set_mode(size)
                    screen.fill(BG_COLOR)
                    # generate chart
                    generate_income_chart()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False

    # update screen
    pygame.display.update()

    # set the max FPS
    clock.tick(FPS)

cap.release()
