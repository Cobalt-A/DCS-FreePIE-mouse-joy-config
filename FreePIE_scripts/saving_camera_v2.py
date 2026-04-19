# =====================================================
# --- Cкрипт мышеджойстика с сохранением камеры FreePIE Cobalt'а - для DCS ---
# - saving_camera_v2 - отличается от saving_camera_v1 тем что дополнительно имеет возможность обзора с сохранением камеры так и без
# =====================================================
# --- ВНИМАНИЕ !!! ---
# - VJoy: требует 2 включеных виртуальных джойстика
# vJoy[0] с включенными осями X, Y, Z, SLIDER и включенными кнопками скрипт по дефолту работает с 5
# vJoy[1] с включенными осями X, Y, Z, RX, RY
# - FreePIE: скрипт должен запускаться в среде FreePIE
# - Opentrack: конфиг и скрины с настройками можно посмотреть на github
# =====================================================
# --- Оси виртуального джостика (vJoy[0]) (могут быть переназначены по желанию) ---
# - Оси X,Y - оси мышеджоя (крен, тангаж)
# - Ось Z - ось рысканья
# - Ось SLIDER - ось РУД
# =====================================================
# --- Оси виртуального джостика (vJoy[1]) (могут быть переназначены по желанию) ---
# - Оси X,Y - оси смещения обзора
# - Ось Z - ось приближения
# - Оси RX, RY - оси обзора
# =====================================================
# --- Кнопки виртуального джостика vJoy[0] повторяют кнопки мыши по дефолту кнопок 5 (могут быть переназначены по желанию) ---
# - Центральная кнопка мыши центрирует курсор/мышеджой
# =====================================================
# --- Клавиши управления (могут быть переназначены по желанию) ---
# - TAB - принудительное выключение мышеджоя (его оси переходят на обзор)
# - Home - переключение блокировки клавиатурного ввода (мышеджой должен быть выключен)
# - F10 - блокирует любой ввод, может быть разблокирован клавиатурный ввод клавишами: Home, F1
# - F1 - разблокирует клавиатурный ввод в случаи если ввод был заблокирован клавишей F10
# - V - включает мышеджой, удержание кнопку включает обзор
# - C - включает мышеджой и центрирует обзор на прицел, удержание кнопку включает обзор
# - F - Центрирует взгляд по оси X
# - W, S - тяга
# - A, D - крен по клавиатуре на максимальное значение
# - LeftCtrl, LeftShift - тангаж по клавиатуре на максимальное значение
# - Q, E - рысканье по клавиатуре на максимальное значение
# - 5, 6, 7, 8, 9 - перемещение обзора в определенную точку без выключения мышеджоя: вверх, вниз, вправо, влево, назад
# - 1, 2, 4, 4 - смещение обзора по кабине: верх, вниз, вправо, влево
# =====================================================

# Начало скрипта управления
from ctypes import windll, Structure, c_ulong, byref
import operator

# Инициализация констант и стартовых значений,
# все не вычисляемые переемные должны задаваться в этом блоке
if starting:

    class POINT(Structure):
        _fields_ = [("x", c_ulong), ("y", c_ulong)]

    # Функция плавного изменения оси, если достигнут предел возвращает флаг = False
    def change_axis(current_value, op, max_value, sensitivity):
        new_value = current_value + sensitivity
        if op(max_value, new_value):
            return [new_value, True]
        else:
            return [max_value, False]

    # Функция плавного возвращения оси в назначенное значение
    def return_axis_to_value(current_value, target_value, sensitivity):
        if current_value > target_value:
            return change_axis(current_value, operator.lt, -target_value, -sensitivity)
        else:
            return change_axis(current_value, operator.gt, target_value, sensitivity)

    # Необходимые технические константы
    CURSOR = POINT()
    VJOY_RANGE = 32768
    MAX_VJOY_VALUE = VJOY_RANGE / 2
    SCREEN_X = windll.user32.GetSystemMetrics(0)
    SCREEN_Y = windll.user32.GetSystemMetrics(1)

    # Количество кнопок vjoy
    VJOY_NUMBER_BUTTONS = 5

    # Максимальное смещение, opentrack достигает максимального смещения уже на 5000
    MAX_VIEW_OFFSET_VALUE = 5000

    # Размеры мышеджоя в px
    MOUSE_JOY_WIDTH = 1500
    MOUSE_JOY_HEIGHT = SCREEN_Y

    # Формула множителя для перевода координат курсора в значения мышеджоя
    MULTIPLE_X = VJOY_RANGE / MOUSE_JOY_WIDTH
    MULTIPLE_Y = VJOY_RANGE / MOUSE_JOY_HEIGHT

    # Чувствительность обзора с мышки и приближения
    VIEW_SENSITIVITY = 1
    FAST_VIEW_SENSITIVITY = 5
    Z_SENSITIVITY = 11

    # Чувствительность изменения осей по клавиатуре
    KEYBOARD_PITCH_SENSITIVITY = 500
    KEYBOARD_ROLL_SENSITIVITY = 500
    KEYBOARD_YAW_SENSITIVITY = 500
    CHANGE_X_VIEW_SENSITIVITY = 500
    CHANGE_Y_VIEW_SENSITIVITY = 100
    CHANGE_TRUST_SENSITIVITY = 500
    
    # Ограничения изменения осей с клавиатуры
    MAX_KEYBOARD_PITCH_VALUE = MAX_VJOY_VALUE
    MAX_KEYBOARD_ROLL_VALUE = MAX_VJOY_VALUE
    MAX_X_VIEW_OFFSET_VALUE = 2500 # максимального отклонение opentrack достигает уже на 5000
    MAX_POSITIVE_Y_VIEW_OFFSET_VALUE = 5000
    MAX_NEGATIVE_Y_VIEW_OFFSET_VALUE = 2500

    # Клавиша включения мышеджоя и обзора при удержании
    MOUSE_VJOY_TOGGLE_BUTTON = Key.C

    # Клавиша включения мышеджоя и обзора при удержании с сохранением камеры
    MOUSE_VJOY_UNEBALE_FORCED_BUTTON = Key.Tab
    
    # Клавиша центрирования взгляда
    CENTER_VIEW_BUTTON = Key.RightShift

    # Клавиша включения обзора с сохранением вида
    MOUSE_VJOY_TOGGLE_SAVE_VIEW_BUTTON = Key.V

    # Клавиша центрирования взгляда по оси x
    CENTER_VIEW_X_BUTTON = Key.F

    # Клавиша блокировки ввода
    BLOCK_INPUT_BUTTON = Key.Home
    
    # Клавиша блокировки ввода по карте
    BLOCK_MAP_INPUT_BUTTON = Key.F10

    # Клавиша разблокировки ввода карты
    UNBLOCK_MAP_INPUT_BUTTON = Key.F1

    # Клавиши обзора
    VIEW_UP_BUTTON = Key.D1
    VIEW_DOWN_BUTTON = Key.D2
    VIEW_LEFT_BUTTON = Key.D3
    VIEW_RIGHT_BUTTON = Key.D4
    VIEW_BACK_BUTTON = Key.D5

    # Клавиши смещения вверх/вниз
    VIEW_OFFSET_UP_BUTTON = Key.D6
    VIEW_OFFSET_DOWN_BUTTON = Key.D7

    # Клавиши смещения лево/право
    VIEW_OFFSET_LEFT_BUTTON = Key.D8
    VIEW_OFFSET_RIGHT_BUTTON = Key.D9

    # Клавиши рысканья
    YAW_UP_BUTTON = Key.E
    YAW_DOWN_BUTTON = Key.Q

    # Клавиши тангажа
    PITCH_DOWN_BUTTON = Key.LeftShift
    PITCH_UP_BUTTON = Key.LeftControl

    # Клавиши крена
    ROLL_LEFT_BUTTON = Key.A
    ROLL_RIGHT_BUTTON = Key.D

    # Клавиши тяги
    TRUST_UP_BUTTON = Key.W
    TRUST_DOWN_BUTTON = Key.S

    # Инициализация осей
    vJoy[0].x = 0
    vJoy[0].y = 0
    vJoy[0].z = 0
    vJoy[0].slider = 0
    vJoy[1].z = 0
    vJoy[1].rx = 0
    vJoy[1].ry = 0
    vJoy[1].x = 0
    vJoy[1].y = 0
    saved_x_joy = vJoy[0].x
    saved_y_joy = vJoy[0].y

    # Инициализация координат мышеджоя
    mouse_vjoy_x = windll.user32.GetSystemMetrics(0) / 2
    mouse_vjoy_y = windll.user32.GetSystemMetrics(1) / 2

    # Логические флаги для работы логи
    is_mouse_vjoy_active = True
    is_mouse_vjoy_active_save_view = False
    is_mouse_vjoy_unenable = False
    is_keyboard_joy_x_enabled = False
    is_keyboard_joy_y_enabled = False
    is_keyboard_x_view_active = False
    is_keyboard_y_view_active = False
    is_input_block = False
    is_input_block_by_map = False
    is_keyboard_z_enabled = False
    is_keyboard_offset_x_active = False

# Назначение кнопок мышеджоя
for i in range(VJOY_NUMBER_BUTTONS - 1):
    if mouse.getButton(i + 1):
        vJoy[0].setButton(i + 1, True)
    else:
        vJoy[0].setButton(i + 1, False)

# Кнопки обзора
if keyboard.getKeyDown(VIEW_UP_BUTTON) and is_mouse_vjoy_active:
    is_keyboard_y_view_active = True
    vJoy[1].ry = 4000
    if not is_keyboard_x_view_active:
        vJoy[1].rx = 0
    else:
        is_keyboard_x_view_active = False

if keyboard.getKeyDown(VIEW_BACK_BUTTON) and is_mouse_vjoy_active:
    is_keyboard_x_view_active = True
    vJoy[1].rx = 15000

if keyboard.getKeyDown(VIEW_LEFT_BUTTON) and is_mouse_vjoy_active:
    is_keyboard_x_view_active = True
    vJoy[1].rx = 6400

if keyboard.getKeyDown(VIEW_RIGHT_BUTTON) and is_mouse_vjoy_active:
    is_keyboard_x_view_active = True
    vJoy[1].rx = -6400

if keyboard.getKeyDown(VIEW_DOWN_BUTTON) and is_mouse_vjoy_active:
    is_keyboard_y_view_active = True
    vJoy[1].ry = -1500

# Кнопки смещения обзора
if keyboard.getKeyDown(VIEW_OFFSET_DOWN_BUTTON):
    [new_value, flag] = change_axis(
        vJoy[1].y, operator.lt, -MAX_NEGATIVE_Y_VIEW_OFFSET_VALUE, -CHANGE_Y_VIEW_SENSITIVITY
    )
    vJoy[1].y = new_value

if keyboard.getKeyDown(VIEW_OFFSET_UP_BUTTON):
    [new_value, flag] = change_axis(
        vJoy[1].y, operator.gt, MAX_POSITIVE_Y_VIEW_OFFSET_VALUE, CHANGE_Y_VIEW_SENSITIVITY
    )
    vJoy[1].y = new_value

if keyboard.getKeyDown(VIEW_OFFSET_LEFT_BUTTON):
    [new_value, flag] = change_axis(
        vJoy[1].x, operator.gt, MAX_X_VIEW_OFFSET_VALUE, CHANGE_X_VIEW_SENSITIVITY
    )
    vJoy[1].x = new_value
    if not is_keyboard_offset_x_active:
        is_keyboard_offset_x_active = True

if keyboard.getKeyDown(VIEW_OFFSET_RIGHT_BUTTON):
    [new_value, flag] = change_axis(
        vJoy[1].x, operator.lt, -MAX_X_VIEW_OFFSET_VALUE, -CHANGE_X_VIEW_SENSITIVITY
    )
    vJoy[1].x = new_value
    if not is_keyboard_offset_x_active:
        is_keyboard_offset_x_active = True

# Возврат смещения по оси X
if (
    not keyboard.getKeyDown(VIEW_OFFSET_RIGHT_BUTTON)
    and not keyboard.getKeyDown(VIEW_OFFSET_LEFT_BUTTON)
    and is_keyboard_offset_x_active
):
    [new_value, flag] = return_axis_to_value(vJoy[1].x, 0, CHANGE_X_VIEW_SENSITIVITY)
    vJoy[1].x = new_value
    is_keyboard_offset_x_active = flag

# Кнопки обзора
if (
    keyboard.getKeyDown(MOUSE_VJOY_TOGGLE_BUTTON)
    and is_mouse_vjoy_active
    and not is_mouse_vjoy_unenable
):
    is_mouse_vjoy_active = False
    is_mouse_vjoy_active_save_view = False
    if is_keyboard_x_view_active:
        is_keyboard_x_view_active = False
    if is_keyboard_y_view_active:
        is_keyboard_y_view_active = False

if (
    keyboard.getKeyDown(MOUSE_VJOY_TOGGLE_SAVE_VIEW_BUTTON)
    and is_mouse_vjoy_active
    and not is_mouse_vjoy_unenable
):
    is_mouse_vjoy_active = False
    is_mouse_vjoy_active_save_view = True
    if is_keyboard_x_view_active:
        is_keyboard_x_view_active = False
    if is_keyboard_y_view_active:
        is_keyboard_y_view_active = False

# Включение мышеджоя с центрирование камеры
if (
    not is_input_block
    and keyboard.getKeyUp(MOUSE_VJOY_TOGGLE_BUTTON)
    and not keyboard.getKeyDown(MOUSE_VJOY_TOGGLE_SAVE_VIEW_BUTTON)
    and not is_mouse_vjoy_active
    and not is_mouse_vjoy_unenable
):
    is_mouse_vjoy_active = True

    if not is_mouse_vjoy_active_save_view:
        vJoy[1].rx = 0
        vJoy[1].ry = 0

    windll.user32.SetCursorPos(mouse_vjoy_x, mouse_vjoy_y)

# Принудительное выключение мышеджоя
if keyboard.getPressed(MOUSE_VJOY_UNEBALE_FORCED_BUTTON):
    is_mouse_vjoy_unenable = True
    is_mouse_vjoy_active = False

# Принудительное включение мышеджоя с центрирование камеры
if (
    not is_input_block
    and is_mouse_vjoy_unenable
    and keyboard.getPressed(MOUSE_VJOY_TOGGLE_BUTTON)
):
    is_mouse_vjoy_unenable = False
    is_mouse_vjoy_active = True
    if not is_mouse_vjoy_active_save_view:
        vJoy[1].rx = 0
        vJoy[1].ry = 0
    windll.user32.SetCursorPos(mouse_vjoy_x, mouse_vjoy_y)

# Принудительное включение мышеджоя с сохранением камеры
if (
    not is_input_block
    and is_mouse_vjoy_unenable
    and keyboard.getPressed(MOUSE_VJOY_TOGGLE_SAVE_VIEW_BUTTON)
):
    is_mouse_vjoy_unenable = False
    is_mouse_vjoy_active = True
    windll.user32.SetCursorPos(mouse_vjoy_x, mouse_vjoy_y)

# Центрирование курсора
if mouse.middleButton:
    windll.user32.SetCursorPos(SCREEN_X / 2, SCREEN_Y / 2)
    if is_mouse_vjoy_active:
        vJoy[0].x = 0
        vJoy[0].y = 0

# Блокировка ввода
if is_mouse_vjoy_unenable and keyboard.getPressed(BLOCK_INPUT_BUTTON):
    is_input_block = not is_input_block
    
if keyboard.getPressed(BLOCK_MAP_INPUT_BUTTON) and not is_input_block:
    is_mouse_vjoy_unenable = True
    is_input_block = True
    is_input_block_by_map = True

if keyboard.getPressed(UNBLOCK_MAP_INPUT_BUTTON) and is_input_block_by_map:
    is_mouse_vjoy_unenable = True
    is_input_block = False
    is_input_block_by_map = False

# Логика работы мышеджоя
if is_mouse_vjoy_active:
    windll.user32.GetCursorPos(byref(CURSOR))
    mouse_vjoy_x = CURSOR.x
    mouse_vjoy_y = CURSOR.y

    new_x_value = (mouse_vjoy_x - (SCREEN_X / 2)) * MULTIPLE_X
    if new_x_value > MAX_VJOY_VALUE:
        new_x_value = MAX_VJOY_VALUE
    if new_x_value < -MAX_VJOY_VALUE:
        new_x_value = -MAX_VJOY_VALUE
    saved_x_joy = new_x_value

    if not is_keyboard_joy_x_enabled:
        vJoy[0].x = new_x_value

    new_y_value = (mouse_vjoy_y - (SCREEN_Y / 2)) * MULTIPLE_Y
    if new_y_value > MAX_VJOY_VALUE:
        new_y_value = MAX_VJOY_VALUE
    if new_y_value < -MAX_VJOY_VALUE:
        new_y_value = -MAX_VJOY_VALUE
    saved_y_joy = new_y_value

    if not is_keyboard_joy_y_enabled:
        vJoy[0].y = new_y_value

    # ЛКМ работает только при включенном мышеджое, чтобы не было случайных выстрелов (если на ЛКМ назначена гашетка)
    # если на ЛКМ гашетки нет можно выносить из блока if, для использовании ЛКМ без включения мышеджоя
    if mouse.leftButton:
        vJoy[0].setButton(0, True)
    else:
        vJoy[0].setButton(0, False)

# Ось приближения
vJoy[1].z += mouse.wheel * Z_SENSITIVITY
if vJoy[1].z >= MAX_VJOY_VALUE:
    vJoy[1].z = MAX_VJOY_VALUE
if vJoy[1].z <= -MAX_VJOY_VALUE:
    vJoy[1].z = -MAX_VJOY_VALUE

# Крен влево с клавиатуры
if not is_input_block and keyboard.getKeyDown(ROLL_LEFT_BUTTON):
    [new_value, flag] = change_axis(
        vJoy[0].x, operator.lt, -MAX_KEYBOARD_ROLL_VALUE, -KEYBOARD_ROLL_SENSITIVITY
    )
    vJoy[0].x = new_value
    if not is_keyboard_joy_x_enabled:
        is_keyboard_joy_x_enabled = True

# Крен право с клавиатуры
if not is_input_block and keyboard.getKeyDown(ROLL_RIGHT_BUTTON):
    [new_value, flag] = change_axis(
        vJoy[0].x, operator.gt, MAX_KEYBOARD_ROLL_VALUE, KEYBOARD_ROLL_SENSITIVITY
    )
    vJoy[0].x = new_value
    if not is_keyboard_joy_x_enabled:
        is_keyboard_joy_x_enabled = True

# Тангаж вниз с клавиатуры
if not is_input_block and keyboard.getKeyDown(PITCH_DOWN_BUTTON):
    [new_value, flag] = change_axis(
        vJoy[0].y, operator.lt, -MAX_KEYBOARD_PITCH_VALUE, -KEYBOARD_PITCH_SENSITIVITY
    )
    vJoy[0].y = new_value
    if not is_keyboard_joy_y_enabled:
        is_keyboard_joy_y_enabled = True

# Тангаж вверх с клавиатуры
if not is_input_block and keyboard.getKeyDown(PITCH_UP_BUTTON):
    [new_value, flag] = change_axis(
        vJoy[0].y, operator.gt, MAX_KEYBOARD_PITCH_VALUE, KEYBOARD_PITCH_SENSITIVITY
    )
    vJoy[0].y = new_value
    if not is_keyboard_joy_y_enabled:
        is_keyboard_joy_y_enabled = True

# Возврат положения крена джоя
if (
    not keyboard.getKeyDown(ROLL_RIGHT_BUTTON)
    and not keyboard.getKeyDown(ROLL_LEFT_BUTTON)
    and is_keyboard_joy_x_enabled
):
    [new_value, flag] = return_axis_to_value(
        vJoy[0].x, saved_x_joy, KEYBOARD_ROLL_SENSITIVITY
    )
    vJoy[0].x = new_value
    is_keyboard_joy_x_enabled = flag

# Возврат положения тангажа джоя
if (
    not keyboard.getKeyDown(PITCH_UP_BUTTON)
    and not keyboard.getKeyDown(PITCH_DOWN_BUTTON)
    and is_keyboard_joy_y_enabled
):
    [new_value, flag] = return_axis_to_value(
        vJoy[0].y, saved_y_joy, KEYBOARD_PITCH_SENSITIVITY
    )
    vJoy[0].y = new_value
    is_keyboard_joy_y_enabled = flag

# Рысканье вправо
if not is_input_block and keyboard.getKeyDown(YAW_UP_BUTTON):
    [new_value, flag] = change_axis(
        vJoy[0].z, operator.gt, MAX_VJOY_VALUE, KEYBOARD_YAW_SENSITIVITY
    )
    vJoy[0].z = new_value
    if not is_keyboard_z_enabled:
        is_keyboard_z_enabled = True

# Рысканье влево
if not is_input_block and keyboard.getKeyDown(YAW_DOWN_BUTTON):
    [new_value, flag] = change_axis(
        vJoy[0].z, operator.lt, -MAX_VJOY_VALUE, -KEYBOARD_YAW_SENSITIVITY
    )
    vJoy[0].z = new_value
    if not is_keyboard_z_enabled:
        is_keyboard_z_enabled = True

# Возврат положения рысканья
if (
    not keyboard.getKeyDown(YAW_DOWN_BUTTON)
    and not keyboard.getKeyDown(YAW_UP_BUTTON)
    and is_keyboard_z_enabled
):
    [new_value, flag] = return_axis_to_value(vJoy[0].z, 0, KEYBOARD_YAW_SENSITIVITY)
    vJoy[0].z = new_value
    is_keyboard_z_enabled = flag

# Тяга вверх
if not is_input_block and keyboard.getKeyDown(TRUST_DOWN_BUTTON):
    [new_value, flag] = change_axis(
        vJoy[0].slider, operator.gt, MAX_VJOY_VALUE, CHANGE_TRUST_SENSITIVITY
    )
    vJoy[0].slider = new_value

# Тяга вниз
if not is_input_block and keyboard.getKeyDown(TRUST_UP_BUTTON):
    [new_value, flag] = change_axis(
        vJoy[0].slider, operator.lt, -MAX_VJOY_VALUE, -CHANGE_TRUST_SENSITIVITY
    )
    vJoy[0].slider = new_value

# Центрирование взгляда по оси x
if keyboard.getKeyDown(CENTER_VIEW_X_BUTTON):
    vJoy[1].rx = 0
    
# Центрирование взгляда
if keyboard.getKeyDown(CENTER_VIEW_BUTTON):
    vJoy[1].rx = 0
    vJoy[1].ry = 0

# Обзор с мышки
if not is_mouse_vjoy_active:
    if not is_mouse_vjoy_unenable:
        vJoy[1].rx = vJoy[1].rx - mouse.deltaX * FAST_VIEW_SENSITIVITY
        vJoy[1].ry = vJoy[1].ry - mouse.deltaY * FAST_VIEW_SENSITIVITY
    else:
        vJoy[1].rx = vJoy[1].rx - mouse.deltaX * VIEW_SENSITIVITY
        vJoy[1].ry = vJoy[1].ry - mouse.deltaY * VIEW_SENSITIVITY

# диагностические значения
diagnostics.watch(is_mouse_vjoy_active)
diagnostics.watch(is_mouse_vjoy_active_save_view)
diagnostics.watch(vJoy[0].x)
diagnostics.watch(vJoy[0].y)
diagnostics.watch(vJoy[0].z)
diagnostics.watch(vJoy[0].slider)
diagnostics.watch(vJoy[1].z)
diagnostics.watch(vJoy[1].rx)
diagnostics.watch(vJoy[1].ry)
diagnostics.watch(vJoy[1].x)
diagnostics.watch(vJoy[1].y)
diagnostics.watch(saved_x_joy)
diagnostics.watch(saved_y_joy)
diagnostics.watch(SCREEN_X)
diagnostics.watch(mouse.deltaX)
diagnostics.watch(mouse.deltaY)
