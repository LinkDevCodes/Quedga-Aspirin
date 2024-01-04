import os
import re
import sys
import time
import pygame
import weakref
import configparser

import System.Source.file as file
import System.Source.display as display
import System.Source.hardware as hardware
import System.Source.exception as exception
import System.Source.arithmetic.generating as generating
import System.Source.arithmetic.handle as handle
import System.Source.arithmetic.__handle as __handle

from System.Source.constants import *
from System.Source.spirits.tiles import *
from System.Source.spirits.drivers import *
from System.Source.constants import workspace
from System.Source.spirits.computerPlayer import computerPlayer as cPlayer

pygame.init()
keysPressedEvent = []
gameWindow = None
handle.temp = []
buttonSensitivity = 10000
fileInformation = {}
gameWindowLength, gameWindowWidth = 300, 100
keys_pressed, mouse_coordinate = [], ()
mouseRollUp, mouseRollDown = False, False
mouseDown, keyboardDown, keyboardUp = False, False, False
flag = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE  # 窗口模式应急配适


conf = configparser.ConfigParser()
conf.read(filenames='./System/main.ini', encoding='utf-8')
if conf['WINDOWS'].getboolean('isLogo'):
    logoWindow = pygame.display.set_mode(size=(gameWindowLength, gameWindowWidth), flags=pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE | pygame.NOFRAME, depth=36)  # 启动用的临时窗口
    for _ in range(20000):
        pygame.display.flip()  # 刷新渲染
del conf


try:
    aspirinConfigElement = configparser.ConfigParser()  # 初始化配适器
    aspirinConfigElement.read(filenames='./System/main.ini', encoding='utf-8')  # 配置配适目标
    presentSection = 'WINDOWS'  # 读取窗口信息
    # 读取窗口大小(分辨率)
    gameWindowLength, gameWindowWidth = int(aspirinConfigElement.get(presentSection, 'LENGTH')), int(
        aspirinConfigElement.get(presentSection, 'WIDTH'))
    gameWindowTitle = aspirinConfigElement.get(presentSection, 'TITLE')  # 读取窗口标题
    gameWindowIconLoading = aspirinConfigElement.get(presentSection, 'ICON')  # 读取窗口图标
    gameWindowIcon = pygame.image.load(gameWindowIconLoading)  # 载入图标的对象
    gameWindowRatio = re.split(':', aspirinConfigElement.get(presentSection, 'RATIO'))  # 读取长宽比
    gameWindowRatio = int(gameWindowRatio[0]), int(gameWindowRatio[1])  # 格式化长宽比
    # isGrab：是否占据计算机一切的鼠标与键盘操作(Esc->out), isSizeChange：对于用户对于主窗口大小自主调整的许可, isDouble：是否使用双线程渲染, isUsingRatio：是否使用长宽比保持控件
    isGrab = bool(0 if aspirinConfigElement.get(presentSection, 'GRAB') == 'False' else 1 if aspirinConfigElement.get(
        presentSection, 'GRAB') == 'True' else 0)
    isSizeChange = bool(
        0 if aspirinConfigElement.get(presentSection, 'isSizeChangeAble') == 'False' else 1 if aspirinConfigElement.get(
            presentSection, 'isSizeChangeAble') == 'True' else 0)
    isDouble = bool(
        0 if aspirinConfigElement.get(presentSection, 'doubleBuf') == 'False' else 1 if aspirinConfigElement.get(
            presentSection, 'doubleBuf') == 'True' else 0)
    isUsingRatio = bool(
        0 if aspirinConfigElement.get(presentSection, 'isUsingRatio') == 'False' else 1 if aspirinConfigElement.get(
            presentSection, 'isUsingRatio') == 'True' else 0)
    presentSection = 'DISPLAY'  # 读取渲染信息
    gameFPS = int(aspirinConfigElement.get(presentSection, 'FPS'))  # 读取游戏帧率
    display.backgroundColor = handle.intTupleCommasString(
        aspirinConfigElement.get(presentSection, 'defaultBackground'))  # 读取默认背景色
    presentSection = 'FONTS'  # 读取字体信息
    gameWindowFontPath = aspirinConfigElement.get(presentSection, 'DefaultPath')
    FontSizeTitle = int(aspirinConfigElement.get(presentSection, 'TitleSize'))
    FontSizeLarge = int(aspirinConfigElement.get(presentSection, 'LargeSize'))
    FontSizeDefault = int(aspirinConfigElement.get(presentSection, 'DefaultSize'))
    FontSizeLittle = int(aspirinConfigElement.get(presentSection, 'LittleSize'))
    FontSizeTip = int(aspirinConfigElement.get(presentSection, 'TipSize'))
    presentSection = 'HARDWARE'  # 读取硬件信息
    buttonSensitivity = int(aspirinConfigElement.get(presentSection, 'buttonSensitivity'))
    keyboardSensitivity = int(aspirinConfigElement.get(presentSection, 'keyboardSensitivity'))
    rollSelectorSensitivity = int(aspirinConfigElement.get(presentSection, 'rollSelectorSensitivity'))
    presentSection = 'FILE'  # 读取文件信息
    for key, value in aspirinConfigElement[presentSection].items():
        fileInformation[key] = value

except configparser.NoSectionError:
    gameFPS = 60
    gameWindowLength, gameWindowWidth = 620, 360
    gameWindowRatio = (16, 9)
    gameWindow = pygame.display.set_mode(size=(gameWindowLength, gameWindowWidth),
                                         flags=pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
    buttonSensitivity = 7000
    raise SyntaxError
except configparser.NoOptionError:
    gameFPS = 60
    gameWindowLength, gameWindowWidth = 620, 360
    gameWindowRatio = (16, 9)
    gameWindow = pygame.display.set_mode(size=(gameWindowLength, gameWindowWidth),
                                         flags=pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
    buttonSensitivity = 7000
    raise SyntaxError
except ValueError:
    gameFPS = 60
    gameWindowLength, gameWindowWidth = 620, 360
    gameWindowRatio = (16, 9)
    gameWindow = pygame.display.set_mode(size=(gameWindowLength, gameWindowWidth),
                                         flags=pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
    buttonSensitivity = 7000
    raise SyntaxError
else:
    # 配适窗口格式
    if isSizeChange and isDouble:
        flag = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
    elif isSizeChange or isDouble:
        flag = pygame.HWSURFACE | pygame.DOUBLEBUF if isDouble else pygame.HWSURFACE | pygame.RESIZABLE
    else:
        flag = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
    gameWindow = pygame.display.set_mode(size=(gameWindowLength, gameWindowWidth), flags=flag, depth=36)  # 初始化窗口
    SIZE = (gameWindowLength, gameWindowWidth)  # 登记窗口大小状态
    pygame.display.set_caption(gameWindowTitle)  # 初始化窗口标题
    pygame.display.set_icon(gameWindowIcon)  # 初始化窗口图标
    pygame.event.set_grab(isGrab)  # 初始化窗口硬件输入流范围权限
    gameWindowInfo = pygame.display.Info()  # 读取窗口注册初始化信息
    gameWindowTitleFont = pygame.font.Font(gameWindowFontPath, FontSizeTitle)  # 初始化标题字体
    gameWindowLargeFont = pygame.font.Font(gameWindowFontPath, FontSizeLarge)  # 初始化大号字体
    gameWindowDefaultFont = pygame.font.Font(gameWindowFontPath, FontSizeDefault)  # 初始化默认字体
    gameWindowLittleFont = pygame.font.Font(gameWindowFontPath, FontSizeLittle)  # 初始化小号字体
    gameWindowTipFont = pygame.font.Font(gameWindowFontPath, FontSizeTip)  # 初始化提示字体
finally:
    del aspirinConfigElement  # 析构配适器
    del presentSection  # 析构节的配适参量
    fpsControl = pygame.time.Clock()  # 初始化帧率控件
    Quit = lambda e, k: exit() if e.type == 256 or k[pygame.K_ESCAPE] or e.type == pygame.QUIT else None  # 初始化退出事件预处理
    graphicalUserInterfaceElements = {}  # 初始化图形化用户界面引索词典: key.type(must)=int
    graphicalArtExpendElements = {}  # 初始化图形化美术增强词典: key.type(must)=int
    gameWindow.fill(display.backgroundColor)


def updateAfterWindowChange() -> None:
    global graphicalUserInterfaceElements, gameWindow, gameWindowTipFont
    gameWindowTipFont = pygame.font.Font(gameWindowFontPath, int(gameWindow.get_size()[1] // 32 - 4))  # 更新提示字体
    for key in graphicalUserInterfaceElements.keys():
        if type(graphicalUserInterfaceElements[key]) == display.layoutElement:
            graphicalUserInterfaceElements[key].updateWindowsSizeAsSuperiorSize(SIZE)  # 基础布局器窗口大小更新
            graphicalUserInterfaceElements[key].updateAlterableVariable()  # 布局器可表达变量刷新
            graphicalUserInterfaceElements[key].updateDisplay(gameWindow)  # 刷新布局器渲染
        elif type(graphicalUserInterfaceElements[key]) == display.tipsMessagesPusher:
            graphicalUserInterfaceElements[key].updateWindowsSize(SIZE)
            graphicalUserInterfaceElements[key].updateFont(gameWindowTipFont)
            graphicalUserInterfaceElements[key].pushGroup([f'{SYSTEM}:窗口已重新规划'], 25)


def updateFrame() -> None:
    global graphicalUserInterfaceElements, gameWindow
    global mouse_coordinate
    for key in graphicalUserInterfaceElements.keys():
        if graphicalUserInterfaceElements[key].isWake:
            if type(graphicalUserInterfaceElements[key]) == display.layoutElement:
                graphicalUserInterfaceElements[key].update(gameWindow)
                graphicalUserInterfaceElements[key].updateSystemLinkInfo([mouseDown, mouse_coordinate, mouseRollUp, mouseRollDown],
                                                                         [keyboardDown, keyboardUp, keys_pressed])
                graphicalUserInterfaceElements[key].updateDisplay(gameWindow)
            elif type(graphicalUserInterfaceElements[key]) == display.tipsMessagesPusher:
                graphicalUserInterfaceElements[key].keep()


def basicEventProcessing() -> None:
    global fpsControl, keys_pressed, mouse_coordinate, gameWindow, gameWindowLength, gameWindowWidth
    global SIZE, Quit, mouseDown, keyboardDown, keyboardUp, keysPressedEvent, mouseRollUp, mouseRollDown
    keysPressedEvent = []
    fpsControl.tick(gameFPS)  # 帧率控件
    keys_pressed = pygame.key.get_pressed()  # 读取键盘按下事件
    mouse_coordinate = pygame.mouse.get_pos()  # 读取鼠标坐标情况
    if gameWindow.get_size() != (gameWindowLength, gameWindowWidth):  # 窗宽比维持组件
        if isUsingRatio:
            gameWindowLength, gameWindowWidth = display.ratioKeeper(gameWindow, gameWindowRatio)
            gameWindow = pygame.display.set_mode(
                size=(gameWindowLength[0] if type(gameWindowLength) == tuple else gameWindowLength, gameWindowWidth),
                flags=flag, depth=36)
            SIZE = (gameWindowLength[0] if type(gameWindowLength) == tuple else gameWindowLength, gameWindowWidth)
        else:
            gameWindowLength, gameWindowWidth = gameWindow.get_size()
            gameWindow = pygame.display.set_mode(
                size=(gameWindowLength[0] if type(gameWindowLength) == tuple else gameWindowLength, gameWindowWidth),
                flags=flag, depth=36)
            SIZE = (gameWindowLength[0] if type(gameWindowLength) == tuple else gameWindowLength, gameWindowWidth)
        updateAfterWindowChange()
    for systemEvent in pygame.event.get():  # 处理事件
        Quit(systemEvent, keys_pressed)  # 执行退出
        mouseDown = systemEvent.type == pygame.MOUSEBUTTONDOWN  # 侦测鼠标按下
        keyboardDown = systemEvent.type == pygame.KEYDOWN  # 侦测键盘按下
        keyboardUp = systemEvent.type == pygame.KEYUP  # 侦测键盘松开
        if systemEvent.type == pygame.MOUSEBUTTONDOWN:
            mouseRollUp = systemEvent.button == 4
            mouseRollDown = systemEvent.button == 5
    if mouseDown:
        mouseRollUp, mouseRollDown = False, False
    for keyboardEvent in pygame.event.get(pygame.KEYDOWN):
        keysPressedEvent.append(keyboardEvent.key)


def mainPageConfig() -> None:
    global graphicalUserInterfaceElements
    gameWindow.fill((0, 0, 0))
    graphicalUserInterfaceElements['main'].isWake = True
    graphicalUserInterfaceElements['main'].clear()
    graphicalUserInterfaceElements['pusher'].updateTipAppend('')
    graphicalUserInterfaceElements['main'].addElement(
        __10x0=display.alterableText(string='Quedga Aspirin', size=(25, 6), color=(255, 255, 255),
                                     path=gameWindowFontPath, expend={}),
        __13x3=display.Button(string='  游戏 ', size=(10, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"游戏\"按钮选项, 单击鼠标右键以进入',
            '__check__': 'Warning: 当前选中于\"游戏\"按钮选项, 载入游戏页面中…',
            'sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __13x6=display.Button(string='  设置 ', size=(10, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"设置\"按钮选项, 单击鼠标任意键以进入',
            '__check__': 'Warning: 当前选中于\"设置\"按钮选项, 载入游戏页面中…',
            'sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __13x9=display.Button(string='  更多 ', size=(10, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"更多\"按钮选项, 单击鼠标任意键以进入',
            '__check__': 'Warning: 当前选中于\"更多\"按钮选项, 载入游戏页面中…',
            'sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __13x12=display.Button(string='  退出 ', size=(10, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"退出\"按钮选项, 单击鼠标任意键以退出或返回上级',
            '__check__': 'Warning: 执行退出或返回上级',
            'sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        })
    )
    graphicalUserInterfaceElements['main'].updateDisplay(gameWindow)
    time.sleep(hardware.timeControlSensitivityBuilder(buttonSensitivity))


def gamePageConfig() -> None:
    global graphicalUserInterfaceElements
    gameWindow.fill((0, 0, 0))
    graphicalUserInterfaceElements['main'].clear()
    graphicalUserInterfaceElements['main'].addElement(
        __10x0=display.alterableText(string='Quedga Aspirin', size=(25, 6), color=(255, 255, 255),
                                     path=gameWindowFontPath, expend={}),
        __13x3=display.Button(string='单人游戏 ', size=(10, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"单人游戏\"按钮选项, 单击鼠标右键以进入',
            '__check__': 'Warning: 当前选中于\"单人游戏\"按钮选项, 载入游戏页面中…',
            'sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __13x6=display.Button(string='多人对局 ', size=(10, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"多人对局\"按钮选项, 单击鼠标任意键以进入',
            '__check__': 'Warning: 当前选中于\"多人对局\"按钮选项, 载入游戏页面中…',
            'sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __13x9=display.Button(string='联机对局 ', size=(10, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"联机对局\"按钮选项, 单击鼠标任意键以进入',
            '__check__': 'Warning: 当前选中于\"联机对局\"按钮选项, 载入游戏页面中…',
            'sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __13x12=display.Button(string='  退出 ', size=(10, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"退出\"按钮选项, 单击鼠标任意键以退出或返回上级',
            '__check__': 'Warning: 执行退出或返回上级',
            'sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        })
    )
    graphicalUserInterfaceElements['main'].updateDisplay(gameWindow)


def multiplePersonsGamePageConfig(launcher):
    global graphicalUserInterfaceElements
    gameWindow.fill((0, 0, 0))
    graphicalUserInterfaceElements['main'].clear()
    launcher.init_page()
    graphicalUserInterfaceElements['main'].addElement(
        __10x0=display.alterableText(string='Quedga Aspirin', size=(25, 6), color=(255, 255, 255),
                                     path=gameWindowFontPath, expend={}),
        __13x3=display.Button(string='>> 开始游戏 <<', size=(10, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"开始游戏\"按钮选项, 单击鼠标右键以确认进入游戏',
            '__check__': 'Warning: 当前选中于\"开始游戏\"按钮选项, 载入游戏页面中…',
            'sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __13x15=display.Button(string='    退出   ', size=(10, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"退出\"按钮选项, 单击鼠标任意键以退出或返回上级',
            '__check__': 'Warning: 执行退出或返回上级',
            'sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __3x5=display.rollSelector(string='游戏模式:', size=(5, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"游戏模式\"滚动选项器, 保持悬浮的同时单击鼠标以选择您要进行的游戏模式',
            '__check__': 'Warning: 当前选中于\"游戏模式\"滚动选项器, 上下滚动鼠标中间以此更换选项, 鼠标单击任意处已确认并终止选择',
            '__roll__': 'Tip: 当前选中于\"游戏模式\"滚动选项器, 单击鼠标中间或迅疾连续按下键盘箭头键以更改您的选择, 单击以保存您的设置',
            '__values__': launcher.game_pattern,
            '__describe__': 'PATTERN',
            'roll_sensitivity': hardware.timeControlSensitivityBuilder(rollSelectorSensitivity),
            'keyboard_sensitivity': hardware.timeControlSensitivityBuilder(keyboardSensitivity),
            'button_sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __3x7=display.rollSelector(string='地图长度:', size=(5, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"地图长度\"滚动选项器, 保持悬浮的同时单击鼠标以选择您的游戏的地图的逻辑长度',
            '__check__': 'Warning: 当前选中于\"地图长度\"滚动选项器, 上下滚动鼠标中间以此更换选项, 鼠标单击任意处已确认并终止选择',
            '__roll__': 'Tip: 当前选中于\"地图长度\"滚动选项器, 单击鼠标中间或迅疾连续按下键盘箭头键以更改您的选择, 单击以保存您的设置',
            '__values__': launcher.map_LENGTH,
            '__describe__': 'LENGTH',
            'roll_sensitivity': hardware.timeControlSensitivityBuilder(rollSelectorSensitivity),
            'keyboard_sensitivity': hardware.timeControlSensitivityBuilder(keyboardSensitivity),
            'button_sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __3x9=display.rollSelector(string='地图宽度:', size=(5, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"地图宽度\"滚动选项器, 保持悬浮的同时单击鼠标以选择您的游戏的地图的逻辑宽度',
            '__check__': 'Warning: 当前选中于\"地图宽度\"滚动选项器, 上下滚动鼠标中间以此更换选项, 鼠标单击任意处已确认并终止选择',
            '__roll__': 'Tip: 当前选中于\"地图宽度\"滚动选项器, 单击鼠标中间或迅疾连续按下键盘箭头键以更改您的选择, 单击以保存您的设置',
            '__values__': launcher.map_WIDTH,
            '__describe__': 'WIDTH',
            'roll_sensitivity': hardware.timeControlSensitivityBuilder(rollSelectorSensitivity),
            'keyboard_sensitivity': hardware.timeControlSensitivityBuilder(keyboardSensitivity),
            'button_sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __3x11=display.rollSelector(string='地图模板:', size=(5, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"地图模板\"滚动选项器, 保持悬浮的同时单击鼠标以选择您的游戏的地图的模板或者地图',
            '__check__': 'Warning: 当前选中于\"地图模板\"滚动选项器, 上下滚动鼠标中间以此更换选项, 鼠标单击任意处已确认并终止选择',
            '__roll__': 'Tip: 当前选中于\"地图模板\"滚动选项器, 单击鼠标中间或迅疾连续按下键盘箭头键以更改您的选择, 单击以保存您的设置',
            '__values__': launcher.map_TEMPLATE,
            '__describe__': 'TEMPLATE',
            'roll_sensitivity': hardware.timeControlSensitivityBuilder(rollSelectorSensitivity),
            'keyboard_sensitivity': hardware.timeControlSensitivityBuilder(keyboardSensitivity),
            'button_sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __3x13=display.rollSelector(string='生成算法:', size=(5, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"生成算法\"滚动选项器, 保持悬浮的同时单击鼠标以选择您的游戏的地图所使用的生成算法',
            '__check__': 'Warning: 当前选中于\"生成算法\"滚动选项器, 上下滚动鼠标中间以此更换选项, 鼠标单击任意处已确认并终止选择',
            '__roll__': 'Tip: 当前选中于\"生成算法\"滚动选项器, 单击鼠标中间或迅疾连续按下键盘箭头键以更改您的选择, 单击以保存您的设置',
            '__values__': launcher.map_GENERATING,
            '__describe__': 'GENERATING',
            'roll_sensitivity': hardware.timeControlSensitivityBuilder(rollSelectorSensitivity),
            'keyboard_sensitivity': hardware.timeControlSensitivityBuilder(keyboardSensitivity),
            'button_sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __18x5=display.rollSelector(string='插件状态:', size=(5, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"插件状态\"滚动选项器, 保持悬浮的同时单击鼠标以选择启用您所选择携带的插件',
            '__check__': 'Warning: 当前选中于\"插件状态\"滚动选项器, 上下滚动鼠标中间以此更换选项, 鼠标单击任意处已确认并终止选择',
            '__roll__': 'Tip: 当前选中于\"插件状态\"滚动选项器, 单击鼠标中间或迅疾连续按下键盘箭头键以更改您的选择, 单击以保存您的设置',
            '__values__': launcher.is_Plug,
            '__describe__': 'isUsingPlug',
            'roll_sensitivity': hardware.timeControlSensitivityBuilder(rollSelectorSensitivity),
            'keyboard_sensitivity': hardware.timeControlSensitivityBuilder(keyboardSensitivity),
            'button_sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __18x7=display.rollSelector(string='实时记录:', size=(5, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"实时记录\"滚动选项器, 保持悬浮的同时单击鼠标以选择启用实时记录功能以便您回顾整个对局',
            '__check__': 'Warning: 当前选中于\"实时记录\"滚动选项器, 上下滚动鼠标中间以此更换选项, 鼠标单击任意处已确认并终止选择',
            '__roll__': 'Tip: 当前选中于\"实时记录\"滚动选项器, 单击鼠标中间或迅疾连续按下键盘箭头键以更改您的选择, 单击以保存您的设置',
            '__values__': launcher.realTime_recording,
            '__describe__': 'RealTimeRECODING',
            'roll_sensitivity': hardware.timeControlSensitivityBuilder(rollSelectorSensitivity),
            'keyboard_sensitivity': hardware.timeControlSensitivityBuilder(keyboardSensitivity),
            'button_sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __18x9=display.rollSelector(string='初始步数:', size=(5, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"初始步数\"滚动选项器, 保持悬浮的同时单击鼠标以选择您游戏的初始步数',
            '__check__': 'Warning: 当前选中于\"初始步数\"滚动选项器, 上下滚动鼠标中间以此更换选项, 鼠标单击任意处已确认并终止选择',
            '__roll__': 'Tip: 当前选中于\"初始步数\"滚动选项器, 单击鼠标中间或迅疾连续按下键盘箭头键以更改您的选择, 单击以保存您的设置',
            '__values__': launcher.init_step,
            '__describe__': 'INIT_STEP',
            'roll_sensitivity': hardware.timeControlSensitivityBuilder(rollSelectorSensitivity),
            'keyboard_sensitivity': hardware.timeControlSensitivityBuilder(keyboardSensitivity),
            'button_sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __18x11=display.rollSelector(string='收缩速率:', size=(5, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"收缩速率\"滚动选项器, 保持悬浮的同时单击鼠标以选择您游戏中地图的收缩率',
            '__check__': 'Warning: 当前选中于\"收缩速率\"滚动选项器, 上下滚动鼠标中间以此更换选项, 鼠标单击任意处已确认并终止选择',
            '__roll__': 'Tip: 当前选中于\"收缩速率\"滚动选项器, 单击鼠标中间或迅疾连续按下键盘箭头键以更改您的选择, 单击以保存您的设置',
            '__values__': launcher.map_SHRINK,
            '__describe__': 'SHRINK',
            'roll_sensitivity': hardware.timeControlSensitivityBuilder(rollSelectorSensitivity),
            'keyboard_sensitivity': hardware.timeControlSensitivityBuilder(keyboardSensitivity),
            'button_sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        __18x13=display.Button(string='查看插件选项', size=(5, 3), color=(255, 55, 55), path=gameWindowFontPath, expend={
            'pusher': graphicalUserInterfaceElements['pusher'],
            '__hover__': 'Warning: 当前悬浮于\"> 查看插件选项 <\"按钮选项, 单击鼠标右键以确认进入插件携带选项页面',
            '__check__': 'Warning: 当前选中于\"> 查看插件选项 <\"按钮选项, 载入插件页面中…',
            'sensitivity': hardware.timeControlSensitivityBuilder(buttonSensitivity),
        }),
        )
    graphicalUserInterfaceElements['main'].updateDisplay(gameWindow)
    time.sleep(hardware.timeControlSensitivityBuilder(buttonSensitivity))


graphicalUserInterfaceElements['start'] = display.layoutElement(coordinate=(0, 0), size=(32, 18),
                                                                unit=('value:@back=0', 'value:@back=0'),
                                                                windowSize=(gameWindowLength, gameWindowWidth),
                                                                isOverlay=False)
graphicalUserInterfaceElements['start'].addElement(
    __9x6=display.alterableText(string='Quedga Aspirin ', size=(30, 16), color=(255, 255, 255), path=gameWindowFontPath,
                                expend={}),
    __20x8=display.alterableText(string=' Official 2.3.12Beta Edition', size=(16, 4), color=(255, 255, 255),
                                 path=gameWindowFontPath, expend={}),
    __1x17=display.alterableText(string='原创作者/Authorship：@Yawek、@Link   ', size=(16, 4), color=(255, 55, 255),
                                 path=gameWindowFontPath, expend={}),
    __12x17=display.alterableText(string='美术制作/Art Production：@Link       ', size=(16, 4), color=(55, 255, 255),
                                  path=gameWindowFontPath, expend={}),
    __22x17=display.alterableText(string='程序编写/Programming：@Link         ', size=(16, 4), color=(255, 255, 55),
                                  path=gameWindowFontPath, expend={}),
    __0x0=display.alterableText(string='保留版权所有 | All rights reserved', size=(10, 3), color=(255, 55, 55),
                                path=gameWindowFontPath, expend={})
)
graphicalUserInterfaceElements['start'].updateDisplay(gameWindow)
graphicalUserInterfaceElements['pusher'] = display.tipsMessagesPusher(gameWindow, gameWindowTipFont)
graphicalUserInterfaceElements['pusher'].updateTipAppend('（按空格键继续 或 点击鼠标）')
graphicalUserInterfaceElements['pusher'].pushGroup(
    [f'{SYSTEM}:初始化窗口', f'{SYSTEM}:初始化字体文件', f'{SYSTEM}:初始化配置文件',
     f'{SYSTEM}:读取目录文件'] +
    handle.traverse_filesFormat(os.getcwd()) + [f'{SYSTEM}:初始化常量'] +
    [f'Init:Computing a constant called {x} that we need to compute' for x in list(dir(file))+list(dir(handle))+list(dir(__handle))] +
    [f'{SYSTEM}:初始化布局器', f'{SYSTEM}:初始化资源路径', f'{SYSTEM}:就绪'], 1)
handle.temp = []


# 开屏项目
while True:
    basicEventProcessing()
    updateFrame()  # 更新帧
    pygame.display.flip()  # 刷新渲染
    if (keys_pressed[pygame.K_SPACE] or mouseDown) and not graphicalUserInterfaceElements['pusher'].stringList != []:
        break


gameWindow = pygame.display.set_mode(size=(gameWindowLength, gameWindowWidth), flags=flag, depth=36)  # 重新初始化窗口
gameWindow.fill(display.backgroundColor)
pygame.display.flip()
graphicalUserInterfaceElements['start'].clear()
del graphicalUserInterfaceElements['start']
graphicalUserInterfaceElements['main'] = display.layoutElement(coordinate=(0, 0), size=(32, 18),
                                                               unit=('value:@back=0', 'value:@back=0'),
                                                               windowSize=(gameWindowLength, gameWindowWidth),
                                                               isOverlay=False)
mainPageConfig()


# 正式项目
while True:
    basicEventProcessing()
    updateFrame()  # 更新帧
    pygame.display.flip()  # 刷新渲染

    # 游戏选项页面
    if graphicalUserInterfaceElements['main'].includingObjects['13x3'].value:
        graphicalUserInterfaceElements['main'].clear()
        gamePageConfig()
        while True:
            basicEventProcessing()
            updateFrame()  # 更新帧
            pygame.display.flip()  # 刷新渲染

            # 单人游戏选项页面
            if graphicalUserInterfaceElements['main'].includingObjects['13x3'].value:
                graphicalUserInterfaceElements['main'].clear()
                while True:
                    basicEventProcessing()
                    updateFrame()  # 更新帧
                    pygame.display.flip()  # 刷新渲染

            # 多人选项页面
            if graphicalUserInterfaceElements['main'].includingObjects['13x6'].value:
                tempConfigparser = configparser.ConfigParser()
                tempConfigparser.read(fileInformation['gamelaunchconfig'])
                launcher = gameLauncher(jsonFile_path=tempConfigparser["launch"]["multiplePersonGamePage"], pusher=graphicalUserInterfaceElements['pusher'])
                del tempConfigparser
                graphicalUserInterfaceElements['main'].clear()
                gameInformation: dict = {}
                multiplePersonsGamePageConfig(launcher=launcher)

                while True:
                    basicEventProcessing()
                    updateFrame()  # 更新帧
                    pygame.display.flip()  # 刷新渲染

                    # 开始游戏
                    if graphicalUserInterfaceElements['main'].includingObjects['13x3'].value:
                        gameInformation = launcher.get_gameInformation(graphicalUserInterfaceElement=graphicalUserInterfaceElements['main'])
                        graphicalUserInterfaceElements['main'].clear()
                        game_map: tileMap = tileMap(
                            size=gameInformation['SIZE'],
                            head=(int(gameWindowLength * 5 / 11), int(gameWindowWidth * 5 / 34)),
                            map_=generating.narrowRandom_CreationNumberTile(
                                range_info=file.readJson(r"./Data/Map/RandomGenerating/narrowRandom.numberTiles.json"),
                                scalingRatio=generating.scalingRatio(
                                    window_size=SIZE,
                                    leave_white=(5 / 11, 5 / 34),
                                    map_size=gameInformation['SIZE'],
                                    unit=30
                                ),
                                length=gameInformation['LENGTH'] * gameInformation['WIDTH']
                            ),
                            IToI=file.readJson(r"./Data/Map/mapIndexToImage.json"),
                            unit=generating.now_scalingRatio
                        )
                        while True:
                            basicEventProcessing()
                            updateFrame()  # 更新帧
                            pygame.display.flip()  # 刷新渲染

                    # 执行返回上级
                    if graphicalUserInterfaceElements['main'].includingObjects['13x15'].value:
                        gameInformation: dict = {}
                        gamePageConfig()
                        break

            # 联机对局对局选项页面
            if graphicalUserInterfaceElements['main'].includingObjects['13x9'].value:
                graphicalUserInterfaceElements['main'].clear()
                while True:
                    basicEventProcessing()
                    updateFrame()  # 更新帧
                    pygame.display.flip()  # 刷新渲染

            # 执行返回上级
            if graphicalUserInterfaceElements['main'].includingObjects['13x12'].value:
                mainPageConfig()
                break

    # 设置选项页面
    if graphicalUserInterfaceElements['main'].includingObjects['13x6'].value:
        graphicalUserInterfaceElements['main'].clear()
        while True:
            basicEventProcessing()
            updateFrame()  # 更新帧
            pygame.display.flip()  # 刷新渲染

    # 更多选项页面
    if graphicalUserInterfaceElements['main'].includingObjects['13x9'].value:
        graphicalUserInterfaceElements['main'].clear()
        while True:
            basicEventProcessing()
            updateFrame()  # 更新帧
            pygame.display.flip()  # 刷新渲染

    # 执行退出
    if graphicalUserInterfaceElements['main'].includingObjects['13x12'].value:
        exit()

