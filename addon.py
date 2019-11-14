# -*- coding: utf-8 -*-
# Module: smarthome
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import os, urllib2, json
import xbmc, xbmcaddon, xbmcgui

__author__ = 'DrHellp'
__date__ = '$10.12.2018 14:48:51$'

# Чтение параметров
__settings__ = xbmcaddon.Addon(id='script.module.smarthome')
__ipaddress__ = __settings__.getSetting('ipaddress')
__url_base__ = 'http://' + __ipaddress__ + '/api/'
__language__ = __settings__.getLocalizedString

# Получаем путь к плагину
_addon_path = __settings__.getAddonInfo('path').decode(sys.getfilesystemencoding())

# Указываем пути к картинкам и текстурам:
# фон
background_img = os.path.join(_addon_path, 'resources/media', 'background.jpg')
# фон дополнительного окна
background_windows = os.path.join(_addon_path, 'resources/media', 'windows.png')
# заголовок дополнительного окна
windows_header = os.path.join(_addon_path, 'resources/media', 'windows_header.png')
# текстура кнопки без фокуса
button_nf_img = os.path.join(_addon_path, 'resources/media', 'button_nf.png')
# текстура кнопки в фокусе
button_fo_img = os.path.join(_addon_path, 'resources/media', 'button_fo.png')
# Изображения датчиков
temperature_img = os.path.join(_addon_path, 'resources/media', 'temperature.png')
humidity_img = os.path.join(_addon_path, 'resources/media', 'humidity.png')
pressure_img = os.path.join(_addon_path, 'resources/media', 'pressure.png')

# Сопоставление расположений и переводов
__lang_location__ = {
    'Bedroom': 32104,
    'Cellar': 32105,
    'Garage': 32106,
    'Hall': 32107,
    'Hallway': 32108,
    'Kitchen': 32109,
    'Toilet': 32110,
    'Bathroom': 32111,
    'Livingroom': 32112,
    'Childrensroom': 32113,
    'Outdoors': 32114
}

# Сопоставление названий датчиков и переводов
__sensor_data__ = {
    'Humidity': 32120,
    'Pressure': 32121,
    'Temperature': 32122
}

# Цвета
_color_head = '0xFF000000'
_color_location = '0xFF000000'
_color_head_window = '0xFFFFFFFF'
_color_measure = '0xFFEB9E17'

# Функция для получения json данных
def get_json(url):
    conn = urllib2.urlopen(url)
    html = conn.read()
    conn.close()
    data_json = json.loads(html)

    return data_json

# Получаем список комнат
rooms_data  = get_json(__url_base__ + 'rooms')
rooms_list = rooms_data['rooms']

# Создаем список комнат с данными
rooms_data_list = {}

# Создаем список объектов для сортировки
rooms_obj = []
for room in rooms_list:
    # Поиск перевода
    room_translate = __language__(__lang_location__.get(room['object']))
    rooms_obj.append(room_translate)
    # Переведенное имя объекта
    title = room_translate
    # Получаем данные по каждой комнате
    room_data  = get_json(__url_base__ + 'data/' + room['object'])
    room_list = room_data['data']
    description = room_data['object']['description']
    rooms_data_list[title] = {'Description': description}
    # Проход по данным комнаты
    for data in room_list:
        if (room_list[data] != False and room_list[data] != '' and
                room_list[data] != '0' and data != 'LatestActivity' and
                data != 'LatestActivityTime' and data != 'Title'):
            rooms_data_list[title][data] = room_list[data]

rooms_obj.sort()
print rooms_data_list

# Коды клавиатурных действий
ACTION_PREVIOUS_MENU = 10 # По умолчанию - ESC
ACTION_NAV_BACK = 92 # По умолчанию - Backspace

# Главный класс-контейнер
class MyAddon(xbmcgui.Window):

    def __init__(self):
        # Устанавливаем фоновую картинку
        background = xbmcgui.ControlImage(1, 1, 1280, 720, background_img)
        self.addControl(background)

        # Основная надпись
        background = xbmcgui.ControlImage(30, 80, 300, 30, button_fo_img)
        self.addControl(background)
        self.strActionInfo = xbmcgui.ControlLabel(50, 80, 200, 30, '', 'font16', _color_head)
        self.addControl(self.strActionInfo)
        self.strActionInfo.setLabel(__language__(32103))

        # Окно данных
        background = xbmcgui.ControlImage(650, 150, 600, 30, windows_header)
        self.addControl(background)
        background = xbmcgui.ControlImage(650, 180, 600, 355, background_windows)
        self.addControl(background)

        # Список расположений
        self.list = xbmcgui.ControlList(30, 150, 600, 420, 'font14', buttonTexture=button_nf_img, buttonFocusTexture=button_fo_img, textColor=_color_location, _itemHeight=60, _space=5, _alignmentY=0x00000004)
        self.addControl(self.list)
        for loc in rooms_obj:
            self.list.addItem(loc)
        self.setFocus(self.list)

    def onAction(self, action):
        # Если нажали ESC или Backspace...
        if action == ACTION_NAV_BACK or action == ACTION_PREVIOUS_MENU:
            # ...закрываем плагин.
            self.close()

    def onControl(self, control):
        if control == self.list:
            item = self.list.getSelectedItem()
            key = item.getLabel()
            ukey = unicode(key, 'utf-8')
            key_exists = ukey in rooms_data_list
            if key_exists:
                self.message(ukey)

    # Вывод данных
    def message(self, message):
        # Поиск и вывод данных
        background = xbmcgui.ControlImage(650, 150, 600, 30, windows_header)
        self.addControl(background)
        background = xbmcgui.ControlImage(650, 180, 600, 355, background_windows)
        self.addControl(background)

        room = rooms_data_list[message]
        label = room['Description']
        self.headWindow = xbmcgui.ControlLabel(665, 155, 500, 300, label, 'font14', _color_head_window)
        self.addControl(self.headWindow)

        """ Вывод содержимого словаря с сортировкой по ключам:
        1 Создать список ключей словаря.
        2 Отсортировать его. (Списки в отличие от словарей сортировать можно.)
        3 Перебрать элементы списка, обращаясь по соответствующему ключу к элементу словаря. """

        room_sort = room.keys() # получаем ключи
        room_sort = list(room_sort) # превращаем его в обычный список
        room_sort.sort() # сортируем список

        i = 0
        for key in room_sort:
            if (key != 'Description'):
                measure = ''
                parameter = ''
                if (key == 'Humidity'):
                    measure = __language__(32130)
                    parameter = __language__(32120)
                if (key == 'Pressure'):
                    measure = __language__(32131)
                    parameter = __language__(32121)
                if (key == 'Temperature'):
                    measure = __language__(32132)
                    parameter = __language__(32122)
                label = xbmcgui.ControlLabel(665, 200+i, 200, 50, parameter, font='font16')
                self.addControl(label)
                label = xbmcgui.ControlLabel(865, 200+i, 200, 50, room[key] + ' ' + measure, font='font16', textColor=_color_measure)
                self.addControl(label)
                i = i + 30


if __name__ == '__main__':
    # Создаем экземпляр класса-контейнера.
    addon = MyAddon()
    # Выводим контейнер на экран.
    addon.doModal()
    # По завершении удаляем экземпляр.
    del addon
