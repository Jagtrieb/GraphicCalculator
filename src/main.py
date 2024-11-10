import sys
import numexpr as ne
from math import pi, sin, cos
from PyQt6.QtWidgets import QApplication, QMainWindow
from ui_file import Ui_MainWindow

class GraphicCalculator(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.FunctionInput.textChanged.connect(self.revise_function)
        self.CurrnetFunction = MathFunction('', '')
    
    def revise_function(self):
        entered_function = self.FunctionInput.toPlainText()
        fixed_function = entered_function.split()
        for i in range(len(fixed_function)):
            if fixed_function[i] == '^':
                fixed_function[i] = '**'
            elif '(' in fixed_function[i] or 'x' in fixed_function[i]:
                fixed_function[i] = self.fix_multiply(fixed_function[i])
        fixed_function = ' '.join(fixed_function)
        print(fixed_function)
        try:
            self.CurrnetFunction = MathFunction(fixed_function, entered_function)
            print(self.CurrnetFunction.return_value(5).round(10))
            self.FunctionIsCorrect.setText('Статус: Выражение верно')
        except Exception:
            self.FunctionIsCorrect.setText('Статус: Выражение не верно')
            

    def fix_multiply(self, raw_mult):
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
