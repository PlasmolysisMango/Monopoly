import pygame
import pygame.freetype
import sys
import random
import os
import pickle

# 一些常量
WHITE = pygame.Color('white')
BLACK = pygame.Color('black')
GREEN = pygame.Color('darkgreen')
RED = pygame.Color('red')
YELLOW = 255, 255, 0
PURPLE = 138, 43, 226
BLUE = 0, 0, 255
GREY = 128, 138, 135
BROWN = 244, 164, 95
LINEWIDTH = 2
FONTPATH = os.path.join('fonts', 'font.ttf')
INIT_MONEY = 1500
ADD_MONEY = 150


# 一些游戏控件类定义

# 测试用：父类Draw：
class Draw(object):
    def __init__(self, rect):
        self.rect = pygame.Rect(rect[0], rect[1], rect[2], rect[3])

    def init_Surface(self):
        surface = pygame.Surface((self.rect.w + LINEWIDTH / 2, self.rect.h + LINEWIDTH / 2))
        surface.fill(WHITE)
        pygame.draw.rect(surface, BLACK, (0, 0, self.rect.w, self.rect.h), LINEWIDTH)
        return surface


# 文字展示框类定义
class DisplayBox(object):
    def __init__(self, rect, text, size=20):
        self.box_rect = self.x, self.y, self.w, self.h = int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3])
        self.size = size
        self.margin = 0.1  # 页边距
        self.space = int(self.size / 4)
        self.text = text
        self.need_update = True
        self.font = pygame.freetype.Font(FONTPATH, size=self.size)
        self.oldsurface = None
        # 可滚动文字显示框相关
        self.rolltext_List = []
        self.last_text = ''
        self.linesNum = int((self.h * (1 - 2 * self.margin) + self.space) / (self.space + self.size))
        self.rollpos = 0
        self.mode = '居中对齐'
        self.number = 0
    
    def get_saveList(self):
        savelis = [self.text, self.rolltext_List, self.last_text, self.rollpos, self.number]
        return savelis
    
    def load_saveList(self, savelis):
        [self.text, self.rolltext_List, self.last_text, self.rollpos, self.number] = savelis
        self.need_update = True
        return True

    def get_textList(self, in_text):  # 分割字符串实现自动换行
        textList = in_text.split('\n')
        final_textList = []
        width = int(self.w * (1 - 2 * self.margin))
        for text in textList:
            templenth = 0
            tempstr = ''
            total = 0
            for char in text:
                total += 1
                if char.isupper():
                    charlen = 0.5
                elif char.islower():
                    charlen = 0.5
                elif char.isnumeric():
                    charlen = 0.5
                elif char.isspace():
                    charlen = 0.5
                else:
                    charlen = 1
                templenth += charlen
                if templenth * self.size > width:
                    final_textList.append(tempstr)
                    tempstr = ''
                    templenth = charlen
                tempstr += char
                if total == len(text):
                    final_textList.append(tempstr)

        return final_textList

    def get_inner_avilablerect(self, textList, space):
        x = int(0 + self.margin * self.w)
        h = int(len(textList) * self.size + (len(textList) - 1) * space)
        y = int((self.h - h) / 2 + 0)
        w = int(self.w * (1 - 2 * self.margin))
        return x, y, w, h

    def text_render(self, t_list, mode='居中对齐'):
        font = self.font
        textList = t_list
        surfs = []
        rects = []
        space = self.space  # 0.25倍行距
        self.avilable_rect = self.a_x, self.a_y, self.a_w, self.a_h = self.get_inner_avilablerect(textList, space)
        for i in range(len(textList)):
            text = textList[i]
            t_surf, t_rect = font.render(text, BLACK, size=self.size)
            if mode == '左对齐':
                x = int(self.a_x)
                y = int(self.a_y + (self.size + space) * i)
                w = int(t_rect.w)
                h = int(t_rect.h)
                surfs.append(t_surf)
                rects.append(pygame.Rect((x, y, w, h)))
            elif mode == '居中对齐':
                x = int(self.a_x + self.a_w / 2 - t_rect.w / 2)
                y = int(self.a_y + (self.size + space) * i)
                w = int(t_rect.w)
                h = int(t_rect.h)
                surfs.append(t_surf)
                rects.append(pygame.Rect((x, y, w, h)))
        return surfs, rects

    def update_text(self, text, mode='default'):
        if self.text != text:
            if mode == 'default':
                self.text = text
            elif mode == 'add':
                self.text += text
            self.need_update = True

    def get_Surface(self):
        if not self.oldsurface or self.need_update:
            mode = self.mode
            surface = pygame.Surface((self.w + LINEWIDTH / 2, self.h + LINEWIDTH / 2))
            surface.fill(WHITE)
            pygame.draw.rect(surface, BLACK, (0, 0, self.w, self.h), LINEWIDTH)
            if isinstance(self.text, str):
                textList = self.get_textList(self.text)
            elif isinstance(self.text, list):
                textList = self.text
            surfs, rects = self.text_render(textList, mode)
            for i in range(len(surfs)):
                surface.blit(surfs[i], (rects[i].x, rects[i].y))
            self.oldsurface = surface.copy()
            self.need_update = False
        return self.oldsurface

    def update_rect(self, rect):
        self.box_rect = self.x, self.y, self.w, self.h = int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3])
        self.need_update = True

    def get_rect(self):
        return pygame.Rect(self.box_rect)

    def add_rolltext(self, text, force_update=False):
        if not self.rolltext_List or not text == self.last_text or force_update:
            self.number += 1
            self.rolltext_List.extend(self.get_textList('【{}】{}'.format(self.number, text.replace('\n', '，'))))
            self.text = self.get_rolltext()
            self.last_text = text
            self.need_update = True

    def get_rolltext(self):
        if len(self.rolltext_List) > self.linesNum:
            nowList = self.rolltext_List[- self.linesNum:]
        else:
            nowList = self.rolltext_List
        return nowList

    def mouseroll(self, event):
        if self.rolltext_List:
            if len(self.rolltext_List) > self.linesNum:
                if event == 'UP':
                    self.rollpos -= 1
                elif event == 'DOWN':
                    self.rollpos += 1
                if self.rollpos > -1:
                    self.rollpos = 0
                    nowList = self.rolltext_List[-self.linesNum:]
                else:
                    if self.rollpos < -(len(self.rolltext_List) - self.linesNum):
                        self.rollpos = -(len(self.rolltext_List) - self.linesNum)
                    nowList = self.rolltext_List[self.rollpos - self.linesNum:self.rollpos]
            else:
                nowList = self.rolltext_List
            self.text = nowList
            self.need_update = True

# 输入框定义
class InputBox(object):
    def __init__(self, rect, info = '', mode = 'default', size = 20, color = BLACK, visible = True, lock = False):
        self.rect = self.x, self.y, self.w, self.h = rect[0], rect[1], rect[2], rect[3]
        self.info = info
        self.size = size
        self.isVisible = visible
        self.islocked = lock
        self.text = ''
        self.mode = mode
        self.need_update = True
        self.color = color
    
    def get_char(self, char):
        if self.mode == 'num': 
            if char.isnumeric():
                self.text += str(char)
                return True
            return False
        elif self.mode == 'default':
            self.text += str(char)
            return True
    
    def clear(self):
        self.text = ''
        return True
    
    def delete(self):
        if len(self.text) > 1: 
            self.text = self.text[:-1]
            return True
        else:
            self.text = ''
    
    def hide(self):
        if self.isVisible: 
            self.isVisible = False
            self.islocked = True
            self.need_update = True
    
    def show(self):
        if not self.isVisible: 
            self.isVisible = True
            self.islocked = False
            self.need_update = True

    def get_avilablerect(self):
        x = int(self.x)
        y = int(self.y)
        h = int(self.h)
        w = int(self.w)
        return pygame.Rect(x, y, w, h)

    def get_Surface(self): 
        surface = pygame.Surface((self.w + LINEWIDTH / 2, self.h + LINEWIDTH / 2))
        surface.fill(WHITE)
        if self.isVisible:
            pygame.draw.rect(surface, BLACK, [0, 0, self.w, self.h], LINEWIDTH)
            x = self.x
            y = self.y
            w = self.w
            h = self.h
            font = pygame.freetype.Font(FONTPATH, size=self.size)
            if self.text:
                t_surf, t_rect = font.render(self.text, self.color, size = self.size)
                surface.blit(t_surf, get_xypos([self.w / 2, self.h / 2], [t_rect.w, t_rect.h]))
        return surface




# 按钮类定义
class Button(object):
    def __init__(self, rect, text, size=20, visible=True, lock=False):
        self.text = text
        self.margin = 0.1
        self.size = size
        self.font = pygame.freetype.Font(FONTPATH, size=self.size)
        self.rect = self.x, self.y, self.w, self.h = rect[0], rect[1], rect[2], rect[3]
        self.avilable_rect = self.get_avilablerect()
        self.isPressed = False
        self.isPressed_right = False
        self.isWorked = False
        self.isWorked_right = False
        self.isLocked = lock
        self.need_update = True
        self.isVisible = visible
    
    def get_Surface(self, mode='居中对齐'):
        surface = pygame.Surface((self.w + LINEWIDTH / 2, self.h + LINEWIDTH / 2))
        surface.fill(WHITE)
        if self.isVisible:
            pygame.draw.rect(surface, BLACK, [0, 0, self.w, self.h], LINEWIDTH)
            x = self.avilable_rect.x - self.x
            y = self.avilable_rect.y - self.y
            w = self.avilable_rect.w
            h = self.avilable_rect.h
            if self.isPressed:
                pygame.draw.rect(surface, BLACK, [x, y, w, h], 0)
                color = WHITE
            elif self.isPressed_right: 
                pygame.draw.rect(surface, GREY, [x, y, w, h], 0)
                color = WHITE
            else:
                pygame.draw.rect(surface, BLACK, [x, y, w, h], LINEWIDTH)
                color = BLACK
            if self.isLocked:
                color = GREY
            surfs, rects = self.text_render(color)
            for i in range(len(surfs)):
                surface.blit(surfs[i], (rects[i].x, rects[i].y))
        self.need_update = False
        return surface

    def get_avilablerect(self):
        x = int(self.x + self.margin * self.h)
        y = int(self.y + self.margin * self.h)
        h = int(self.h * (1 - 2 * self.margin))
        w = int(self.w - 2 * self.margin * self.h)
        return pygame.Rect(x, y, w, h)

    def text_render(self, color):
        font = self.font
        textList = self.text.split('\n')
        surfs = []
        rects = []
        space = int(self.size * 0.25)  # 0.25倍行距
        s_y = int(self.h / 2 - (len(textList) * (self.size + space) - space) / 2)
        for i in range(len(textList)):
            text = textList[i]
            t_surf, t_rect = font.render(text, color, size = self.size)
            x = int(0 + self.w / 2 - t_rect.w / 2)
            y = int(s_y + (self.size + space) * i)
            w = int(t_rect.w)
            h = int(t_rect.h)
            surfs.append(t_surf)
            rects.append(pygame.Rect((x, y, w, h)))
        return surfs, rects


    def press_down(self):
        if self.isVisible and not self.isLocked:
            self.isPressed = True
            self.isWorked = False
            self.need_update = True
            return True
    
    def right_press_down(self):
        if self.isVisible and not self.isLocked:
            self.isPressed_right = True
            self.isWorked_right = False
            self.need_update = True
            return True

    def press_up(self):
        if self.isVisible:
            if self.isPressed:
                self.isPressed = False
                self.isWorked = True
                self.need_update = True
            elif self.isPressed_right:
                self.isPressed_right = False
                self.isWorked_right = True
                self.need_update = True
            return True

    def click(self):
        if self.isWorked:
            self.isWorked = False
            return True
        else:
            return False
    
    def click_right(self): 
        if self.isWorked_right:
            self.isWorked_right = False
            return True
        else:
            return False

    def hide(self):
        if self.isVisible == True:
            self.isVisible = False
            self.isLocked = True
            self.need_update = True
    
    def unlock(self):
        if self.isLocked:
            self.isLocked = False
            self.need_update = True
            return True
    
    def lock(self):
        if not self.isLocked:
            self.isLocked = True
            self.need_update = True
            return True

    def show(self):
        if self.isVisible == False:
            self.isVisible = True
            self.isLocked = False
            self.need_update = True

    def update_rect(self, rect):
        self.rect = self.x, self.y, self.w, self.h = int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3])
        self.need_update = True

    def update_text(self, text):
        self.text = text
        self.need_update = True


# 骰子框类定义
class Dice(object):
    def __init__(self, rect, number=2, size=40, rate=12):
        self.rect = pygame.Rect(rect)
        self.number = number
        self.size = size
        self.rollsum = 0
        self.x = self.rect.x
        self.y = self.rect.y
        self.needroll = False
        self.rolltime = 0
        self.clock = pygame.time.Clock()
        self.passedtime = 0
        self.rate = rate
        self.ratetime = 1000 / rate
        self.rollList = self.get_randomList()
        self.rolled = False
        self.oldsurface = None
        self.charge_rolled = False
        self.charge_needroll = False
        self.need_update = True
        self.isbonus = False

    def get_saveList(self):
        savelis = [self.isbonus, self.rollList, self.rollsum]
        return savelis
    
    def load_saveList(self, savelis):
        [self.isbonus, self.rollList, self.rollsum] = savelis
        self.oldsurface = None
        return True

    def get_randomList(self):
        rollList = []
        rollsum = 0
        for i in range(self.number):
            t = self.get_roll()
            rollList.append(t)
            rollsum += t
        self.rollsum = rollsum
        return rollList

    def issameList(self, lis):
        same = False
        for i in range(len(lis) - 1):
            if lis[i] == lis[i + 1]:
                same = True
            else:
                same = False
                break
        return same

    def get_roll(self):
        return random.randint(1, 6)

    def get_rollSurface(self, roll):
        rollSurface = pygame.Surface((self.size + LINEWIDTH / 2, self.size + LINEWIDTH / 2))
        rollSurface.fill(WHITE)
        pygame.draw.rect(rollSurface, BLACK, [0, 0, self.size, self.size], int(LINEWIDTH / 2))
        if roll == 'random':
            roll = self.get_roll()
        if roll == 1:
            pointList = [(int(self.size / 2), int(self.size / 2))]
        elif roll == 2:
            pointList = [(int(self.size / 3), int(self.size / 2)), (int(self.size / 3 * 2), int(self.size / 2))]
        elif roll == 3:
            pointList = [(int(self.size / 4), int(self.size / 4)), (int(self.size / 4 * 2), int(self.size / 4 * 2)),
                         (int(self.size / 4 * 3), int(self.size / 4 * 3))]
        elif roll == 4:
            pointList = [(int(self.size / 3), int(self.size / 3)), (int(self.size / 3 * 2), int(self.size / 3)),
                         (int(self.size / 3), int(self.size / 3 * 2)),
                         (int(self.size / 3 * 2), int(self.size / 3 * 2))]
        elif roll == 5:
            pointList = [(int(self.size / 3), int(self.size / 3)), (int(self.size / 3 * 2), int(self.size / 3)),
                         (int(self.size / 2), int(self.size / 2)), (int(self.size / 3), int(self.size / 3 * 2)),
                         (int(self.size / 3 * 2), int(self.size / 3 * 2))]
        elif roll == 6:
            pointList = [(int(self.size / 3), int(self.size / 4)), (int(self.size / 3 * 2), int(self.size / 4)),
                         (int(self.size / 3), int(self.size / 4 * 2)), (int(self.size / 3 * 2), int(self.size / 4 * 2)),
                         (int(self.size / 3), int(self.size / 4 * 3)), (int(self.size / 3 * 2), int(self.size / 4 * 3))]
        for point in pointList:
            pygame.draw.circle(rollSurface, BLACK, (point[0], point[1]), LINEWIDTH * 2, 0)
        return rollSurface

    def init_surface(self):
        surface = pygame.Surface((self.rect.w + LINEWIDTH / 2, self.rect.h + LINEWIDTH / 2))
        surface.fill(WHITE)
        pygame.draw.rect(surface, BLACK, [0, 0, self.rect.w, self.rect.h], LINEWIDTH)
        return surface

    def get_Surface(self):  # 类似主循环的绘图法
        if (not self.oldsurface) or self.needroll or self.charge_needroll:
            surface = self.init_surface()
            posList = []
            rollSurfaceList = []
            if self.needroll or self.charge_needroll:
                time_passed = self.clock.tick()
                self.passedtime += time_passed
                self.rolled = False
                if self.passedtime > self.ratetime:  # 骰子变化时
                    self.rolltime += 1
                    self.rollList = self.get_randomList()
                    self.passedtime = 0
                if self.rolltime > self.rate:  # 显示结果时
                    self.passedtime = 0
                    self.rolltime = 0
                    if self.charge_needroll:
                        self.charge_needroll = False
                        self.charge_rolled = True
                    else:
                        self.needroll = False
                        self.rolled = True
                        self.isbonus = self.issameList(self.rollList)

            for i in range(self.number):
                x = int(self.rect.w / (self.number + 1) * (i + 1))
                y = int(self.rect.h / 2)
                d_x = int(x - self.size / 2)
                d_y = int(y - self.size / 2)
                posList.append((d_x, d_y))
                rollList = self.rollList
                rollSurface = self.get_rollSurface(rollList[i])
                rollSurfaceList.append(rollSurface)
            for i in range(self.number):
                surface.blit(rollSurfaceList[i], posList[i])
            self.oldsurface = surface.copy()
        return self.oldsurface


# 空地类定义
class Block(object):
    def __init__(self, name, rect, isbuilding, blockprice, color, locate, number, resList):
        self.rect = eval(rect)
        self.x, self.y, self.w, self.h = self.rect[0], self.rect[1], self.rect[2], self.rect[3]
        self.locate = locate
        self.name = name
        self.owner = None
        self.number = number
        self.isbuilding = int(isbuilding)
        self.font = pygame.freetype.Font(FONTPATH, size=20)
        # 状态栏相关
        self.statusposList, self.bgrect = self.get_statuspos()
        self.flag_surf = resList[0]
        self.house_surf = resList[1]
        self.hotal_surf = resList[2]
        self.mortgage = False
        self.need_update = True
        self.houseNum = 0
        self.hotal = False
        if self.isbuilding == 1:  # 可建筑类型
            self.newbuilding_rate = 0.5
            self.blockcharge_rate = 0.2
            self.housecharge_rate = 0.5
            self.hotalcharge_rate = 3
            self.blockprice = int(blockprice) + int(random.randrange(-30, 30, 10))
            self.newbuilding_price = int(self.blockprice * self.newbuilding_rate)
            self.color = eval(color)
            self.colorname = color
        elif self.isbuilding == 2:  # 公共事业类型
            self.blockprice = int(blockprice)
            self.public_charge_rate = 8
        elif self.isbuilding == 3:  # 公共交通类型
            self.blockprice = int(blockprice)
            self.transport_charge_rate = 0.20
        elif self.isbuilding == 0:  # 事件类型
            self.blockprice = None
        # 选择相关：
        self.selected = False
        self.need_select = False
        # 存档载入时重绘：
        self.redraw = False
    
    def get_saveList(self):
        savelis = [self.mortgage, self.houseNum, self.hotal, self.blockprice, self.owner and self.owner.name or None]
        return savelis
    
    def load_saveList(self, savelis):
        [self.mortgage, self.houseNum, self.hotal, self.blockprice, self.owner] = savelis
        self.redraw = True
        self.need_update = True
        return True

    def get_centerPos(self):
        return int(self.x + self.w / 2), int(self.y + self.h / 2)

    def get_avilablerect(self):
        return pygame.Rect(self.rect)

    def get_charge(self, dice):  # 获取过路费
        charge = 0
        if self.owner and not self.owner.prison and not self.mortgage:
            if self.isbuilding == 1:
                if self.hotal:
                    charge = self.blockprice * self.hotalcharge_rate
                elif self.houseNum != 0:
                    charge = self.blockprice * self.housecharge_rate * self.houseNum
                else:
                    if self.colorname in self.owner.enable_colorList:
                        charge = 2 * self.blockcharge_rate * self.blockprice
                    else:
                        charge = self.blockcharge_rate * self.blockprice
            elif self.isbuilding == 2:
                num = len(self.owner.ownpublicList)
                if dice.charge_rolled:
                    roll = dice.rollsum
                    charge = roll * self.public_charge_rate * num
                if not charge:
                    dice.charge_needroll = True
            elif self.isbuilding == 3:
                num = len(self.owner.owntransportList)
                charge = num * self.blockprice * self.transport_charge_rate
        return int(charge)

    def get_statuspos(self):
        color_width = 50
        x = 0
        y = 0
        w = self.w
        h = self.h
        statusposList = []
        rect = ()
        if self.isbuilding:
            if self.locate == 'Left':
                rect = x, y, color_width, h
                for i in range(2):
                    s_x = int(rect[0] + rect[2] / 2)
                    s_y = int(rect[1] + rect[3] / 3 * (i + 1))
                    statusposList.append((s_x, s_y))
            elif self.locate == 'Down':
                rect = x, y + h - color_width, w, color_width
                for i in range(2):
                    s_x = int(rect[0] + rect[2] / 3 * (i + 1))
                    s_y = int(rect[1] + rect[3] / 2)
                    statusposList.append((s_x, s_y))
            elif self.locate == 'Right':
                rect = x + w - color_width, y, color_width, h
                for i in range(2):
                    s_x = int(rect[0] + rect[2] / 2)
                    s_y = int(rect[1] + rect[3] / 3 * (i + 1))
                    statusposList.append((s_x, s_y))
            elif self.locate == 'Up':
                rect = x, y, w, color_width
                for i in range(2):
                    s_x = int(rect[0] + rect[2] / 3 * (i + 1))
                    s_y = int(rect[1] + rect[3] / 2)
                    statusposList.append((s_x, s_y))
        return statusposList, rect

    def select(self):
        if not self.selected:
            self.selected = True

    def cancel(self):
        if self.selected:
            self.selected = False

    def get_Surface(self, width=100):
        screen = pygame.Surface((self.w, self.h)).convert_alpha()
        screen.fill((0, 0, 0, 0))
        if self.isbuilding:
            if self.redraw: # 载入时重绘
                p_surf, p_rect = self.font.render('价格：' + str(self.blockprice) + '元', BLACK, size=15)
                p_bgd = pygame.Surface((p_rect.w, p_rect.h))
                p_bgd.fill((WHITE))
                screen.blit(p_bgd, (self.w / 2 - p_rect.w / 2, self.h / 2 - p_rect.h / 2 + self.h / 5))
                screen.blit(p_surf, (self.w / 2 - p_rect.w / 2, self.h / 2 - p_rect.h / 2 + self.h / 5))
            statusposList = self.statusposList
            bgrect = self.bgrect
            x0 = statusposList[0][0]
            y0 = statusposList[0][1]
            x1 = statusposList[1][0]
            y1 = statusposList[1][1]
            background = pygame.Surface((bgrect[2] - 5, bgrect[3] - 5))
            background.fill(WHITE)
            screen.blit(background, (bgrect[0] + 5, bgrect[1] + 5))
            font = self.font
            if self.owner:
                icon = pygame.transform.scale(self.owner.icon, (15, 15))  # 第一个位置绘制旗子和头像
                flag = pygame.transform.scale(self.flag_surf, (40, 40))
                flag.blit(icon, (8, 6))
                screen.blit(flag, get_xypos((x0, y0), flag.get_rect()))
                if self.mortgage:  # 第二个位置绘制抵押、房子或者旅馆
                    bank_surf, bank_rect = font.render('抵押', RED)
                    pygame.draw.circle(screen, RED, (x1, y1), 20, 1)
                    screen.blit(bank_surf, get_xypos((x1, y1), bank_rect))
                elif self.isbuilding == 1:
                    if self.houseNum:
                        house = pygame.transform.scale(self.house_surf, (40, 40))
                        num_surf, num_rect = font.render(str(self.houseNum), BLACK, size=15)
                        house.blit(num_surf, get_xypos((20, 35), num_rect))
                        screen.blit(house, get_xypos((x1, y1), house.get_rect()))
                    elif self.hotal:
                        hotal = pygame.transform.scale(self.hotal_surf, (40, 40))
                        screen.blit(hotal, get_xypos((x1, y1), hotal.get_rect()))
        if self.selected:
            mark = pygame.Surface((self.w, self.h)).convert_alpha()
            pygame.draw.rect(mark, (0, 0, 0, 120), [0, 0, self.w, self.h], 0) # draw方法并不会绘制透明度，只是将对应像素点的透明度改变
            screen.blit(mark, (0, 0)) # 故此处用mark层进行透明度绘制，若直接在surface层绘制会导致被覆盖
        elif self.need_select:
            pygame.draw.rect(screen, (0, 255, 0), [0, 0, self.w, self.h], LINEWIDTH * 3)
        else:
            self.need_update = False
        return screen


# 玩家类定义
class Player(object):
    def __init__(self, name, icon, block, direction, building_list, disrate=0.25):
        self.name = name
        self.money = INIT_MONEY
        self.icon = icon
        self.rect = icon.get_rect()
        self.direction = direction
        self.fixsign = self.get_distocenter()
        self.disrate = disrate
        self.position = self.x, self.y = self.get_position(block)
        self.i_position = self.i_x, self.i_y = self.x, self.y
        # jump方法所需要的一些属性
        self.clock = pygame.time.Clock()
        self.needjump = False
        self.speed = None
        self.jumptime = 0
        # 自身一些可能变动的属性
        self.block = block
        # move方法所需要的一些属性
        self.needmove = False
        self.speed_x = None
        self.speed_y = None
        self.dice = None
        self.building_list = building_list
        self.moved_time = 0
        self.time_passed = 0
        self.readytomove = False
        self.thoughstart = False
        # 游戏中存储的一些列表
        self.ownblockList = []
        self.ownbuildingsList = []
        self.allcolorDict = []
        self.enable_colorList = []
        self.enable_blockList = []
        self.enable_mortgageList = []
        self.enable_dealList = []
        self.enable_buybackList = []
        self.ownpublicList = []
        self.owntransportList = []
        # 游戏中需要初始化的一些属性
        self.need_pay = False
        self.operate = False
        self.bonus_count = 0
        # 其他属性
        self.need_update = True
        self.need_select = False
        self.selected = False
        self.bankrupted = False
        self.prison = 0
        self.prison_passport = 0
        self.skill_point = 1
        self.blessing = []
        self.move_sign = False
    
    def get_saveList(self):
        ownblock_numList = []
        owntransport_numList = []
        ownpublic_numList = []
        for each in self.ownblockList + self.ownpublicList + self.owntransportList:
            if each.isbuilding == 1:
                ownblock_numList.append(each.number)
            elif each.isbuilding == 2:
                ownpublic_numList.append(each.number)
            elif each.isbuilding == 3:
                owntransport_numList.append(each.number)
        savelis = [self.name, self.money, self.direction, self.fixsign, self.position, self.i_position, self.block.number, ownblock_numList
                    , ownpublic_numList, owntransport_numList, self.bonus_count, self.bankrupted, self.prison, self.prison_passport
                    , self.skill_point, self.blessing, self.x, self.y, self.i_x, self.i_y]
        return savelis
    
    def load_saveList(self, savelis):
        if savelis[0] == self.name:
            [self.name, self.money, self.direction, self.fixsign, self.position, self.i_position, number, ownblock_numList
            , ownpublic_numList, owntransport_numList, self.bonus_count, self.bankrupted, self.prison, self.prison_passport
            , self.skill_point, self.blessing, self.x, self.y, self.i_x, self.i_y] = savelis
            self.block = self.building_list[number]
            for each in ownblock_numList + ownpublic_numList + owntransport_numList:
                if self.building_list[each].isbuilding == 1:
                    self.ownblockList.append(self.building_list[each])
                elif self.building_list[each].isbuilding == 2:
                    self.ownpublicList.append(self.building_list[each])
                elif self.building_list[each].isbuilding == 3:
                    self.owntransportList.append(self.building_list[each])
            self.update()
            return True
        else:
            return False
        

    def get_position(self, block):
        c_x, c_y = block.get_centerPos()
        x = int(c_x + self.fixsign[0] * block.w * self.disrate - self.rect.w / 2)
        y = int(c_y + self.fixsign[1] * block.h * self.disrate - self.rect.h / 2)
        return x, y

    def get_distocenter(self):
        if self.direction == 0:
            sign_x = -1
            sign_y = -1
        elif self.direction == 1:
            sign_x = 1
            sign_y = -1
        elif self.direction == 2:
            sign_x = 1
            sign_y = 1
        elif self.direction == 3:
            sign_x = -1
            sign_y = 1
        return sign_x, sign_y

    def get_Surface(self, x=0, y=0):
        if self.needjump:
            self.jump()
        elif self.needmove and self.dice:
            if self.time_passed < 200:
                self.time_passed += self.clock.tick()
            else:
                self.readytomove = True
            if self.readytomove:
                self.move_to_block()
        else:
            self.position = self.x, self.y = self.i_x, self.i_y
            self.jumptime = 0
            self.moved_time = 0
            self.clock = pygame.time.Clock()
            if self.selected:
                surface = self.icon.copy()
                color = RED
                pygame.draw.rect(surface, color, [0, 0, self.rect.w, self.rect.h], LINEWIDTH)
                return surface
            if self.prison:
                surface = self.icon.copy()
                r = int(self.rect.w / 2)
                x = int(0.7071 * r)
                pygame.draw.circle(surface, RED, [r, r], r, LINEWIDTH)
                pygame.draw.line(surface, RED, [r - x, r - x], [r + x, r + x], LINEWIDTH)
                return surface
        return self.icon

    def sign(self, num):
        if num != 0:
            return int(num / abs(num))
        else:
            return 0
    
    def get_avilablerect(self):
        x = self.x
        y = self.y
        w = self.rect.w
        h = self.rect.h
        return pygame.Rect([x, y, w, h])

    def move(self, dstblock, move_time=0.37, speed=800, max_distence=500):  # 跳棋时间以及纵向最大移动距离
        dstpos = d_x, d_y = self.get_position(dstblock)
        dis_w = d_x - self.i_x
        dis_h = d_y - self.i_y
        sign_w = self.sign(dis_w)
        sign_h = self.sign(dis_h)
        time_passed = self.clock.tick()
        time_second = time_passed / 1000.0
        accelerate = speed / move_time * 2
        if not self.speed_x and not self.speed_y:
            self.speed_x = dis_w / move_time + speed * sign_h
            self.speed_y = dis_h / move_time - speed * sign_w
        self.speed_x -= accelerate * time_second * sign_h
        self.speed_y += accelerate * time_second * sign_w
        moved_x = time_second * self.speed_x
        moved_y = time_second * self.speed_y
        self.x += moved_x
        self.y += moved_y
        if self.x * sign_h - self.y * sign_w < self.i_x * sign_h - self.i_y * sign_w:
            self.block = dstblock
            if dstblock == self.building_list[0]:
                self.money += ADD_MONEY
                self.skill_point += 1
                self.thoughstart = True
            self.position = self.x, self.y = self.i_x, self.i_y = self.get_position(dstblock)
            self.moved_time += 1
            self.speed_x = None
            self.speed_y = None

    def move_to_block(self):
        building_list = self.building_list
        begin_index = building_list.index(self.block)
        if begin_index == len(building_list) - 1:
            self.move(building_list[0])
        else:
            self.move(building_list[begin_index + 1])
        if self.moved_time == self.dice:
            self.needmove = False
            self.dice = None
            self.readytomove = False
            self.time_passed = 0

    def jump(self, speed=400, max_distence=60, move_time=2):  # 弹跳动画
        if self.needjump:
            time_passed = self.clock.tick()
            time_second = time_passed / 1000.0
            if not self.speed:
                self.speed = speed
            accelerate = 100
            self.speed -= time_second * accelerate
            distence_moved = time_second * self.speed
            if self.y - distence_moved > self.i_y:  # 向下触界限
                self.speed = -self.speed
                self.y += distence_moved
                self.jumptime += 1
            elif self.y - distence_moved < self.i_y - max_distence:  # 向上触界限
                self.speed = -self.speed
                self.y += distence_moved
            else:  # 其余情况
                self.y -= distence_moved
            if self.jumptime == move_time:  # 停止弹跳
                self.position = self.x, self.y = self.i_x, self.i_y = self.get_position(self.block)
                self.needjump = False
                self.needmove = True
                self.speed = None

    def change_pos(self, targetblock):
        self.position = self.x, self.y = self.i_x, self.i_y = self.get_position(targetblock)
        self.block = targetblock
        self.init()

    # 下面是一些游戏方法：
    def select(self):
        if not self.selected:
            self.selected = True

    def cancel(self):
        if self.selected:
            self.selected = False

    def buy_Block(self, targetblock):  # 购买空地
        if targetblock.isbuilding in range(1, 4):
            if not targetblock.owner:
                blockprice = targetblock.blockprice
                for blessing in self.blessing:
                    if '买地' in blessing:
                        if '增加' in blessing:
                            blockprice = int(targetblock.blockprice * 1.5)
                        elif '减少' in blessing:
                            blockprice = int(targetblock.blockprice * 0.5)
                        self.blessing.remove(blessing)
                        break
                if self.money > blockprice:
                    self.money -= blockprice
                    targetblock.owner = self
                    if targetblock.isbuilding == 1:
                        self.ownblockList.append(targetblock)
                    if targetblock.isbuilding == 2:
                        self.ownpublicList.append(targetblock)
                    elif targetblock.isbuilding == 3:
                        self.owntransportList.append(targetblock)
                    message = '玩家：{}\n花费{}元\n购买{}成功！'.format(self.name, blockprice, targetblock.name)
                    self.update()
                    targetblock.need_update = True
                else:
                    message = '玩家：{}\n金钱不足\n购买失败！'.format(self.name)
            else:
                message = '名地有主\n购买失败！'
        else:
            message = '不可购买\n购买失败！'
        return message

    def count_block_color(self, mode='self', list = None):
        colorDict = {}
        if mode == 'self':
            blockList = self.ownblockList
        elif mode == 'all':
            blockList = self.building_list
        elif mode == 'in':
            blockList = list
        for block in blockList:
            if block.isbuilding == 1:
                if not block.colorname in colorDict.keys():
                    colorDict[block.colorname] = 1
                else:
                    colorDict[block.colorname] += 1
        return colorDict

    def update(self):
        self.enable_blockList.clear()
        self.enable_colorList.clear()
        self.enable_dealList.clear()
        self.enable_mortgageList.clear()
        self.enable_buybackList.clear()
        self.ownbuildingsList.clear()
        for block in self.building_list: 
            if block.owner == self:
                self.ownbuildingsList.append(block)
            if block.mortgage and block.owner == self: 
                self.enable_buybackList.append(block)
        if not self.allcolorDict:
            self.allcolorDict = self.count_block_color('all')
        owncolorDict = self.count_block_color('self')
        for color in owncolorDict.keys():
            if owncolorDict[color] == self.allcolorDict[color]:
                if not color in self.enable_colorList:
                    self.enable_colorList.append(color)
                max_buildnum = 0
                for block in self.ownblockList:
                    if block.colorname == color:
                        num = block.hotal and 5 or block.houseNum
                        if num > max_buildnum:
                            max_buildnum = num
                sameList = []
                same = True
                for block in self.ownblockList:
                    if block.colorname == color:
                        num = block.hotal and 5 or block.houseNum
                        if num < max_buildnum:
                            sameList.clear()
                            self.enable_blockList.append(block)
                            same = False
                        elif num == max_buildnum and same and not block.hotal:
                            sameList.append(block)
                        if num == max_buildnum:
                            self.enable_mortgageList.append(block)
                if sameList:
                    self.enable_blockList.extend(sameList)
                    if not sameList[0].houseNum and not sameList[0].hotal:
                        self.enable_dealList.extend(sameList)
            elif owncolorDict[color] < self.allcolorDict[color]:
                for block in self.ownblockList:
                    if block.colorname == color:
                        self.enable_mortgageList.append(block)
                        self.enable_dealList.append(block)
        for block in self.ownpublicList + self.owntransportList: 
            if not block.mortgage: 
                self.enable_mortgageList.append(block)
                self.enable_dealList.append(block)

    def construct_house(self, targetblock):  # 建造房屋
        if targetblock.isbuilding == 1:
            if targetblock.colorname in self.enable_colorList:
                newbuilding_price = targetblock.newbuilding_price
                for blessing in self.blessing:
                    if '加盖' in blessing:
                        if '增加' in blessing:
                            newbuilding_price = int(targetblock.newbuilding_price * 1.5)
                        elif '减少' in blessing:
                            newbuilding_price = int(targetblock.newbuilding_price * 0.5)
                        break
                if self.money >= newbuilding_price:
                    if targetblock.houseNum < 4 and not targetblock.hotal:
                        targetblock.houseNum += 1
                        self.money -= newbuilding_price
                        message = '建造房屋成功！'
                        self.update()
                        self.need_update = True
                        if not targetblock in self.enable_blockList:
                            targetblock.need_select = False
                    elif not targetblock.hotal:
                        targetblock.hotal = True
                        targetblock.houseNum = 0
                        message = '建造旅馆成功！'
                        self.money -= newbuilding_price
                        self.need_update = True
                        self.update()
                        if not targetblock in self.enable_blockList:
                            targetblock.need_select = False
                    else:
                        message = ''
                else:
                    message = '金钱不足，无法建造！'
            else:
                message = '未拥有所有该颜色土地，不可建造！'
        else:
            message = '该土地不可建造！'
        return message
    
    def buyback(self, targetblock):
        if targetblock in self.enable_buybackList: 
            if self.money > int(targetblock.blockprice * 0.6): 
                self.money -= int(targetblock.blockprice * 0.6)
                targetblock.mortgage = False
                targetblock.need_select = False
                self.ownblockList.append(targetblock)
                self.update()
                return True
            else:
                return False
            
    def sell(self, targetblock, mode='default'):
        if targetblock.isbuilding == 1 and not targetblock.mortgage:
            construct = 0
            sell = 0
            if targetblock.hotal == True:
                construct = 5
            elif targetblock.houseNum != 0:
                construct = targetblock.houseNum
            if mode == 'all':
                sell = (targetblock.blockprice + construct * targetblock.newbuilding_price) * 0.5
                self.ownblockList.remove(targetblock)
                targetblock.need_select = False
                targetblock.hotal = False
                targetblock.houseNum = 0
                targetblock.mortgage = True
            elif mode == 'buildings':
                sell = (construct * targetblock.newbuilding_price) * 0.5
                targetblock.hotal = False
                targetblock.houseNum = 0
                targetblock.need_select = False
            elif mode == 'default':
                if targetblock.houseNum or targetblock.hotal:
                    sell = (targetblock.newbuilding_price) * 0.5
                    if targetblock.hotal:
                        targetblock.hotal = False
                    else:
                        targetblock.houseNum -= 1
                    targetblock.need_select = False
                else:
                    sell = targetblock.blockprice * 0.5
                    self.ownblockList.remove(targetblock)
                    targetblock.need_select = False
                    targetblock.mortgage = True
        elif targetblock.isbuilding in range(2, 4) and not targetblock.mortgage:
            sell = targetblock.blockprice * 0.5
            targetblock.isbuilding == 2 and self.ownpublicList.append(targetblock) or self.owntransportList.append(targetblock)
            targetblock.need_select = False
            targetblock.mortgage = True
        for blessing in self.blessing:
            if '抵押' in blessing:
                if '增加' in blessing:
                    sell = int(sell * 1.5)
                elif '减少' in blessing:
                    sell = int(sell * 0.5)
                break
        self.money += int(sell)
        self.update()
        return sell

    def deal(self, targetblock, targetplayer): 
        if targetblock.owner == self:
            if targetblock.isbuilding == 1 and not targetblock.houseNum and not targetblock.hotal:
                self.ownblockList.remove(targetblock)
                targetblock.owner = targetplayer
                targetblock.need_select = False
                targetplayer.ownblockList.append(targetblock)
            elif targetblock.isbuilding == 2: 
                self.ownpublicList.remove(targetblock)
                targetblock.owner = targetplayer
                targetblock.need_select = False
                targetplayer.ownpublicList.append(targetblock)
            elif targetblock.isbuilding == 3: 
                self.owntransportList.remove(targetblock)
                targetblock.owner = targetplayer
                targetblock.need_select = False
                targetplayer.owntransportList.append(targetblock)
            self.update()
            targetplayer.update()
            return True
        return False
                

    def init(self):  # 一次使用的判断性语句
        self.need_pay = True
        self.operate = False
        self.move_sign = True

    def pay(self, price, dice, owner):
        message = ''
        if self.need_pay:
            for blessing in self.blessing:
                if '过路' in blessing:
                    if '增加' in blessing:
                        price = int(price * 1.5)
                    elif '减少' in blessing:
                        price = int(price * 0.5)
                    self.blessing.remove(blessing)
                    break
            if price <= self.money:
                self.money -= price
                owner.money += price
                message = '{}支付{}元'.format(dice.charge_rolled and '掷出{}点，'.format(dice.rollsum) or '', price)
                self.need_pay = False
            else:
                message = '需要支付{}元，金钱不足，濒临破产！'.format(price)
        return message
    
    def asset_statistics(self):
        sum = 0
        for block in self.ownblockList:
            num = block.hotal and 5 or block.houseNum
            sum += block.blockprice + block.newbuilding_price * num
        for block in self.ownpublicList + self.owntransportList:
            sum += block.blockprice
        return int(sum * 0.5) + self.money
    
class SpecialEvent(object):
    def __init__(self, building_list, PlayerList, active_player):
        self.building_list = building_list
        self.PlayerList = PlayerList
        self.active_player = active_player
    
    def chance(self, mode = 'random'):
        operate = True
        if self.active_player.enable_blockList:
            build = 3
        else: 
            build = 1
        if self.active_player.enable_mortgageList:
            mortgage = 3
            loseblock = 2
        else:
            mortgage = 1
            loseblock = 1
        if self.active_player.ownblockList or self.active_player.ownpublicList or self.active_player.owntransportList:
            tax = 4
        else:
            tax = 2
        if len(self.active_player.ownbuildingsList) < 3 and loseblock > 1:
            loseblock -= 1
        elif len(self.active_player.ownbuildingsList) > 6:
            loseblock += 2

        if mode == 'random':
            mode = random.choices(range(1,15), [5, 5, tax, tax, build, mortgage, 1, 1, 2, loseblock, 3, 3, 2, 2])[0]

        if mode == 1: # 随机获得金钱事件 
            money = random.randint(1, 4) * 50
            message = '玩家：{}抽中大奖，获得{}元'.format(self.active_player.name, money)
            self.active_player.money += money

        if mode == 2: # 随机失去金钱事件
            money = random.randint(1, 4) * 50
            message = '玩家：{}出门掉坑，支付医药费{}元'.format(self.active_player.name, money)
            if self.active_player.money < money:
                self.active_player.bankrupted = True
                return [money, message]
            self.active_player.money -= money

        if mode == 3: # 随机退税事件
            money = int((self.active_player.asset_statistics() - self.active_player.money) * 0.1)
            message = '玩家：{}被免除地产税，得到{}元'.format(self.active_player.name, money)
            self.active_player.money += money

        if mode == 4: # 随机收税事件
            money = int((self.active_player.asset_statistics() - self.active_player.money) * 0.1)
            message = '玩家：{}被征收地产税，支付{}元'.format(self.active_player.name, money)
            if self.active_player.money < money:
                self.active_player.bankrupted = True
                return [money, message]
            self.active_player.money -= money

        if mode == 5: # 随机加盖事件
            if self.active_player.enable_blockList:
                block = random.choice(self.active_player.enable_blockList)
                if block.houseNum == 4:
                    block.hotal = True
                    block.houseNum = 0
                else:
                    block.houseNum += 1
                message = '玩家：{}邂逅富婆，{}加盖一层'.format(self.active_player.name, block.name)
                block.need_update = True
                self.active_player.update()
            else:
                message = '玩家：{}邂逅富婆，惨遭嫌弃'.format(self.active_player.name)
            
        if mode == 6: # 随机拆房事件
            if self.active_player.enable_mortgageList:
                block = random.choice(self.active_player.enable_mortgageList)
                if block.isbuilding == 1:
                    if block.hotal:
                        block.hotal = False
                        block.houseNum = 4
                    elif block.houseNum:
                        block.houseNum -= 1
                    else:
                        block.mortgage = True
                        self.active_player.ownblockList.remove(block)
                elif block.isbuilding == 2:
                    block.mortgage = True
                    self.active_player.ownpublicList.remove(block)
                elif block.isbuilding == 3:
                    block.mortgage = True
                    self.active_player.owntransportList.remove(block)
                block.need_update = True
                self.active_player.update()
                message = '玩家：{}遇到拆迁队，{}抵押一次'.format(self.active_player.name, block.name)
            else:
                message = '玩家：{}遇到拆迁队，所幸并没有地'.format(self.active_player.name)
            
        if mode == 7: # 全体加盖事件
            for player in self.PlayerList:
                for block in player.enable_blockList:
                    if block.houseNum == 4:
                        block.hotal = True
                        block.houseNum = 0
                    else:
                        block.houseNum += 1
                    block.need_update = True
                player.update()
            message = '全市大基建，所有玩家全体加盖一层'

        if mode == 8: # 全体拆迁事件
            for player in self.PlayerList:
                for block in player.enable_mortgageList:
                    if block.hotal:
                        block.hotal = False
                        block.houseNum = 4
                    elif block.houseNum:
                        block.houseNum -= 1
                    else:
                        block.mortgage = True
                        player.ownblockList.remove(block)
                    block.need_update = True
                player.update()
            message = '全市大拆迁，所有玩家全体抵押一次'

        if mode == 9: # 随机获得地皮事件
            blis = []
            for block in self.building_list:
                if not block.owner and block.isbuilding:
                    blis.append(block)
            if blis:
                block = random.choice(blis)
                block.owner = self.active_player
                if block.isbuilding == 1:
                    self.active_player.ownblockList.append(block)
                if block.isbuilding == 2:
                    self.active_player.ownpublicList.append(block)
                elif block.isbuilding == 3:
                    self.active_player.owntransportList.append(block)
                block.need_update = True
                self.active_player.update()
                message = '玩家：{}结识阔少，获赠{}'.format(self.active_player.name, block.name)
            else:
                message = '玩家：{}结识阔少，可惜地已经被买光了'.format(self.active_player.name)

        if mode == 10: # 随机失去地皮事件
            blis = []
            for block in self.active_player.enable_mortgageList:
                if not block.houseNum and not block.hotal:
                    blis.append(block)
            if blis:
                block = random.choice(blis)
                block.owner = None
                if block.isbuilding == 1:
                    self.active_player.ownblockList.remove(block)
                if block.isbuilding == 2:
                    self.active_player.ownpublicList.remove(block)
                elif block.isbuilding == 3:
                    self.active_player.owntransportList.remove(block)
                block.need_update = True
                self.active_player.update()
                message = '玩家：{}遭遇恶霸，失去{}'.format(self.active_player.name, block.name)
            else:
                message = '玩家：{}遭遇恶霸，所幸什么也没有发生'.format(self.active_player.name)

        if mode == 11: # 随机慈善事件
            money = random.randint(1, 3) * 60
            message = '玩家：{}善心大发，支付{}元分给其他所有玩家'.format(self.active_player.name, money)
            if self.active_player.money < money:
                self.active_player.bankrupted = True
                return [money, message]
            self.active_player.money -= money
            for player in self.PlayerList:
                if player != self.active_player: 
                    player.money += int(money / (len(self.PlayerList) - 1))
                    
        if mode == 12: # 监狱通行证
            message = '玩家：{}行侠仗义，得到监狱通行证一张'.format(self.active_player.name)
            self.active_player.prison_passport += 1

        if mode == 13: # 监狱一日游
            message = '玩家：{}无恶不作，奖励监狱一日游'.format(self.active_player.name)
            dstblock = None
            for block in self.building_list:
                if block.name == '监狱':
                    dstblock = block
                    break
            self.active_player.change_pos(dstblock)
            operate = False

        if mode == 14: # 随机传送
            dstblock = random.choice(self.building_list)
            message = '玩家：{}进入任意门，被传送至{}'.format(self.active_player.name, dstblock.name)
            self.active_player.change_pos(dstblock)
            operate = False

        if operate:
            self.active_player.operate = True
        return message

    def blessing(self):
        blessing = random.choices(['买地', '过路', '抵押', '加盖'], [2, 2, 1, 1])[0]
        sign = random.choice(['增加', '减少'])
        message = blessing + '费用' + sign + '50%'
        add = True
        for single_bless in self.active_player.blessing:
            if blessing in single_bless:
                single_bless = message
                add = False
                break
        if add:
            self.active_player.blessing.append(message)
        self.active_player.operate = True
        return message


    def skill(self):
        self.active_player.skill_point += 2
        self.active_player.operate = True

        


# //各类函数
# 读取空地信息
def readBuildings(resList):
    buildings = []
    with open('buildings.config', 'r', encoding='utf-8') as f:
        for line in f:
            list = line.strip().split('|')
            name = list[1]
            rect = list[2]
            isbuilding = list[3]
            price = list[4]
            color = list[5]
            locate = list[6]
            block = Block(name, rect, isbuilding, price, color, locate, len(buildings), resList)
            buildings.append(block)
    return buildings


# 读取头像信息
def readIcons(width=40, height=40):
    iconDict = {}
    nameList = ['当麻', '黑子', '初春', '婚后', '警策', '美琴', '食蜂', '泪子', '削板']
    for name in nameList:
        surf = pygame.image.load(os.path.join('pics', 'icons', name + '.png')).convert_alpha()
        iconDict[name] = pygame.transform.scale(surf, (width, height))
    return iconDict


# 已知中心坐标求左上坐标：
def get_xypos(center, rect=0):
    if not type(center) == pygame.Surface:
        c_x = center[0]
        c_y = center[1]
        if type(rect) == pygame.Rect:
            c_w = rect.w
            c_h = rect.h
        else:
            c_w = rect[0]
            c_h = rect[1]
    else:
        rect = center.get_rect()
        c_x = rect.x
        c_y = rect.y
        c_w = rect.w
        c_h = rect.h
    x = int(c_x - c_w / 2)
    y = int(c_y - c_h / 2)
    return x, y


# 主函数
def main():
    pygame.init()
    size = width, height = 1600, 900
    background = pygame.display.set_mode((width, height))
    screen = pygame.Surface((width + LINEWIDTH, height + LINEWIDTH))
    icon = pygame.image.load(os.path.join('pics', 'icon.png'))
    font = pygame.freetype.Font(FONTPATH, 20)
    pygame.display.set_caption("Monopoly by PlasmolysisMango")
    pygame.display.set_icon(icon)
    # 读取图像
    FLAG = pygame.image.load(os.path.join('pics', 'res', 'flag.png')).convert_alpha()
    HOUSE = pygame.image.load(os.path.join('pics', 'res', 'house.png')).convert_alpha()
    HOTAL = pygame.image.load(os.path.join('pics', 'res', 'hotal.png')).convert_alpha()
    icon_width = 40
    iconDict = readIcons(icon_width, icon_width)

    # 底图绘图部分
    screen.fill(WHITE)
    line_width = 2

    # 建筑绘制
    building_list = readBuildings([FLAG, HOUSE, HOTAL])  # 读取并实例化所有建筑
    for i in building_list:
        line_width = 2
        x = i.rect[0]
        y = i.rect[1]
        w = i.rect[2]
        h = i.rect[3]
        color_width = 40
        if (i.isbuilding == 1 and i.locate == 'Left'):
            pygame.draw.rect(screen, i.color, [x + w - color_width, y, color_width, h], 0)
            pygame.draw.line(screen, BLACK, (x + w - color_width, y), (x + w - color_width, y + h), line_width)
        if (i.isbuilding == 1 and i.locate == 'Down'):
            pygame.draw.rect(screen, i.color, [x, y, w, color_width], 0)
            pygame.draw.line(screen, BLACK, (x, y + color_width), (x + w, y + color_width), line_width)
        if (i.isbuilding == 1 and i.locate == 'Right'):
            pygame.draw.rect(screen, i.color, [x, y, color_width, h], 0)
            pygame.draw.line(screen, BLACK, (x + color_width, y), (x + color_width, y + h), line_width)
        if (i.isbuilding == 1 and i.locate == 'Up'):
            pygame.draw.rect(screen, i.color, [x, y + h - color_width, w, color_width], 0)
            pygame.draw.line(screen, BLACK, (x, y + h - color_width), (x + w, y + h - color_width), line_width)
        if (i.name == '起点'):
            pygame.draw.rect(screen, BROWN, [x, y, w, h], 0)
        pygame.draw.line(screen, BLACK, (x, y), (x + w, y), line_width)
        pygame.draw.line(screen, BLACK, (x, y), (x, y + h), line_width)
        pygame.draw.line(screen, BLACK, (x + w, y), (x + w, y + h), line_width)
        pygame.draw.line(screen, BLACK, (x, y + h), (x + w, y + h), line_width)

        # 显示相关信息
        f_surf, f_rect = font.render(i.name, BLACK, size=20)
        if i.isbuilding != 0:
            p_surf, p_rect = font.render('价格：' + str(i.blockprice) + '元', BLACK, size=15)
            screen.blit(p_surf, (x + w / 2 - p_rect.w / 2, y + h / 2 - p_rect.h / 2 + h / 5))
        screen.blit(f_surf, (x + w / 2 - f_rect.w / 2, y + h / 2 - f_rect.h / 2))

    # 上边框粗细问题修复
    pygame.draw.line(screen, BLACK, (0, 0), (width, 0), int(line_width * 2))
    pygame.draw.line(screen, BLACK, (0, 0), (0, height), int(line_width))
    pygame.draw.line(screen, BLACK, (width, height), (width, 0), int(line_width))
    pygame.draw.line(screen, BLACK, (width, height), (0, height), int(line_width))

    INIT_SCREEN = screen.copy()  # 对象赋值会跟着变，必须使用copy方法

    # 播放音乐部分
    pygame.mixer.music.load(os.path.join('music', 'background.mp3'))
    pygame.mixer.music.set_volume(0.05)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.pause()

    # 玩家实例化：
    PlayerList = []
    startPos = start_x, start_y = building_list[0].get_centerPos()
    player_disx = int(building_list[0].w * 0.2)
    player_disy = int(building_list[0].h * 0.2)
    player1 = Player('黑子', iconDict['黑子'], building_list[0], 0, building_list)
    player2 = Player('泪子', iconDict['泪子'], building_list[0], 1, building_list)
    player3 = Player('食蜂', iconDict['食蜂'], building_list[0], 2, building_list)
    player4 = Player('警策', iconDict['警策'], building_list[0], 3, building_list)
    PlayerList.extend([player1, player2, player3, player4])
    random.shuffle(PlayerList)
    RAW_PlayerList = PlayerList.copy()
    active_player = PlayerList[0]

    # 测试用
    player1.money = 50000
    for block in building_list:
        if block.isbuilding and block.number != 1:
            player1.buy_Block(block)
            block.hotal = True
    player2.money = 450
    player2.buy_Block(building_list[1])
    # player2.prison = 1
    # player3.prison = 1
    player3.money = 5
    player4.money = 5
    # for player in PlayerList:
    #     player.skill_point = 40

    # //各类控件：
    # 文字显示框实例化：
    DisplayBoxList = []
    moneybox = DisplayBox([700, 250, 200, 100], 'moneybox')
    message_init = '适度游戏益脑，沉迷游戏伤身。\n合理安排时间，享受健康生活。'
    event_init = '抵制不良游戏，拒绝盗版游戏。\n注意自我保护，谨防受骗上当。'
    messagebox = DisplayBox([950, 250, 400, 400], message_init)
    eventbox = DisplayBox([250, 250, 400, 400], event_init)
    DisplayBoxList.extend([moneybox, messagebox, eventbox])

    # 按钮实例化：
    ButtonList = []
    dice_button = Button([700, 550, 200, 100], '点我开始！')
    button1 = Button([320, 517, 100, 50], 'button1', size=17, visible=False, lock=True)
    button2 = Button([480, 517, 100, 50], 'button2', size=17, visible=False, lock=True)
    button3 = Button([320, 583, 100, 50], 'button3', size=17, visible=False, lock=True)
    button4 = Button([480, 583, 100, 50], 'button4', size=17, visible=False, lock=True)
    ButtonList.extend([dice_button, button1, button2, button3, button4])

    # 骰子实例化：
    DiceList = []
    dice = Dice([700, 410, 200, 80])
    DiceList.append(dice)

    # 游戏开始界面
    isStart = False
    startbutton = Button([700, 400, 200, 100], '开始游戏')
    while not isStart:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if startbutton.get_avilablerect().collidepoint(event.pos):
                    startbutton.press_down()
            if event.type == pygame.MOUSEBUTTONUP:
                startbutton.press_up()
        if startbutton.click():
            isStart = True
        # 画面更新部分
        screen = INIT_SCREEN.copy()  # 对象赋值会跟着变，必须使用copy方法
        screen.blit(startbutton.get_Surface(), (startbutton.x, startbutton.y))
        background.blit(screen, (- LINEWIDTH / 2, - LINEWIDTH / 2))
        pygame.display.flip()

    ## 程序主循环
    fix_screen = INIT_SCREEN.copy()
    displaybox_init = False
    # 选择状态相关
    select_stat = ''
    enable_selectList = []
    menu = 'main'  # 主菜单
    inputstr = ''
    inputbox = InputBox([300, 420, 300, 50], visible = False, lock = True)
    select_List = []
    selectplayer = None
    # 一些全局存储的变量
    charge = None
    specialblock = SpecialEvent(building_list, PlayerList, active_player)
    # 保存读取相关
    S_DIR = 'saves'
    if not os.path.exists(S_DIR):
        os.mkdir(S_DIR)
    s_path = os.path.join(S_DIR, 'auto.sav')
    need_save = False
    need_load = False
    saveclock = pygame.time.Clock()
    save_time = 0
    while isStart:
        # 事件处理部分
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # 退出游戏
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:  # 鼠标点击事件，包括滚轮滚动
                # dice_button 事件
                if not dice_button.isLocked:
                    if dice_button.get_avilablerect().collidepoint(event.pos):
                        dice_button.press_down()
                # 消息盒子滑动实现
                if messagebox.get_rect().collidepoint(event.pos):
                    if event.button == 4:
                        messagebox.mouseroll('UP')
                    elif event.button == 5:
                        messagebox.mouseroll('DOWN')
                # button点击事件
                if button1.get_avilablerect().collidepoint(event.pos):
                    button1.press_down()
                if button2.get_avilablerect().collidepoint(event.pos):
                    button2.press_down()
                if button3.get_avilablerect().collidepoint(event.pos):
                    event.button == 1 and button3.press_down() or button3.right_press_down()
                if button4.get_avilablerect().collidepoint(event.pos):
                    button4.press_down()
                # 左键选中方块实现：
                if select_stat == 'selecting':
                    for block in enable_selectList:
                        if block.get_avilablerect().collidepoint(event.pos):
                            if event.button == 1:
                                if not block.selected:
                                    block.select()
                                    if isinstance(block, Player):
                                        selectplayer = block
                                        break
                                    else:
                                        select_List.append(block)
                                        break
                            elif event.button == 3:
                                if block.selected:
                                    block.cancel()
                                    if isinstance(block, Player):
                                        selectplayer = None
                                        break
                                    else: 
                                        select_List.remove(block)
                                        break
            if event.type == pygame.MOUSEBUTTONUP:
                for button in ButtonList:
                    button.press_up()
            if event.type == pygame.KEYDOWN:
                if not inputbox.islocked:
                    if event.key == pygame.K_BACKSPACE:
                        inputbox.delete()
                    elif event.key == pygame.K_DELETE:
                        inputbox.clear()
                    elif event.key in (list(range(48, 58)) + list(range(256, 266)) + list(range(97, 123))):
                        inputbox.get_char(pygame.key.name(event.key).strip('[]'))

            

        ## 程序逻辑更新部分
        # dice_button 事件
        if dice_button.click():
            if not displaybox_init:  # 更新第一次投掷骰子后eventbox情况
                displaybox_init = True
                eventbox.update_text('')
                messagebox.update_text('')
                eventbox.update_rect([250, 250, 400, 250])
                pygame.draw.rect(fix_screen, BLACK, [250, 250, 400, 400], LINEWIDTH)
                button1.show()
                button2.show()
                button3.show()
                button4.show()
                dice_button.text = '{}\n点击投掷！'.format(active_player.name)
                messagebox.size = 18
                messagebox.mode = '左对齐'
            elif dice_button.text == '结束回合': 
                index = PlayerList.index(active_player)
                if not dice.isbonus or active_player.prison:
                    index += 1
                    if index > len(PlayerList) - 1:
                        index = 0
                while PlayerList[index].prison:
                    tmp_player = PlayerList[index]
                    tmp_player.prison -= 1
                    messagebox.add_rolltext('玩家：{}入狱，'.format(tmp_player.name) + (tmp_player.prison and '还剩{}回合'
                                            .format(tmp_player.prison) or '即将出狱'))
                    index += 1
                    if index > len(PlayerList) - 1:
                        index = 0
                if active_player == PlayerList[index]:
                    active_player.bonus_count += 1
                else:
                    active_player.bonus_count = 0
                    active_player = PlayerList[index]
                dice_button.text = dice.isbonus and '再掷一次！' or '{}\n点击投掷！'.format(active_player.name)
                eventbox.update_text('玩家：{}\n请点击投掷！'.format(active_player.name))
            elif '掷' in dice_button.text:
                dice_button.lock()
                if active_player.bonus_count >=3:
                    if not active_player.prison_passport: 
                        messagebox.add_rolltext('玩家：{}因为太欧入狱'.format(active_player.name)) #待测试
                        active_player.change_pos(building_list[16])
                    else:
                        messagebox.add_rolltext('玩家：{}因为太欧入狱，使用监狱通行证免于牢狱之灾'.format(active_player.name))
                        active_player.prison_passport -= 1
                        active_player.init()
                        active_player.needjump = True
                        dice.needroll = True
                else:
                    active_player.init()
                    active_player.needjump = True
                    dice.needroll = True
                dice_button.text = '结束回合'
            elif dice_button.text == '确认破产':
                eventbox.size = 20
                menu = 'main'
                index = PlayerList.index(active_player)
                index += 1
                if index >= len(PlayerList):
                    index = 0
                b_player = active_player
                for block in b_player.ownblockList + b_player.ownpublicList + b_player.owntransportList:
                    block.owner = None
                    block.need_update = True
                active_player = PlayerList[index]
                PlayerList.remove(b_player)
                dice.isbonus = False
                dice_button.text = '{}\n点击投掷！'.format(active_player.name)
                eventbox.update_text('玩家：{}\n请点击投掷！'.format(active_player.name))
            elif dice_button.text == '游戏结束':
                sys.exit()

        # 保存读取
        save_time += saveclock.tick() / 1000
        if save_time > 60.0:
            need_save = True
            save_time = 0
            messagebox.add_rolltext('自动保存中...')
        if need_save:
            player_saveList = []
            for player in PlayerList:
                player_saveList.append(player.get_saveList())
            dice_save = dice.get_saveList()
            building_saveList = []
            for block in building_list:
                building_saveList.append(block.get_saveList())
            displaybox_saveList = [moneybox.get_saveList(), messagebox.get_saveList(), eventbox.get_saveList()]
            active_player_index = PlayerList.index(active_player)
            savelis = (player_saveList, dice_save, building_saveList, displaybox_saveList, active_player_index, dice_button.text)
            with open(s_path, 'wb') as f:
                pickle.dump(savelis, f)
            need_save = False
            messagebox.add_rolltext('保存完成！')
        if need_load:
            with open(s_path, 'rb') as f:
                loadlis = pickle.load(f)
            (player_saveList, dice_save, building_saveList, displaybox_saveList, active_player_index, dice_button_savetext) = loadlis
            PlayerList.clear()
            for i in range(len(player_saveList)):
                player_save = player_saveList[i]
                for player in RAW_PlayerList:
                    if player.name == player_save[0]:
                        PlayerList.append(player)
                        player.load_saveList(player_save)
                        break
            dice.load_saveList(dice_save)
            for i in range(len(building_list)):
                blockowner_name = building_saveList[i][-1]
                if blockowner_name:
                    for player in PlayerList:
                        if player.name == blockowner_name:
                            block_owner = player
                            break
                else:
                    block_owner = None
                building_saveList[i][-1] = block_owner
                building_list[i].load_saveList(building_saveList[i])
            moneybox.load_saveList(displaybox_saveList[0])
            messagebox.load_saveList(displaybox_saveList[1])
            eventbox.load_saveList(displaybox_saveList[2])
            active_player = PlayerList[active_player_index]
            dice_button.update_text(dice_button_savetext)
            messagebox.add_rolltext('载入存档成功！')
            need_load = False
                
        # 方块选择状态：
        if select_stat == 'begin':
            select_stat = 'selecting'
            for enable_block in enable_selectList:
                enable_block.need_select = True

        # 菜单按钮锁定部分
        change_buttonList = [button1, button2, button3, button4]
        for button in change_buttonList:
            if (active_player.needjump or active_player.needmove or dice.needroll or ('掷' in dice_button.text and menu == 'main')
                 or active_player.prison or dice.charge_needroll): 
                button.lock()
            else:
                button.unlock()
        if '掷' in dice_button.text:
            button3.unlock()
        # 破产判定：
        if active_player.bankrupted:
            if active_player.asset_statistics() < charge:
                menu = 'bankrupted'
                if len(PlayerList) > 2:
                    dice_button.update_text('确认破产')
                else:
                    dice_button.update_text('游戏结束')
                for button in change_buttonList:
                    button.lock()
                text = '结算：\n \n'
                for player in PlayerList:
                    if player != active_player:
                        text += '玩家：{}，总资产：{}元\n'.format(player.name, player.asset_statistics())
                text += ' \n玩家：{}不幸破产！'.format(active_player.name)
                eventbox.update_text(text)
                eventbox.size = 18

        # 主菜单
        if menu == 'main':
            if eventbox.text == '' or eventbox.text == '请选择要进行的操作：':
                eventbox.update_text('请选择项目')
            if not active_player.bankrupted:
                button1.update_text('买地')
            else:
                button1.update_text('支付欠款')
            button2.update_text('角色')
            button3.update_text('设置')
            button4.update_text('操作')
            if active_player.prison:
                button4.lock()
            if button4.isWorked:
                menu = 'handle'
                button4.isWorked = False
            if active_player.operate:
                button1.click()
            if button2.click():
                menu = 'character'
            if button3.click():
                menu = 'setting'
        # # 角色
        elif menu == 'character':
            dice_button.lock()
            button1.update_text('技能')
            button2.update_text('祝福')
            button3.hide()
            button4.update_text('返回')
            house = 0
            hotal = 0
            for block in active_player.ownblockList:
                if block.houseNum:
                    house += block.houseNum
                if block.hotal:
                    hotal += 1
            text = ('玩家：{}\n \n拥有地皮：{}\n  拥有房屋：{}\n  拥有旅馆：{}\n拥有公共交通：{}\n拥有公共事业：{}\n拥有监狱通行证：{}\n总资产：{}元'
                    .format(active_player.name, len(active_player.ownblockList), house, hotal, len(active_player.owntransportList)
                    , len(active_player.ownpublicList), active_player.prison_passport, active_player.asset_statistics()))
            if not '祝福' in eventbox.text:
                eventbox.size = 18
                eventbox.update_text(text)
            if button4.click():
                menu = 'main'
                button3.show()
                eventbox.size = 20
                eventbox.update_text('请选择项目')
            if button1.click():
                menu = 'skill'
            if button2.click():
                if not '祝福' in eventbox.text:
                    eventbox.size = 20
                    b_text = '祝福：\n \n'
                    if active_player.blessing:
                        for blessing in active_player.blessing:
                            b_text += '下一次{}\n'.format(blessing)
                    else:
                        b_text += '无'
                    eventbox.update_text(b_text)
                else:
                    eventbox.size = 18
                    eventbox.update_text(text)
        
                
        # # # 技能
        elif menu == 'skill':
            dice_button.lock()
            button1.lock()
            button1.update_text('确认使用')
            button2.update_text('取消')
            button3.hide()
            button4.update_text('返回')
            if active_player.name == '食蜂':
                skill_cost = 5
                skill_text = '消耗({})点技能点\n随机获得其他玩家的一块空地'.format(skill_cost)
            elif active_player.name == '黑子':
                skill_cost = 2
                skill_text = '消耗({})点技能点\n随机移动至一块土地'.format(skill_cost)
            elif active_player.name == '泪子':
                skill_cost = 2
                skill_text = '消耗({})点技能点\n随机触发一次幸运机会'.format(skill_cost)
            elif active_player.name == '警策':
                skill_cost = 2
                skill_text = '消耗({})点技能点\n获得一个额外回合'.format(skill_cost)
            if not '使用' in eventbox.text:
                eventbox.update_text('技能描述：\n \n' + skill_text + '\n \n当前技能点：({})'.format(active_player.skill_point))
            if skill_cost <= active_player.skill_point: 
                button1.unlock()
            if button4.click():
                menu = 'character'
                button1.unlock()
            if button2.click():
                pass
            if button1.click():
                blis = []
                receive = ''
                if active_player.name == '食蜂':
                    for block in building_list:
                        if block.isbuilding == 1:
                            if block.owner and block.owner != active_player and not block.mortgage:
                                if not block.houseNum and not block.hotal and not block.colorname in block.owner.enable_colorList:
                                    blis.append(block)
                    if not blis: 
                        message = '使用失败！\n没有有效的目标'
                    else:
                        targetblock = random.choice(blis)
                        old_owner = targetblock.owner
                        targetblock.owner.ownblockList.remove(targetblock)
                        targetblock.owner.update()
                        targetblock.owner = active_player
                        active_player.ownblockList.append(targetblock)
                        active_player.update()
                        targetblock.need_update = True
                        message = '玩家：{}使用心理掌握获取了{}的{}'.format(active_player.name, old_owner.name, targetblock.name)
                elif active_player.name == '黑子':
                    for block in building_list:
                        if block.isbuilding == 1:
                            blis.append(block)
                    if not blis: 
                        message = '使用失败！\n没有有效的目标'
                    else:
                        targetblock = random.choice(blis)
                        active_player.change_pos(targetblock)
                        message = '玩家：{}使用瞬间移动到达了{}'.format(active_player.name, targetblock.name)
                elif active_player.name == '泪子':
                    chanceList = [1, 3, 5, 7, 9, 12, 14] # 奖金、退税、加盖、群体加盖、随机空地、监狱通行证、随机移动
                    buildrate = active_player.enable_blockList and 3 or 1
                    tax = active_player.ownblockList and 5 or 2
                    heightList = [5, tax, 1 + buildrate, buildrate - 1, 1 + (3 - buildrate), 4, 3]
                    chance_mode = random.choices(chanceList, heightList)[0]
                    specialblock.active_player = active_player
                    receive = specialblock.chance(chance_mode)
                    message = '玩家：{}使用剧本预知触发了一次幸运机会'.format(active_player.name)
                elif active_player.name == '警策':
                    if not dice.isbonus:
                        dice.isbonus = True
                        active_player.bonus_count -= 1
                        message = '玩家：{}使用液化人形获得一个额外回合'.format(active_player.name)
                    else:
                        message = '使用失败！\n已经拥有额外回合'
                if not '失败' in message:
                    active_player.skill_point -= skill_cost
                    eventbox.update_text('使用成功！')
                    messagebox.add_rolltext(message)
                    if receive:
                        messagebox.add_rolltext(receive)
                else:
                    eventbox.update_text(message)

            

        # # 设置
        elif menu == 'setting':
            dice_button.lock()
            if not '音乐' in button1.text:
                button1.update_text('音乐：关')
            button2.update_text('保存')
            button3.update_text('读取')
            button4.update_text('返回')
            if button4.click():
                menu = 'main'
            if button1.click():
                if button1.text == '音乐：开':
                    button1.update_text('音乐：关')
                    pygame.mixer.music.pause()
                elif button1.text == '音乐：关':
                    button1.update_text('音乐：开')
                    pygame.mixer.music.unpause()
            if button2.click():
                need_save = True
            if button3.click():
                need_load = True

        # # 操作
        elif menu == 'handle':
            dice_button.lock()
            button1.update_text('加盖')
            button2.update_text('交易')
            button3.update_text('抵押/赎回')
            button4.update_text('返回')
            button3.show()
            eventbox.update_text('请选择要进行的操作：')
            if button4.isWorked:
                menu = 'main'
                button4.isWorked = False
            if button1.isWorked:
                menu = 'build'
                button1.isWorked = False
            if button3.click():
                menu = 'mortgage'
            if button3.click_right():
                menu = 'buyback'
            if button2.click():
                menu = 'deal'
        # # # 加盖
        elif menu == 'build':
            dice_button.lock()
            enable_selectList = active_player.enable_blockList
            if not select_stat or select_stat == 'selected':
                select_stat = 'begin'
            button1.lock()
            button1.update_text('确定')
            button2.update_text('取消')
            button3.hide()
            button4.update_text('返回')
            sum = 0
            if select_List:
                for block in select_List:
                    sum += block.newbuilding_price
                eventbox.update_text('选择了{}块土地\n加盖费用{}元'.format(len(select_List), sum))
                eventbox.need_update = True
                button1.unlock()
            elif select_stat == 'selecting' and not '继续加盖' in eventbox.text:
                eventbox.update_text('请点击需要加盖的土地：')
                eventbox.need_update = True
            if button4.click():
                menu = 'handle'
                select_stat = ''
                for block in active_player.building_list:
                    block.need_select = False
                    block.selected = False
                    block.need_update = True
                select_List.clear()
                moneybox.need_update = True
                messagebox.need_update = True
                button1.unlock()
                enable_selectList = []
            if button1.click():
                select_stat = 'selected'
                build = False
                complete = True
                blockname = ''
                if active_player.money >= sum:
                    build = True
                for block in select_List:
                    if build:
                        if not active_player.construct_house(block):
                            complete = False
                    block.selected = False
                    blockname += block.name + '、'
                for blessing in active_player.blessing:
                    if '加盖' in blessing:
                        if '增加' in blessing:
                            sum = int(sum * 1.5)
                        elif '减少' in blessing:
                            sum = int(sum * 0.5)
                        active_player.blessing.remove(blessing)
                        break
                if build and complete and sum:
                    messagebox.add_rolltext('玩家：{}，花费了{}元为{}加盖了房屋'.format(active_player.name, sum, blockname.strip('、'))
                                            , force_update=True)
                    messagebox.need_update = True
                    eventbox.update_text('\n加盖成功！\n请继续加盖或者返回', mode = 'add')
                else:
                    eventbox.update_text('\n加盖失败！\n请继续加盖或者返回', mode = 'add')
                    messagebox.need_update = True
                select_List.clear()
            if button2.click():
                for block in select_List:
                    block.selected = False
                select_List.clear()
        # # # 抵押
        elif menu == 'mortgage':
            dice_button.lock()
            enable_selectList = active_player.enable_mortgageList
            if not select_stat or select_stat == 'selected':
                select_stat = 'begin'
            button1.lock()
            button2.lock()
            button3.lock()
            if select_List: 
                button1.unlock()
                colorDict = active_player.count_block_color(mode = 'in', list = select_List)
                for color in colorDict.keys():
                    if colorDict[color] == active_player.allcolorDict[color]:
                        button2.unlock()
                        button3.unlock()
            button1.update_text('确定')
            button2.update_text('拆房')
            button3.update_text('全部')
            button4.update_text('返回')
            sum = 0
            if select_List:
                for block in select_List:
                    if block.hotal or block.houseNum:
                        sum += int(block.newbuilding_price * 0.5)
                    else:
                        sum += int(block.blockprice * 0.5)
                eventbox.update_text('选择了{}块土地\n抵押一次可得{}元'.format(len(select_List), sum))
                eventbox.need_update = True
            elif select_stat == 'selecting' and not '继续抵押' in eventbox.text:
                eventbox.update_text('请点击需要抵押的土地：')
                eventbox.need_update = True
            if button4.click():
                menu = 'handle'
                button1.lock()
                button2.unlock()
                button3.unlock()
                select_stat = ''
                for block in active_player.building_list: 
                    block.need_select = False 
                    block.selected = False
                    block.need_update = True
                select_List.clear()
                moneybox.need_update = True
                messagebox.need_update = True
                enable_selectList = []
            if button1.click():
                select_stat = 'selected'
                blockname = ''
                for block in select_List:
                    active_player.sell(block)
                    block.selected = False
                    block.need_update = True
                    blockname += block.name + '、'
                for blessing in active_player.blessing:
                    if '抵押' in blessing:
                        if '增加' in blessing:
                            sum = int(sum * 1.5)
                        elif '减少' in blessing:
                            sum = int(sum * 0.5)
                        active_player.blessing.remove(blessing)
                        break
                if sum:
                    messagebox.add_rolltext('玩家：{}，抵押了{}得到了{}元'.format(active_player.name, blockname.strip('、'), sum)
                                            , force_update=True)
                    messagebox.need_update = True
                    eventbox.update_text('\n抵押成功！\n请继续抵押或者返回', mode = 'add')
                select_List.clear()
            mode = ''
            if button2.click():
                mode = 'buildings'
            elif button3.click():
                mode = 'all'
            if mode:
                select_stat = 'selected'
                blockname = ''
                sum = 0
                for block in select_List:
                    sell = active_player.sell(block, mode)
                    block.selected = False
                    block.need_update = True
                    sum += int(sell)
                    blockname += block.name + '、'
                if select_List:
                    messagebox.add_rolltext('玩家：{}，{}抵押了{}{}，得到了{}元'.format(active_player.name, mode == 'all' and '全部' or ''
                                            , blockname.strip('、'), mode == 'buildings' and '的全部房屋' or '', sum), force_update=True)
                    messagebox.need_update = True
                    eventbox.update_text('\n抵押成功！\n请继续抵押或者返回', mode = 'add')
                select_List.clear()
        # # # 赎回
        elif menu == 'buyback':
            dice_button.lock()
            enable_selectList = active_player.enable_buybackList
            if not select_stat or select_stat == 'selected':
                select_stat = 'begin'
            button1.lock()
            button2.lock()
            if select_List: 
                button1.unlock()
                button2.unlock()
            button1.update_text('确定')
            button2.update_text('取消')
            button3.hide()
            button4.update_text('返回')
            sum = 0
            if select_List:
                for block in select_List:
                    sum += int(block.blockprice * 0.6)
                eventbox.update_text('选择了{}块土地\n赎回费用{}元'.format(len(select_List), sum))
                eventbox.need_update = True
                button1.unlock()
            elif select_stat == 'selecting' and not '继续赎回' in eventbox.text:
                eventbox.update_text('请点击需要赎回的土地：')
                eventbox.need_update = True
            if button4.click():
                menu = 'handle'
                select_stat = ''
                for block in active_player.building_list:
                    block.need_select = False
                    block.selected = False
                    block.need_update = True
                select_List.clear()
                moneybox.need_update = True
                messagebox.need_update = True
                button1.unlock()
                enable_selectList = []
            if button1.click():
                select_stat = 'selected'
                blockname = ''
                buyback = False
                complete = True
                if active_player.money >= sum:
                    buyback = True
                for block in select_List:
                    if buyback:
                        if not active_player.buyback(block):
                            complete = False
                    block.selected = False
                    block.need_update = True
                    blockname += block.name + '、'
                if buyback and complete and sum:
                    messagebox.add_rolltext('玩家：{}，花费了{}元赎回了{}'.format(active_player.name, sum, blockname.strip('、'))
                                            , force_update=True)
                    messagebox.need_update = True
                    eventbox.update_text('\n赎回成功！\n请继续赎回或者返回', mode = 'add')
                else:
                    eventbox.update_text('\n赎回失败！\n请继续赎回或者返回', mode = 'add')
                    messagebox.need_update = True
                select_List.clear()
            if button2.click():
                for block in select_List:
                    block.selected = False
                select_List.clear()
        # # #交易
        elif menu == 'deal': 
            dice_button.lock()
            if not select_stat or select_stat == 'selected':
                select_stat = 'begin'
            button1.lock()
            button2.lock()
            if selectplayer:
                enable_selectList = [selectplayer] + active_player.enable_dealList
                if select_List and inputbox.text: 
                    button1.unlock()
                    button2.unlock()
            else:
                enable_selectList = PlayerList + active_player.enable_dealList
                enable_selectList.remove(active_player)
            button1.update_text('确定')
            button2.update_text('取消')
            button3.hide()
            button4.update_text('返回')
            if select_List and selectplayer:
                eventbox.update_text('选择了{}块土地\n交易对象：{}  金钱：{}'.format(len(select_List), selectplayer.name, selectplayer.money))
                eventbox.need_update = True
            elif select_stat == 'selecting' and not '继续交易' in eventbox.text:
                eventbox.update_text('请点击需要交易的土地以及交易玩家\n并输入期望的交易金额：')
                eventbox.need_update = True
                inputbox.show()
                inputbox.mode = 'num'
            if button4.click():
                menu = 'handle'
                select_stat = ''
                for block in active_player.building_list + PlayerList:
                    block.need_select = False
                    block.selected = False
                    block.need_update = True
                select_List.clear()
                selectplayer = None
                moneybox.need_update = True
                messagebox.need_update = True
                button1.unlock()
                inputbox.hide()
                enable_selectList = []
            if button1.click():
                select_stat = 'selected'
                price = int(inputbox.text)
                enable_deal = False
                complete = False
                blockname = ''
                if selectplayer:
                    if selectplayer.money >= price:
                        enable_deal = True
                for block in select_List + [selectplayer]:
                    if enable_deal and isinstance(block, Block):
                        blockname += block.name + '、'
                        if active_player.deal(block, selectplayer):
                            complete = True
                    block.selected = False
                if enable_deal and complete and selectplayer:
                    messagebox.add_rolltext('玩家：{}，将{}以{}元交易给了{}'.format(active_player.name, blockname.strip('、'), price
                                            , selectplayer.name), force_update=True)
                    active_player.money += price
                    selectplayer.money -= price
                    eventbox.update_text('交易成功！\n请继续交易或者返回')
                else:
                    eventbox.update_text('交易失败！\n请继续交易或者返回')
                    messagebox.need_update = True
                select_List.clear()
                selectplayer = None
                inputbox.clear()
            if button2.click():
                for block in select_List + [selectplayer]:
                    block.selected = False
                select_List.clear()
                selectplayer = None
                inputbox.clear()

                


        # moneybox 和 messagebox 显示部分
        if dice.rolled:
            messagebox.add_rolltext(
                '玩家：{}，掷出{}点{}'.format(active_player.name, dice.rollsum, dice.isbonus and ',再掷一次' or ''))
            if active_player.needmove:
                active_player.dice = dice.rollsum
            dice.rolled = False
        if active_player.thoughstart == True:
            messagebox.add_rolltext('玩家：{}经过起点，领取150元并获取(1)技能点'.format(active_player.name))
            active_player.thoughstart = False
        if displaybox_init:
            moneybox.update_text('当前玩家：\n{}\n金钱：{}元'.format(active_player.name, active_player.money))
        else:
            p_text = '玩家顺序：\n'
            for i in range(len(PlayerList)):
                p_text += '{}：{} '.format(i + 1, PlayerList[i].name)
                if i % 2 == 1:
                    p_text += '\n'
            moneybox.update_text(p_text.strip('\n'))

        
        # 移动结束后的事件：
        if active_player.needmove == False and active_player.needjump == False and menu == 'main':
            if displaybox_init and not active_player.operate:
                text = '玩家：{}\n来到了{}'.format(active_player.name, active_player.block.name)
                if active_player.block.isbuilding == 0:
                    if not active_player.bankrupted:
                        if active_player.move_sign:
                            messagebox.add_rolltext(text)
                            eventbox.update_text(text)
                            active_player.move_sign = False
                        if active_player.block.name == '监狱':
                            if not active_player.prison_passport:
                                active_player.prison = 1
                                messagebox.add_rolltext('玩家：{}自投罗网，入狱一回合'.format(active_player.name))
                                if dice.isbonus:
                                    dice.isbonus = False
                            else:
                                active_player.prison_passport -= 1
                                messagebox.add_rolltext('玩家：{}使用了监狱通行证，免于牢狱之灾'.format(active_player.name))
                            active_player.operate = True
                        elif active_player.block.name == '机会':
                            specialblock.active_player = active_player
                            receive = specialblock.chance()
                            if isinstance(receive, str):
                                messagebox.add_rolltext(receive)
                            else:
                                charge = receive[0]
                                t_text = receive[1] + '\n濒临破产，需支付欠款{}元'.format(charge)
                                eventbox.update_text(t_text, mode = 'add')
                                messagebox.add_rolltext(t_text)
                        elif active_player.block.name == '祝福':
                            specialblock.active_player = active_player
                            receive = specialblock.blessing()
                            messagebox.add_rolltext('玩家：{}得到了祝福，下一次'.format(active_player.name) + receive)
                        elif active_player.block.name == '技能':
                            specialblock.active_player = active_player
                            specialblock.skill()
                            messagebox.add_rolltext('玩家：{}获得(2)技能点，目前技能点：({})'.format(active_player.name, active_player.skill_point))
                    else:
                        if button1.click() and menu == 'main':
                            if active_player.money >= charge:
                                active_player.money -= charge
                                active_player.bankrupted = False
                                text_charge = '玩家：{}\n支付了欠款'.format(active_player.name)
                                messagebox.add_rolltext(text_charge)
                                eventbox.update_text(text_charge)
                                active_player.operate = True      
                    
                elif active_player.block.isbuilding != 0:
                    if not active_player.block.owner and menu == 'main':
                        if not '购买成功' in eventbox.text and not '购买失败' in eventbox.text:
                            eventbox.update_text('玩家：{}\n是否购买{}？'.format(active_player.name, active_player.block.name))
                        if button1.click() and menu == 'main':
                            buy_text = active_player.buy_Block(active_player.block)
                            messagebox.add_rolltext(buy_text)
                            eventbox.update_text(buy_text)
                            if '成功' in buy_text:
                                active_player.operate = True
                        elif active_player.move_sign:
                            messagebox.add_rolltext(text)
                            active_player.move_sign = False
                    elif active_player.block.owner != active_player and menu == 'main':
                        if active_player.need_pay:
                            if not active_player.bankrupted:
                                messagebox.add_rolltext(text)
                                charge = int(active_player.block.get_charge(dice))
                            if charge:
                                if not active_player.bankrupted:
                                    dice_button.unlock()
                                    paytext = active_player.pay(int(charge), dice, active_player.block.owner)
                                    dice.charge_rolled = False    
                                    text_charge = ('玩家：{}\n走到了{}的{},真是不幸\n{}'
                                                .format(active_player.name, active_player.block.owner.name,
                                                        active_player.block.isbuilding != 1
                                                        and '产业' or (active_player.block.hotal and '旅馆' or (
                                                                active_player.block.houseNum and '房子'
                                                                or '土地')), paytext))
                                    messagebox.add_rolltext(text_charge)
                                    if '破产' in paytext:
                                        active_player.bankrupted = True
                                        dice_button.lock()
                                    else:
                                        active_player.operate = True
                                        eventbox.update_text(text_charge)
                                elif active_player.asset_statistics() >= charge:
                                    eventbox.update_text('玩家：{}\n请支付欠款'.format(active_player.name))
                                    if button1.click() and menu == 'main':
                                        if active_player.money >= charge:
                                            active_player.money -= charge
                                            active_player.block.owner.money += charge
                                            active_player.bankrupted = False
                                            text_charge = '玩家：{}\n支付了欠款'.format(active_player.name)
                                            messagebox.add_rolltext(text_charge)
                                            eventbox.update_text(text_charge)
                                            active_player.operate = True       
                            
                            elif active_player.block.owner.prison:
                                messagebox.add_rolltext('玩家：{}，由于{}入狱，免收路费'.format(active_player.name, 
                                                        active_player.block.owner.name))
                                active_player.operate = True
                    elif active_player.block.owner == active_player and not active_player.operate:
                        messagebox.add_rolltext(text)
                        active_player.operate = True
            if not active_player.bankrupted and not dice.charge_needroll:
                dice_button.unlock()
        elif menu == 'bankrupted' and (dice_button.text == '确认破产' or dice_button.text == '游戏结束'):
            dice_button.unlock()


        ## 画面更新部分

        # 改变时绘图序列
        bgd_drawList = DisplayBoxList + ButtonList + (not select_stat and building_list or []) # A and B or C 运算符应保证B为真
        for draw in bgd_drawList:
            if draw.need_update:
                fix_screen.blit(draw.get_Surface(), (draw.x, draw.y))
        screen = fix_screen.copy()

        # 选择时绘图序列
        if select_stat:
            for block in building_list + [inputbox]:
                screen.blit(block.get_Surface(), (block.x, block.y))

        # 实时绘图序列
        DrawList = DiceList + PlayerList  # 考虑后续逻辑更新，骰子必须先行绘制
        # 实时更新的绘图序列
        for draw in DrawList:
            screen.blit(draw.get_Surface(), (draw.x, draw.y))

        background.blit(screen, (- LINEWIDTH / 2, - LINEWIDTH / 2))
        pygame.display.flip()


if __name__ == "__main__":
    main()
