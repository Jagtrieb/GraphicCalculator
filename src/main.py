import sys
import numexpr as ne
from math import pi, sin, cos
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene
from PyQt6.QtGui import QColor, QPen, QBrush
from ui_file import Ui_MainWindow

class GraphicCalculator(QMainWindow, Ui_MainWindow):  #Класс граф. калькулятора
    def __init__(self):
        self.correctiveX = 0
        self.correctiveY = 0
        self.PPS = 20 #Pixels_per_step
        self.scale = 1 #Масштаб координатной плоскости. По умолчанию(100%) 20 пикселей равняются 1 единице в плоскости
        super().__init__()
        self.setupUi(self)
        self.CurrnetFunction = MathFunction('', '')
        self.FunctionInput.textChanged.connect(self.revise_function)
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 4000, 4000)
        self.graphicsView.setBackgroundBrush(QBrush(QColor.fromRgb(255, 255, 255)))
        self.graphicsView.setScene(self.scene)
        self.draw_grid()
        #self.text = self.scene.addText('Hello')
        #self.scene.addEllipse(2000, self.zero_y(), 5, 5, self.CurrnetFunction.pen)

    def pix_to_coord(self, raw):
        return (raw - self.scene.width() / 2 + self.correctiveX) / (self.PPS * self.scale)
    
    def coords_to_pix(self, raw):
        return self.scene.height() - (raw * (self.PPS * self.scale) + self.scene.height() / 2)

    def draw_function(self):
        for pix_x in range(1, int(self.scene.width()) + 1):
            prev_x = self.pix_to_coord(pix_x - 1)
            cur_x = self.pix_to_coord(pix_x)
            cur_y = self.coords_to_pix(self.CurrnetFunction.return_value(cur_x))
            prev_y = self.coords_to_pix(self.CurrnetFunction.return_value(prev_x))
            print(f'x: {cur_x}; cur_y: {cur_y}')
            self.scene.addLine(pix_x - 1, prev_y, pix_x, cur_y, self.CurrnetFunction.pen)

    def draw_grid(self):
        pen = QPen(QColor.fromRgb(220, 220, 220))
        end = int(self.scene.width())
        for coord in range(0, end + self.PPS, self.PPS):
            if coord == end / 2:
                self.scene.addLine(0, coord, end, coord)
                self.scene.addLine(coord, 0, coord, end)
            else:
                self.scene.addLine(0, coord, end, coord, pen)
                self.scene.addLine(coord, 0, coord, end, pen)

    def revise_function(self):
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
            self.CurrnetFunction = MathFunction(fixed_function, entered_function)
            self.FunctionIsCorrect.setText('Статус: Выражение верно')
            self.scene.clear()
            self.draw_grid()
            self.draw_function()
        except Exception as e:
            #print(e)
            self.FunctionIsCorrect.setText('Статус: Выражение не верно')
            
    def fix_multiply(self, raw_mult): #Функция, заменяющая умножение типа 2x или x(...) на 2 * x и x * (...)
        new_mult = raw_mult[:]
        fix_ind = 0
        for sym_ind in range(1, len(raw_mult)):
            prev = raw_mult[sym_ind - 1]
            if (raw_mult[sym_ind] == '(' or raw_mult[sym_ind] == 'x') and (prev.isdigit() or prev == 'x'):
                new_mult = new_mult[:sym_ind + fix_ind] + (' * ' + raw_mult[sym_ind]) + new_mult[sym_ind + 1 + fix_ind:]
                fix_ind += 3    
        return new_mult
    
class MathFunction:
    def __init__(self, function, str_function):
        self.function = function
        self.str_function = str_function
        self.pen = QPen(QColor.fromRgb(255, 0, 0))

    def __str__(self):
        return self.str_function
    
    def return_value(self, cur_x):
        x = cur_x
        return ne.evaluate(self.function)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GraphicCalculator()
    ex.show()
    sys.exit(app.exec())
