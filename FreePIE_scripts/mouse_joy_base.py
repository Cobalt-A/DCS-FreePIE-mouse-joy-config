# =====================================================
# Cкрипт FreePIE Cobalt'а - для DCS
# мышеджойстик (ВНИМАНИЕ !!! требует ОДИН виртуальный джойстик vJoy + FreePIE + Opentrack)
# =====================================================
# --- Оси виртуального джостика vJoy[0] (могут быть переназначены по желанию) ---
# - Оси X,Y (vJoy[0]) - оси мышеджойстика (элероны, тангаж)
# - Оси RX,RY,Z (vJoy[0]) - оси для обзора
# - Ось (vJoy[0]) (rz) - ось рысканья
# =====================================================
# --- Кнопки виртуального джойстика vJoy[0] повторяют кнопки мыши по дефолту кнопок 5 (могут быть переназначены по желанию) ---
# =====================================================
# --- Клавиши управления (могут быть переназначены по желанию) ---
# - TAB - принудительное выключение мышеджоя (его оси переходят на обзор)
# - C включает мышеджой и центрирует обзор на прицел, удержание кнопку включает обзор
# - A,D - перемещение положение мышеджоя по крену на MAX_MOUSE_JOY_VALUE/2 относительного текущего положение мышеджоя
# - LeftCtrl, LeftShift - перемещение положение мышеджоя по тангажу на MAX_MOUSE_JOY_VALUE/2 относительного текущего положение мышеджоя
# - Enter - Центрирование обзора, Opentrack желательно включать после центрироваия обзора для правильной его работы
# =====================================================

# Начало скрипта управления
from ctypes import windll, Structure, c_ulong, byref

# Инициализация констант и стартовых значений,
# все не вычисляемые переемные должны задаваться в этом блоке
if starting:
	class POINT(Structure):
		_fields_ = [("x", c_ulong), ("y", c_ulong)]
	CURSOR = POINT()
	MAX_MOUSE_JOY_VALUE = 32768
	MAX_VIEW_VALUE = 13000
	VIEW_SENS = 1
	FAST_VIEW_SENS = 5
	Z_SENS = 11
	SCREEN_X = windll.user32.GetSystemMetrics(0)
	SCREEN_Y = windll.user32.GetSystemMetrics(1)

	# Размеры мышеджоя
	MOUSE_JOY_WIDTH = SCREEN_X
	MOUSE_JOY_HEIGHT = SCREEN_Y

	# Формула множителя для перевода координат курсора в значения мышеджоя
	MULTIPLE_X = MAX_MOUSE_JOY_VALUE / MOUSE_JOY_WIDTH
	MULTIPLE_Y = MAX_MOUSE_JOY_VALUE / MOUSE_JOY_HEIGHT

	vJoy[0].x = 0
	vJoy[0].y = 0
	vJoy[0].z = 0
	vJoy[0].rx = 0
	vJoy[0].ry = 0
	vJoy[0].rz = 0
	saved_x_joy = vJoy[0].x
	saved_y_joy = vJoy[0].y

	mouse_x = windll.user32.GetSystemMetrics(0)/2
	mouse_y = windll.user32.GetSystemMetrics(1)/2

	mouse_vjoy_is_enabled = False
	mouse_vjoy_toggle_key = Key.C
	mouse_vjoy_is_forced_unenable = True
	mouse_vJoy_unenable_forced_key = Key.Tab
	is_keyboard_joy_x_enabled = False
	is_keyboard_joy_y_enabled = False

	
is_cursor_to_center_key_pressed = mouse.middleButton

# Кнопка обзора
if keyboard.getKeyDown(mouse_vjoy_toggle_key) and mouse_vjoy_is_enabled and not mouse_vjoy_is_forced_unenable:
	mouse_vjoy_is_enabled = False

# Включение мышеджоя
if not keyboard.getKeyDown(mouse_vjoy_toggle_key) and not mouse_vjoy_is_enabled and not mouse_vjoy_is_forced_unenable:
	mouse_vjoy_is_enabled = True
	vJoy[0].rx = 0
	vJoy[0].ry = 1000
	windll.user32.SetCursorPos(
		mouse_x,
		mouse_y
	)

# Принудительное выключение мышеджоя
if (keyboard.getPressed(mouse_vJoy_unenable_forced_key)):
	mouse_vjoy_is_forced_unenable = True
	mouse_vjoy_is_enabled = False

# Принудительное включение мышеджоя
if (mouse_vjoy_is_forced_unenable and keyboard.getPressed(mouse_vjoy_toggle_key)):
	mouse_vjoy_is_forced_unenable = False
	mouse_vjoy_is_enabled = True
	vJoy[0].rx = 0
	vJoy[0].ry = 600
	windll.user32.SetCursorPos(
		mouse_x,
		mouse_y
	)

# Центрирование курсора полезно для кликабильности при включенном мышеджое центрируется мышеджой
if (is_cursor_to_center_key_pressed):
	windll.user32.SetCursorPos(SCREEN_X / 2, SCREEN_Y / 2)
	if mouse_vjoy_is_enabled:
		vJoy[0].x = 0
		vJoy[0].y = 0	

# Логика работы мышеджоя
if mouse_vjoy_is_enabled: 
	windll.user32.GetCursorPos(byref(CURSOR))
	mouse_x = CURSOR.x
	mouse_y = CURSOR.y

	# --- Блокировка выхода курсора за пределы мыше джоя (не имеет смысла если размер мыше джостика = размеру монитора) ---
	# if (mouse_x < (SCREEN_X - MOUSE_JOY_WIDTH)/2):
	# 	windll.user32.SetCursorPos((SCREEN_X - MOUSE_JOY_WIDTH)/2, mouse_y)
	# if (mouse_x > SCREEN_X - ((SCREEN_X - MOUSE_JOY_WIDTH)/2)):
	# 	windll.user32.SetCursorPos(SCREEN_X - ((SCREEN_X - MOUSE_JOY_WIDTH)/2), mouse_y)
	# if (mouse_y < (SCREEN_Y - MOUSE_JOY_HEIGHT)/2):
	# 	windll.user32.SetCursorPos(mouse_x, (SCREEN_Y - MOUSE_JOY_HEIGHT)/2)   
	# if (mouse_y > SCREEN_Y - ((SCREEN_Y - MOUSE_JOY_HEIGHT)/2)):
	# 	windll.user32.SetCursorPos(mouse_x, SCREEN_Y - ((SCREEN_Y - MOUSE_JOY_HEIGHT)/2))

	if (not is_keyboard_joy_x_enabled):
		vJoy[0].x = (mouse_x - (SCREEN_X / 2)) * MULTIPLE_X
		saved_x_joy = vJoy[0].x
	else:
		saved_x_joy = (mouse_x - (SCREEN_X / 2)) * MULTIPLE_X

	if (not is_keyboard_joy_y_enabled):
		vJoy[0].y = (mouse_y - (SCREEN_Y / 2)) * MULTIPLE_Y
		saved_y_joy = vJoy[0].y
	else:
		saved_y_joy = (mouse_y - (SCREEN_Y / 2)) * MULTIPLE_Y

	# ЛКМ работает только при влюченом мышеджое, чтобы не было случайных выстрелов (если на ЛКМ назначена гашетка)
	# если на ЛКМ гашетки нет можно выносить из блока if, для использовании ЛКМ без включения мышеджоя
	if mouse.leftButton: vJoy[0].setButton(0, True)
	else: vJoy[0].setButton(0, False)

# Назначение кнопок мышеджоя
if mouse.rightButton: vJoy[0].setButton(1, True)
else: vJoy[0].setButton(1, False)
if mouse.middleButton: vJoy[0].setButton(2, True)
else: vJoy[0].setButton(2, False)
if mouse.getButton(3): vJoy[0].setButton(3, True)
else: vJoy[0].setButton(3, False)
if mouse.getButton(4): vJoy[0].setButton(4, True)
else: vJoy[0].setButton(4, False)   

# Ось приближения
vJoy[0].z += mouse.wheel * Z_SENS
if vJoy[0].z > 18480: vJoy[0].z = 18480
if vJoy[0].z < -17160: vJoy[0].z = -17160

# Крен влево с клавиатуры
if keyboard.getKeyDown(Key.A):
	if not is_keyboard_joy_x_enabled: is_keyboard_joy_x_enabled = True
	if (saved_x_joy - MAX_MOUSE_JOY_VALUE/2 > -MAX_MOUSE_JOY_VALUE/2):
		vJoy[0].x = saved_x_joy - MAX_MOUSE_JOY_VALUE/2
	else:
		vJoy[0].x = -MAX_MOUSE_JOY_VALUE/2

# Крен право с клавиатуры
if keyboard.getKeyDown(Key.D):
	if not is_keyboard_joy_x_enabled: is_keyboard_joy_x_enabled = True
	if (saved_x_joy + MAX_MOUSE_JOY_VALUE/2 < MAX_MOUSE_JOY_VALUE/2):
		vJoy[0].x = saved_x_joy + MAX_MOUSE_JOY_VALUE/2
	else:
		vJoy[0].x = MAX_MOUSE_JOY_VALUE/2

# Тангаж вниз с клавиатуры
if keyboard.getKeyDown(Key.LeftShift):
	if not is_keyboard_joy_y_enabled: is_keyboard_joy_y_enabled = True
	if (saved_y_joy - MAX_MOUSE_JOY_VALUE/2 > -MAX_MOUSE_JOY_VALUE/2):
		vJoy[0].y = saved_y_joy - MAX_MOUSE_JOY_VALUE/2
	else:
		vJoy[0].y = -MAX_MOUSE_JOY_VALUE/2

# Тангаж вверх с клавиатуры
if keyboard.getKeyDown(Key.LeftControl):
	if not is_keyboard_joy_y_enabled: is_keyboard_joy_y_enabled = True
	if (saved_y_joy + MAX_MOUSE_JOY_VALUE/2 < MAX_MOUSE_JOY_VALUE/2):
		vJoy[0].y = saved_y_joy + MAX_MOUSE_JOY_VALUE/2
	else:
		vJoy[0].y = MAX_MOUSE_JOY_VALUE/2

# Возврат положения крена джоя
if (not keyboard.getKeyDown(Key.D) and not keyboard.getKeyDown(Key.A)) and is_keyboard_joy_x_enabled:
	is_keyboard_joy_x_enabled = False
	vJoy[0].x = saved_x_joy

# Возврат положения тангажа джоя
if (not keyboard.getKeyDown(Key.LeftControl) and not keyboard.getKeyDown(Key.LeftShift)) and is_keyboard_joy_y_enabled:
	is_keyboard_joy_y_enabled = False
	vJoy[0].y = saved_y_joy

# Центрирование взгляда
if keyboard.getKeyDown(Key.Return):
    vJoy[0].rx = 0
    vJoy[0].ry = 0

# Обзор с мышки
if not mouse_vjoy_is_enabled: 
	if not mouse_vjoy_is_forced_unenable:
		vJoy[0].rx = vJoy[0].rx - mouse.deltaX * FAST_VIEW_SENS
		vJoy[0].ry = vJoy[0].ry - mouse.deltaY * FAST_VIEW_SENS
	else:
		vJoy[0].rx = vJoy[0].rx - mouse.deltaX * VIEW_SENS
		vJoy[0].ry = vJoy[0].ry - mouse.deltaY * VIEW_SENS

# защита от переполнения (высоких значений)
if vJoy[0].rx > MAX_VIEW_VALUE: vJoy[0].rx = MAX_VIEW_VALUE
if vJoy[0].rx < -MAX_VIEW_VALUE: vJoy[0].rx = -MAX_VIEW_VALUE
if vJoy[0].ry > MAX_VIEW_VALUE: vJoy[0].ry = MAX_VIEW_VALUE
if vJoy[0].ry < -MAX_VIEW_VALUE: vJoy[0].ry = -MAX_VIEW_VALUE
	
# диагностические значения
diagnostics.watch(mouse_vjoy_is_enabled)
diagnostics.watch(vJoy[0].x)
diagnostics.watch(vJoy[0].y)
diagnostics.watch(SCREEN_X)
diagnostics.watch(mouse.deltaX)
diagnostics.watch(vJoy[0].z)
diagnostics.watch(vJoy[0].rz)
diagnostics.watch(vJoy[0].rx)
diagnostics.watch(vJoy[0].ry)
diagnostics.watch(is_keyboard_joy_x_enabled)
diagnostics.watch(mouse_y)
diagnostics.watch(mouse_x)
diagnostics.watch(saved_x_joy)
diagnostics.watch(saved_y_joy)
