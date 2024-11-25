import sys
import csv
import numexpr as ne
from numpy import nan
from math import pi as PI
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QColorDialog, QColorDialog, QFileDialog, QTableWidgetItem
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QColor, QPen, QBrush, QFont
from PyQt6.QtCore import Qt
from ui_file import Ui_MainWindow
from copy import copy
from MathFunction import MathFunction

class GraphicCalculator(QMainWindow, Ui_MainWindow):
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
        self.PPS = 40 #Pixels_per_step
        self.scale = 1
        super().__init__()
        self.setupUi(self)
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 4400, 4400)
        self.count_coord_border()
        self.graphicsView.setBackgroundBrush(QBrush(QColor.fromRgb(255, 255, 255)))
        self.graphicsView.setScene(self.scene)
        self.ScalesBox.addItems(['10%', '25%', '50%', '75%', '100%', '125%', '150%', '175%', '200%'])
        self.ScalesBox.setCurrentIndex(4),
        self.tableWidget.itemDoubleClicked.connect(self.edit_color_in_table)
        #self.edit_flag = False
        self.tableWidget.itemChanged.connect(self.edit_table_func)
        self.CurrnetFunction = MathFunction('', '')
        self.ColorSeletButton.clicked.connect(self.select_func_color)
        self.FunctionInput.textChanged.connect(self.current_function_update)
        self.ScalesBox.currentTextChanged.connect(self.change_scale)
        self.AddFuncButton.clicked.connect(self.add_function)
        self.deleteButton.clicked.connect(self.delete_func)
        self.New_file.triggered.connect(self.reset)
        self.Open_file.triggered.connect(self.open_table)
        self.Save_file.triggered.connect(self.save_table_data)
        self.Save_file_as.triggered.connect(self.save_as)
        self.Help.triggered.connect(self.show_help)
        self.reset()

    def reset(self):
        self.scene.clear()
        self.draw_grid()
        self.functions = []
        self.fill_table()
        self.FunctionInput.setText('')
        self.ColorSeletButton.setStyleSheet(
                "background-color: {}".format(QColor.fromRgb(255, 0, 0).name()))
        self.CurrnetFunction = MathFunction('', '')
        self.file_name = 'saved_graphs/new.csv'
        self.create_blank_table()
        self.load_table_data(self.file_name)
        self.ScalesBox.setCurrentIndex(4)
        self.scale = 1


    def count_coord_border(self):
        self.top = self.scene.height() / self.PPS / 2
        self.bottom = self.top * -1

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

    def draw_function(self, function):
        """
        Функция, которая отрисовывает математическую функцию
        """

        for pix_x in range(1, int(self.scene.width()) + 1):
            prev_x = self.pix_to_coord(pix_x - 1)
            cur_x = self.pix_to_coord(pix_x)
            cur_y = self.coords_to_pix(function.return_value(cur_x))
            prev_y = self.coords_to_pix(function.return_value(prev_x))
            if not ((str(cur_y) == 'nan') or (str(cur_y) == 'inf') and (self.bottom < cur_y < self.top)):
                function.lines.append(self.scene.addLine(pix_x - 1, prev_y, pix_x, cur_y, function.pen)) 

    def remove_function(self, function): #Пока не работает
        for i in range(len(function.lines)):
            self.scene.removeItem(function.lines[i])
        function.lines = []

    def draw_all_functions(self):
        for func in self.functions:
            if func.isCorrect:
                self.draw_function(func)

    def draw_grid(self):
        """
        Отрисовывает сетку координатной плоскости на виджете *self.scene*
        """
        pen = QPen(QColor.fromRgb(220, 220, 220))
        end = int(self.scene.width())
        mark_coord = end / 2 - self.PPS / 4
        for coord in range(0, end + self.PPS, self.PPS):
            self.scene.addLine(0, coord, end, coord, pen)
            if self.correctiveX == 0:
                self.scene.addLine(mark_coord, coord, mark_coord + self.PPS / 2, coord)
            self.scene.addLine(coord, 0, coord, end, pen)
            if self.correctiveY == 0:
                self.scene.addLine(coord, mark_coord, coord, mark_coord + self.PPS / 2)
        if self.correctiveY == 0:
            self.scene.addLine(0, end / 2, end, end / 2)
        if self.correctiveX == 0:
            self.scene.addLine(end / 2, 0, end / 2, end)
        self.add_num_marks()

    def create_num_mark(self, x, y, text):
        mark = self.scene.addText(text)
        mark.setPos(x, y)
        mark.setFont(QFont("Arial", 11))
        mark.setDefaultTextColor(QColor.fromRgb(0, 0, 0))

    def add_num_marks(self):
        end = int(self.scene.width())
        if self.correctiveY == 0:
            for coord in range(0, end + self.PPS, int(self.PPS * 1)):
                self.create_num_mark(coord, end / 2, str(round((coord - end / 2) / self.PPS / self.scale, 2)))
        if self.correctiveX == 0:
            for coord in range(0, end + self.PPS, int(self.PPS * 1)):
                self.create_num_mark(end / 2, end - coord, str(round((coord - end / 2) / self.PPS / self.scale, 2)))

    def drawing_procedure(self):
        """
        Функция, запускающая процессы отрисовки сетки и графиков
        """
        self.scene.clear()
        self.draw_grid()
        if self.CurrnetFunction.isCorrect:
            self.draw_function(self.CurrnetFunction)
        self.draw_all_functions()

    def select_func_color(self):
        """
        Функия для выбора цвета графика *self.CurrecntFunction*
        """
        color = QColorDialog.getColor()
        if color.isValid(): 
            print(type(color))
            self.ColorSeletButton.setStyleSheet(
                "background-color: {}".format(color.name()))
            self.CurrnetFunction.color = color
            self.CurrnetFunction.pen.setColor(color)
            self.draw_function(self.CurrnetFunction)
        
    def change_scale(self):
        self.scale = float(str(self.ScalesBox.currentText()[:-1])) / 100
        self.drawing_procedure()

    def revise_function(self, func):
        """
        Функция для проверки введённой математической функции и её отрисовка при удовлетворительном результате
        """
        fixed_function = func.function
        try:
            x = 0
            ne.evaluate(fixed_function)
            self.FunctionIsCorrect.setText('Статус: Выражение верно' if fixed_function else 'Статус: Выражение не введено')
            return 1
        except Exception as e:
            self.FunctionIsCorrect.setText('Статус: Выражение не верно')
            return 0

    def fix_function(self, function=''):
        fixed_function = function.split()
        for i in range(len(fixed_function)):
            if fixed_function[i] == '^':
                fixed_function[i] = '**'
            elif '(' in fixed_function[i] or 'x' in fixed_function[i]:
                fixed_function[i] = self.fix_multiply(fixed_function[i])
        fixed_function = ' '.join(fixed_function)
        fixed_function = fixed_function.replace('pi', str(PI))
        return fixed_function

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


    def current_function_update(self):
        self.CurrnetFunction.str_function = self.FunctionInput.toPlainText()
        self.CurrnetFunction.function = self.fix_function(self.CurrnetFunction.str_function)
        if self.revise_function(self.CurrnetFunction):
            self.CurrnetFunction.isCorrect = True
        else:
            self.CurrnetFunction.isCorrect = False
        self.drawing_procedure()

    def add_function(self):
        if self.CurrnetFunction.isCorrect:
            self.functions.append(copy(self.CurrnetFunction))
            self.FunctionInput.setText('')
            color = QColor.fromRgb(255, 0, 0)
            self.ColorSeletButton.setStyleSheet(
                "background-color: {}".format(color.name()))
            self.CurrnetFunction = MathFunction('', '')
            self.fill_table()
            

    def open_table(self):
        self.reset()
        self.file_name = QFileDialog.getOpenFileName(self, 'Выбрать таблицу', '', 'Таблица (*.csv)')[0]
        self.load_table_data(self.file_name)

    def create_blank_table(self):
        with open(self.file_name, 'w', encoding='utf8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['str_func', 'color', 'function'])

    def load_table_data(self, table_name):
        self.functions = []
        with open(table_name, 'r', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            next(reader)
            for row in reader:
                row[1] = tuple(int(i) for i in row[1][1:-1].split(', '))
                self.functions.append(MathFunction(row[2], row[0], QColor.fromRgb(*row[1])))
        #print(self.functions)
        self.fill_table()

    def save_table_data(self):
        if self.file_name == 'saved_graphs/new.csv':
            self.save_as()
        with open(self.file_name, 'w', encoding='utf8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['str_func', 'color', 'function'])
            for row, function in enumerate(self.functions):
                rgb = (function.color.red(), function.color.green(), function.color.blue())
                writer.writerow([function.str_function, rgb, function.function])

    def save_as(self):
        #options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        initial_dir = 'saved_graphs'
        fileName, _ = QFileDialog.getSaveFileName(self, 
            "Сохранить как", initial_dir, "Таблица(*.csv)")
        if fileName:
            with open(fileName, 'w', encoding='utf8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(['str_func', 'color', 'function'])
                for row, function in enumerate(self.functions):
                    rgb = (function.color.red(), function.color.green(), function.color.blue())
                    writer.writerow([function.str_function, rgb, function.function])
                self.file_name = fileName
            self.load_table_data(self.file_name)

    def fill_table(self):
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(['Функция', 'Цвет', 'Корректность'])
        self.tableWidget.setRowCount(0)
        for i, func in enumerate(self.functions):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            self.tableWidget.setItem(i, 0, QTableWidgetItem(func.str_function))

            item = QTableWidgetItem(' ')
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.tableWidget.setItem(i, 1, item)
            self.tableWidget.item(i, 1).setBackground(func.color)

            item = QTableWidgetItem('ОК') if func.isCorrect else QTableWidgetItem("Error")
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(i, 2, item)
            self.tableWidget.resizeColumnsToContents()

    def edit_color_in_table(self, item):
        row, column = item.row(), item.column()
        if column == 1:
            color = QColorDialog.getColor()
            if color.isValid():
                self.functions[row].pen.setColor(color)
                self.functions[row].color = color
                self.tableWidget.item(row, 1).setBackground(self.functions[row].color)
                self.fill_table()

    def edit_table_func(self, item):
        row, column = item.row(), item.column()
        if column == 0:
            self.functions[row].str_function = self.tableWidget.item(row, 0).text()
            self.functions[row].function = self.fix_function(self.functions[row].str_function)
            if self.revise_function(self.functions[row]):
                self.functions[row].isCorrect = True
            else:
                self.functions[row].isCorrect = False
            item = QTableWidgetItem('ОК') if self.functions[row].isCorrect else QTableWidgetItem("Error")
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(row, 2, item)
            self.drawing_procedure()
            self.tableWidget.resizeColumnsToContents()

    def delete_func(self):
        id = self.deletionChoose.value()
        if -1 < id - 1 < len(self.functions):
            self.functions.pop(id - 1)
            self.fill_table()
            self.drawing_procedure()

    def show_help(self):
        with open('src/help.txt', 'r') as f:
            text = f.readlines()
            text = '\n'.join(text)
            QMessageBox.information(self, 'Справка', text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GraphicCalculator()
    ex.show()
    sys.exit(app.exec())
