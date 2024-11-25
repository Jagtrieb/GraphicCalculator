from PyQt6.QtGui import QColor, QPen
import numexpr as ne
from numpy import nan

class MathFunction:
    """
    Класс математической функции, хранящий в себе Математическую функцию в двух формах (для расчёта и для демонстрации), а также цвет, которым будет отрисован график функции
    """
    def __init__(self, function, str_function, color = QColor.fromRgb(255, 0, 0)):
        self.function = function
        self.str_function = str_function
        self.color = color
        self.pen = QPen(self.color)
        self.isCorrect = False
        self.lines = []

    def __str__(self):
        return self.str_function
    
    def return_value(self, cur_x):
        x = cur_x
        if self.function:
            return ne.evaluate(self.function)
        return nan