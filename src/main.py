import sys
import csv
import numexpr as ne
from numpy import nan
from math import pi
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QColorDialog
from PyQt6.QtGui import QColor, QPen, QBrush, QFont
from ui_file import Ui_MainWindow

class GraphicCalculator(QMainWindow, Ui_MainWindow):  #Класс граф. калькулятора
    """
    Основной класс графического калькулятора
    
    :param scene: поле, на котором будут отрисовываться графики
    :param CurrentFunction: объект класса :class:`MathFunction`, который обрабатывается в момент работы приложения 
    :param scale: масштаб координатной плоскости
    :param pixels per step *PPS*: отношение количества пикселей в self.scene к единице координатной плоскости
    :param correctiveX: смещение координатной плоскости по оси X
    :param correctiveY: смещение координатной плоскости по оси Y
    """
    def __init__(self):
        self.correctiveX = 0
        self.correctiveY = 0
        self.PPS = 20 #Pixels_per_step
        self.scale = 1 #Масштаб координатной плоскости. По умолчанию(100%) 20 пикселей равняются 1 единице в плоскости
        super().__init__()
        self.setupUi(self)
        self.ColorSeletButton.clicked.connect(self.select_func_color)
        self.CurrnetFunction = MathFunction('', '')
        self.FunctionInput.textChanged.connect(self.revise_function)
        self.ScalesBox.currentTextChanged.connect(self.change_scale)
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 4000, 4000)
        self.graphicsView.setBackgroundBrush(QBrush(QColor.fromRgb(255, 255, 255)))
        self.graphicsView.setScene(self.scene)
        self.draw_grid()


    def pix_to_coord(self, raw):
        """
        Перевод координаты пикселя в self.scene в значение координаты в координатной плоскости

        :param raw: Значение координаты пикселя в *self.scene*
        :return: Значение координаты в координатной плоскости
        :rtype: float
        """
        return (raw - self.scene.width() / 2 + self.correctiveX) / (self.PPS * self.scale)
    
    def coords_to_pix(self, raw):
        """
        Перевод значения на координатной плоскости в значение пикселя в *self.scene*

        :param raw: Значение координаты на координатной плоскости
        :return: Координата пикселя в *self.scene*
        :rtype: float
        """
        return self.scene.height() - (raw * (self.PPS * self.scale) + self.scene.height() / 2)

    def draw_function(self):
        """
        Функция, которая отрисовывает математическую функцию
        """
        for pix_x in range(1, int(self.scene.width()) + 1):
            prev_x = self.pix_to_coord(pix_x - 1)
            cur_x = self.pix_to_coord(pix_x)
            cur_y = self.coords_to_pix(self.CurrnetFunction.return_value(cur_x))
            prev_y = self.coords_to_pix(self.CurrnetFunction.return_value(prev_x))
            #print(f'x: {cur_x}; cur_y: {cur_y}')
            if not ((str(cur_y) == 'nan') or (str(cur_y) == 'inf')):
                self.scene.addLine(pix_x - 1, prev_y, pix_x, cur_y, self.CurrnetFunction.pen)

    def draw_grid(self):
        """
        Отрисовывает сетку координатной плоскости на виджете *self.scene*
        """
        pen = QPen(QColor.fromRgb(220, 220, 220))
        end = int(self.scene.width())
        mark_coord = end / 2 - self.PPS / 4
        for coord in range(0, end + self.PPS, self.PPS):
            self.scene.addLine(0, coord, end, coord, pen)
            if self.correctiveY == 0:
                self.scene.addLine(mark_coord, coord, mark_coord + self.PPS / 2, coord)
            self.scene.addLine(coord, 0, coord, end, pen)
            if self.correctiveX == 0:
                self.scene.addLine(coord, mark_coord, coord, mark_coord + self.PPS / 2)
        if self.correctiveX == 0:
            self.scene.addLine(0, end / 2, end, end / 2)
        if self.correctiveY == 0:
            self.scene.addLine(end / 2, 0, end / 2, end)
        self.add_num_marks()

    def create_num_mark(self, x, y, text):
        mark = self.scene.addText(text)
        mark.setPos(x, y)
        mark.setFont(QFont("Arial", 11))
        mark.setDefaultTextColor(QColor.fromRgb(0, 0, 0))

    def add_num_marks(self):
        end = int(self.scene.width())
        if self.correctiveX == 0:
            for coord in range(0, end + self.PPS, self.PPS * 5):
                self.create_num_mark(coord - self.PPS / 1.3, end / 2, str(round((coord - end / 2) / self.PPS / self.scale, 2)))
        if self.correctiveY == 0:
            for coord in range(0, end + self.PPS, self.PPS * 5):
                self.create_num_mark(end / 2, end - coord - self.PPS / 1.5, str(round((coord - end / 2) / self.PPS / self.scale, 2)))

    def drawing_procedure(self):
        """
        Функция, запускающая процессы отрисовки сетки и графиков
        """
        self.scene.clear()
        self.draw_grid()
        self.draw_function()

    def select_func_color(self):
        """
        Функия для выбора цвета графика *self.CurrecntFunction*
        """
        color = QColorDialog.getColor()
        if color.isValid():
            print(type(color))
            self.ColorSeletButton.setStyleSheet(
                "background-color: {}".format(color.name()))
            self.CurrnetFunction.pen.setColor(color)
            self.drawing_procedure()
        
    def change_scale(self):
        self.scale = float(str(self.ScalesBox.currentText()[:-1])) / 100
        self.drawing_procedure()

    def revise_function(self):
        """
        Функция для проверки введённой математической функции и её отрисовка при удовлетворительном результате
        """
        entered_function = self.FunctionInput.toPlainText()
        fixed_function = entered_function.split()
        for i in range(len(fixed_function)):
            if fixed_function[i] == '^':
                fixed_function[i] = '**'
            elif '(' in fixed_function[i] or 'x' in fixed_function[i]:
                fixed_function[i] = self.fix_multiply(fixed_function[i])
        fixed_function = ' '.join(fixed_function)
        #print(fixed_function)
        try:
            #self.CurrnetFunction = MathFunction(fixed_function, entered_function)
            self.CurrnetFunction.function = fixed_function
            self.CurrnetFunction.str_function = entered_function
            self.FunctionIsCorrect.setText('Статус: Выражение верно' if fixed_function else 'Статус: Выражение не введено')
            self.drawing_procedure()
            # self.scene.clear()
            # self.draw_grid()
            # self.draw_function()
        except Exception as e:
            #print(e)
            self.FunctionIsCorrect.setText('Статус: Выражение не верно')
            
    def fix_multiply(self, raw_mult): #Функция, заменяющая умножение типа 2x или x(...) на 2 * x и x * (...)
        """
        Функция для замены умножения в виде 2x или x(...) на 2 * x и x * (...), для правильного прочтения введённой математической функции 
        
        :param raw_mult: Введённая (*сырая*) математическая функция
        :return: Введённая математическая функция, которая была исправлена для корректного прочтения и обработки
        """
        new_mult = raw_mult[:]
        fix_ind = 0
        for sym_ind in range(1, len(raw_mult)):
            prev = raw_mult[sym_ind - 1]
            if (raw_mult[sym_ind] == '(' or raw_mult[sym_ind] == 'x') and (prev.isdigit() or prev == 'x'):
                new_mult = new_mult[:sym_ind + fix_ind] + (' * ' + raw_mult[sym_ind]) + new_mult[sym_ind + 1 + fix_ind:]
                fix_ind += 3    
        return new_mult
    
class MathFunction:
    """
    Класс математической функции, хранящий в себе Математическую функцию в двух формах (для расчёта и для демонстрации), а также цвет, которым будет отрисован график функции
    """
    def __init__(self, function, str_function, color = QColor.fromRgb(255, 0, 0)):
        self.function = function
        self.str_function = str_function
        self.color = color
        self.pen = QPen(self.color)

    def __str__(self):
        return self.str_function
    
    def return_value(self, cur_x):
        x = cur_x
        if self.function:
            return ne.evaluate(self.function)
        return nan

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GraphicCalculator()
    ex.show()
    sys.exit(app.exec())
