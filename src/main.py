import sys
import numexpr as ne
from PyQt6.QtWidgets import QApplication, QMainWindow
from ui_file import Ui_MainWindow

class GraphicCalculator(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.FunctionInput.textChanged.connect(self.revise_function)
    
    def revise_function(self):
        entered_function = self.FunctionInput.toPlainText()
        fixed_function = entered_function.split()
        for i in range(len(fixed_function)):
            if fixed_function[i] == '^':
                fixed_function[i] = '**'
            elif '(' in fixed_function[i]:
                fixed_function[i] = self.fix_multiply(fixed_function[i], '(')
            elif 'x' in fixed_function[i] and len(fixed_function[i]) > 1:
                fixed_function[i] = self.fix_multiply(fixed_function[i], 'x')
        fixed_function = ' '.join(fixed_function)
        print(fixed_function)
        try:
            x = 1
            print(ne.evaluate(fixed_function))
        except Exception:
            self.FunctionIsCorrect.setText('Статус: Выражение не верно')
        else:
            self.FunctionIsCorrect.setText("Статус: Выражение верно")

    def fix_multiply(self, raw_mult, sym):
        alt_bracket = {'0' + sym : '0 * ',
                            '1' + sym : '1 * ',
                            '2' + sym: '2 * ',
                            '3' + sym: '3 * ',
                            '4' + sym: '4 * ',
                            '5' + sym: '5 * ',
                            '6' + sym: '6 * ',
                            '7' + sym: '7 * ',
                            '8' + sym: '8 * ',
                            '9' + sym: '9 * ',
                            '-' + sym: '-1 *',
                            'x' + sym: 'x *'}
        sym_index = raw_mult.index(sym) - 1
        if raw_mult[sym_index] + sym in alt_bracket:
            print(alt_bracket[raw_mult[sym_index] + sym])
            return raw_mult.replace(raw_mult[sym_index], alt_bracket[raw_mult[sym_index] + sym])
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GraphicCalculator()
    ex.show()
    sys.exit(app.exec())
