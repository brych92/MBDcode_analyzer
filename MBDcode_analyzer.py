import csv, re, sys

from qgis.PyQt.QtGui import QCursor, QIcon, QPixmap, QTransform, QFont

from qgis.PyQt.QtCore import Qt, QUrl

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from qgis.PyQt.QtWidgets import (
    QLabel, QComboBox, QHBoxLayout, QVBoxLayout, QAction, QLabel,
    QPushButton, QApplication, QMenu, QWidget, QListWidget, QDialog, QSizePolicy
)

def open_dots(string:str):
    # Use a regular expression to find matching parts in the format a+d+...d+
    pattern = r"(;)?(\d\d\.\d\d)\.\.\.([\d\.]+)"
    
    def replace_match(match):
        sep, d_start, d_end = match.groups()
        if '.' not in d_end:
            a = f"{d_start.split('.')[0]}."
            d_start = d_start.split('.')[1]
            
            # Form the replacement string
            if sep:
                replacement = f"{sep}{a}{d_start}"
            else:
                replacement = f"{a}{d_start}"
                
            for i in range(int(d_start)+1, int(d_end)+1):
                if d_start[0] == '0':
                    d_formatted = f"{i:02d}"
                    replacement += f";{a}{d_formatted}"
                else:
                    replacement += f";{a}{i}"
        else:
            if not purpose_codes:
                return string
            started = False
            for pcode in purpose_codes.keys():
                if  started:
                    replacement += f";{pcode}"
                if pcode == d_start:
                    if sep:
                        replacement = f"{sep}{pcode}"
                    else:
                        replacement = f"{pcode}"
                    started = True
        return replacement
    
    # Replace the matching parts in the input text
    result = re.sub(pattern, replace_match, string)
    return result


def load_as_dict(filename : str):
    with open(filename, "r") as csv_file:
    # Створити об'єкт читача CSV
        csv_reader = csv.reader(csv_file,delimiter = ';')
    
        columns = csv_reader.__next__()
        
        file_dict = {}
        # Прочитати рядки з файлу
        for row in csv_reader:
            
            file_dict[row[0]] = {}
            for i, v in enumerate(columns):
                if i > 0:
                    if '...' in row[i]:
                        file_dict[row[0]][v] = open_dots(row[i])
                    else:
                        file_dict[row[0]][v] = row[i]
            #print(row)
    # Закрити файл
    csv_file.close()
    
    return file_dict

purpose_codes = load_as_dict("tables/purpose.csv")

functional_codes = load_as_dict("tables/functional.csv")# Відкрити файл для читання

dk_codes = load_as_dict("tables/edssb.csv")

#print(open_dots('01.01...13;09.01...02;10.01;10.02;10.04;10.05;10.10;11.01...04;14.01;14.02;15.01;15.02;15.03;15.04;15.05;15.06;15.07;15.08;15.09;15.10;12.01...04'))

        
#print(json.dumps(dk_codes, indent='  ', ensure_ascii=False))


class AboutDialog(QDialog):
    def __init__(self, icon):
        super().__init__()
        self.setWindowTitle("Про програму")
        self.setWindowIcon(icon)
        
        layout = QHBoxLayout()
        layout2 = QVBoxLayout()
        
        self.image_label = QLabel()
        pixmap = QPixmap("resources/humski.png") 
        pixmap = pixmap.scaledToWidth(220)
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignLeft)
        self.image_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.image_label)
        
        layout.addLayout(layout2)
        
        program_description = r"""        Міні програма призначена для автоматизованого підбору кодів будівель 
та земельних ділянок з таблиці додатку 2 до порядку ведення 
Єдиної державної електронної системи у сфері будівництва (далі - Таблиця),
та Класифікатору видів функціонального призначення територій та їх
співвідношення з видами цільового призначення земельних ділянок згідно з 
постановою №1051 (далі - Класифікатор).

        1.  При виборі коду будівлі відповідно до ДК 18-2000, програма визначає
можливі коди ділянки з Таблиці,"Коди за Класифікацією видів цільового 
призначення земель", де перша колонка позначена як основна,а друга - 
як допустима згідно яких беруться можливі коди функціональних зон відповідно 
до колонок .

        2.  При виборі коду цільового призначення згідно з постановою №1051, програма
використовує код функціональної зони з Класифікатору та відповідний код будівлі
з Таблиці, згідно з першим пунктом.

        3.  При виборі коду функціонального призначення, програма визначає коди
земельнихділянок згідно з Класифікатором, а потім автоматично визначає
відповідні коди будівель з Таблиці, за аналогією з першим пунктом.

Якщо ви знайшли помилки, будь ласка, повідомте на пошту brych92@gmail.com
"""
        message_label = QLabel(program_description)
        message_label.setAlignment(Qt.AlignJustify)
        layout2.addWidget(message_label)
        
        ok_button = QPushButton("Йов!")
        ok_button.clicked.connect(self.accept)
        layout2.addWidget(ok_button)

        self.setLayout(layout)

        # Play sound effect
        self.dialog_theme = QMediaPlayer()
        self.dialog_theme.setMedia(QMediaContent(QUrl.fromLocalFile("resources/theme.mp3")))  # Replace "fun_sound.wav" with your sound file
        self.dialog_theme.setVolume(10)
        self.dialog_theme.play()
        
        self.setFixedSize(self.sizeHint())

    def mousePressEvent(self, event):
        if self.dialog_theme.state() == 0:
            self.dialog_theme.play()
        else:
            self.dialog_theme.stop()
    
    def sizeHint(self):
        return self.minimumSizeHint()

class CustomComboBox(QComboBox):
    def __init__(self, my_dict, parent=None):
        super().__init__(parent)
        self.addItems([f"{key} - {val['name']}" for key, val in my_dict.items()])
        # self.setMinimumWidth(480)
        self.setMinimumContentsLength(50)
        self.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.setMaxVisibleItems(40)
        for i in range(self.count()):
            item_text = self.itemText(i)
            self.setItemData(i, item_text, role=Qt.ToolTipRole)

class CustomListWidget(QListWidget):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        self.parent = parent

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        copy_selected_action = QAction("Скопіювати виділене", self)
        copy_all_action = QAction("Скопіювати все", self)
        apply_action = QAction("Застосувати виділене", self)

        copy_selected_action.triggered.connect(lambda: self.copy_selected_line())
        copy_all_action.triggered.connect(lambda: self.copy_all_lines())
        apply_action.triggered.connect(lambda: self.apply_value())

        context_menu.addAction(apply_action)
        context_menu.addAction(copy_selected_action)
        context_menu.addAction(copy_all_action)

        context_menu.exec_(QCursor.pos())

    def copy_selected_line(self):
        selected_items = self.selectedItems()
        if selected_items:
            selected_text = selected_items[0].text()
            QApplication.clipboard().setText(selected_text)

    def copy_all_lines(self):
        all_items = [self.item(i).text() for i in range(self.count())]
        all_text = "\n".join(all_items)
        QApplication.clipboard().setText(all_text)
    
    def apply_value(self):
        selected_items = self.selectedItems()
        action = {
            'dk_list':self.parent.dk_double_click,
            'purpose_list':self.parent.purpose_double_click,
            'functional_list':self.parent.functional_double_click
        }
        action[self.name](selected_items[0])

class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Шпаргалка відповідності кодів будівель ділянок та функціональних зон")
        self.resize(640,640)
        self.setWindowOpacity(0.95)
        self.icon = QIcon("resources/humski.ico")
        self.setWindowIcon(self.icon)

        main_layout = QVBoxLayout(self)
        title_label = QLabel("Виберіть код з будь якої колонки, в інших відобразяться можливі залежності")
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt;") 

        main_layout.addWidget(title_label)
        iface_layout = QHBoxLayout()

        dk_layout = QVBoxLayout()#LR-18 2000-------------------------------------------
        
        self.dk_codes_list = CustomComboBox(dk_codes)
        self.dk_codes_list.textActivated.connect(self.dk_changed)
        
        self.dk_list_view_main = CustomListWidget('dk_list',self)
        self.dk_list_view_main.itemDoubleClicked.connect(self.dk_double_click)

        self.dk_list_view_second = CustomListWidget('dk_list',self)        
        self.dk_list_view_second.itemDoubleClicked.connect(self.dk_double_click)      

        dk_layout.addWidget(QLabel('Код будівлі'))
        dk_layout.addWidget(self.dk_codes_list)
        dk_layout.addWidget(QLabel('Основне призначення:'))
        dk_layout.addWidget(self.dk_list_view_main)
        dk_layout.addWidget(QLabel('Допустиме призначення:'))
        dk_layout.addWidget(self.dk_list_view_second)

        purpose_layout = QVBoxLayout()#цільова ---------------------------------------
        
        self.purpose_codes_list = CustomComboBox(purpose_codes)
        self.purpose_codes_list.textActivated.connect(self.purpose_changed)
        self.purpose_list_view_main = CustomListWidget('purpose_list',self)
        self.purpose_list_view_main.itemDoubleClicked.connect(self.purpose_double_click)  

        self.purpose_list_view_second = CustomListWidget('purpose_list',self)
        self.purpose_list_view_second.itemDoubleClicked.connect(self.purpose_double_click)  

        purpose_layout.addWidget(QLabel('Цільове призначення земельної ділянки'))
        purpose_layout.addWidget(self.purpose_codes_list)
        purpose_layout.addWidget(QLabel('Основне призначення:'))
        purpose_layout.addWidget(self.purpose_list_view_main)
        purpose_layout.addWidget(QLabel('Допустиме призначення:'))
        purpose_layout.addWidget(self.purpose_list_view_second)

        functional_layout = QVBoxLayout()# Функціональне -----------------------------
        
        self.functional_codes_list = CustomComboBox(functional_codes)
        self.functional_codes_list.textActivated.connect(self.functional_changed)
        self.functional_list_view_main = CustomListWidget('functional_list',self)
        self.functional_list_view_main.itemDoubleClicked.connect(self.functional_double_click)  
        self.functional_list_view_second = CustomListWidget('functional_list',self)
        self.functional_list_view_second.itemDoubleClicked.connect(self.functional_double_click)  

        functional_layout.addWidget(QLabel('Код функціональної зони'))
        functional_layout.addWidget(self.functional_codes_list)
        functional_layout.addWidget(QLabel('Основне призначення:'))
        functional_layout.addWidget(self.functional_list_view_main)
        functional_layout.addWidget(QLabel('Допустиме призначення:'))
        functional_layout.addWidget(self.functional_list_view_second)

        iface_layout.addLayout(dk_layout)
        iface_layout.addLayout(purpose_layout)
        iface_layout.addLayout(functional_layout)

        about_button = QPushButton("Про програму")
        about_button.clicked.connect(self.about)

        main_layout.addLayout(iface_layout)
        main_layout.addWidget(about_button)

        #self.setLayout(main_layout)

    def about(self):
        dialog = AboutDialog(self.icon)
        dialog.exec_()

    def make_combobox(self, my_dict:dict):
        cbox = QComboBox()
        cbox.addItems([f"{key} - {val['name']}" for key, val in my_dict.items()])
        #cbox.setMinimumWidth(480)
        cbox.setMinimumContentsLength(50)
        cbox.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        cbox.setMaxVisibleItems(40)
        for i in range(cbox.count()):
            item_text = cbox.itemText(i)
            cbox.setItemData(i, item_text, role=Qt.ToolTipRole)

        return cbox
    
    def dk_double_click(self, item):
        code = item.text()
        item = self.dk_codes_list.findText(code)
        if item != -1:
            self.dk_codes_list.setCurrentIndex(item)
            self.dk_changed(code, noclear = True)
    
    def purpose_double_click(self, item):
        code = item.text()
        item = self.purpose_codes_list.findText(code)
        if item != -1:
            self.purpose_codes_list.setCurrentIndex(item)
            self.purpose_changed(code, noclear = True)
    
    def functional_double_click(self, item):
        code = item.text()
        item = self.functional_codes_list.findText(code)
        if item != -1:
            self.functional_codes_list.setCurrentIndex(item)
            self.functional_changed(code, noclear = True)
        


    def dk_changed(self, value:str, noclear = False):
        def get_main_purposes_list(value:str):
            code = value.split(' - ')[0]
            if dk_codes[code]['Код землі основний'] == 'всі':
                list = [key for key in purpose_codes.keys()]
            else:
                list = dk_codes[code]['Код землі основний'].split(';')
            if list[0] != '':
                result = []
                for key in list:
                    if key in purpose_codes:
                        result.append(f"{key} - {purpose_codes[key]['name']}")
                    else:
                        result.append(f"{key} - невідоме цільове призначення!!!!")
                return result
            else:
                return []
        
        def get_second_purposes_list(value:str):
            code = value.split(' - ')[0]
            if dk_codes[code]['Код землі другорядний'] == 'всі':
                list = [key for key in purpose_codes.keys()]
            else:
                list = dk_codes[code]['Код землі другорядний'].split(';')

            if len(list) > 1 or list[0] != '':
                result = []
                for key in list:
                    if key in purpose_codes:
                        result.append(f"{key} - {purpose_codes[key]['name']}")
                    else:
                        result.append(f"{key} - невідоме цільове призначення!!!!")
                return result
            else:
                return []
        
        def get_main_functionals_list(value:str):
            code = value.split(' - ')[0]
            result = []
            result.append(f"Коди за ДБН: {dk_codes[code]['Код зони за ДБН головний']}")
            result.append(f"Коди за ДСТУ: {dk_codes[code]['Код зони за ДСТУ головний']}")
            
            if 'всі' in dk_codes[code]['Код землі основний']:
                result.append(f"Допустимо розміщувати на будь яких землях")
            else:
                purpose_list = dk_codes[code]['Код землі основний'].split(';')
                temp_funct_codes_main=[]
                temp_funct_codes_second=[]
                for purpose in purpose_list:
                    for k, v in functional_codes.items():
                        if purpose in v["main"]:
                            temp_funct_codes_main.append(f"{k} - {v['name']}")
                        if purpose in v["secondary"]:
                            temp_funct_codes_second.append(f"{k} - {v['name']}")
                
                funct_codes_main = sorted(list(set(temp_funct_codes_main)))
                funct_codes_second = sorted(list(set(temp_funct_codes_second)))
                if len(funct_codes_main) > 0:
                    result.append(f"Цільове призначення земель для будівель {code} вказане як основне в таких функціональних зонах:")
                    result.extend(funct_codes_main)
                if len(funct_codes_second) > 0:
                    result.append(f"Цільове призначення земель для будівель {code} вказане як супутнє в таких функціональних зонах:")
                    result.extend(funct_codes_second)

            return result
        
        def get_second_functionals_list(value:str):
            code = value.split(' - ')[0]
            result = []
            result.append(f"Коди за ДБН: {dk_codes[code]['Код зони за ДБН другорядний']}")
            result.append(f"Коди за ДСТУ: {dk_codes[code]['Код зони за ДСТУ другорядний']}")
            
            if 'всі' in dk_codes[code]['Код землі другорядний']:
                result.append(f"Допустимо розміщувати на будь яких землях")
            else:
                purpose_list = dk_codes[code]['Код землі другорядний'].split(';')
                temp_funct_codes_main=[]
                temp_funct_codes_second=[]
                for purpose in purpose_list:
                    for k, v in functional_codes.items():
                        if purpose in v["main"]:
                            temp_funct_codes_main.append(f"{k} - {v['name']}")
                        if purpose in v["secondary"]:
                            temp_funct_codes_second.append(f"{k} - {v['name']}")
                
                funct_codes_main = sorted(list(set(temp_funct_codes_main)))
                funct_codes_second = sorted(list(set(temp_funct_codes_second)))
                if funct_codes_main and len(funct_codes_main) > 0:
                    result.append(f"Цільове призначення земель для будівель {code} вказане як основне в таких функціональних зонах:")
                    result.extend(funct_codes_main)
                if funct_codes_second and len(funct_codes_second) > 0:
                    result.append(f"Цільове призначення земель для будівель {code} вказане як супутнє в таких функціональних зонах:")
                    result.extend(funct_codes_second)

            return result

        if not noclear:
            self.dk_list_view_main.clear()
            self.dk_list_view_second.clear()

        self.purpose_list_view_main.clear()
        self.purpose_list_view_main.addItems(get_main_purposes_list(value))
        self.purpose_list_view_second.clear()
        self.purpose_list_view_second.addItems(get_second_purposes_list(value))
        
        self.functional_list_view_main.clear()
        self.functional_list_view_main.addItems(get_main_functionals_list(value))
        self.functional_list_view_second.clear()
        self.functional_list_view_second.addItems(get_second_functionals_list(value))
        
        
    def purpose_changed(self, value:str, noclear = False):
        def get_main_functionals_list(value:str):
            result = []
            purpose = value.split(' - ')[0]
            for k, v in functional_codes.items():
                if purpose in v["main"]:
                    result.append(f"{k} - {v['name']}")
            return result
        
        def get_second_functionals_list(value:str):
            result = []
            purpose = value.split(' - ')[0]
            for k, v in functional_codes.items():
                if purpose in v["secondary"]:
                    result.append(f"{k} - {v['name']}")
            return result
        
        def get_main_dk_list(value:str):
            result = []
            purpose = value.split(' - ')[0]
            for k, v in dk_codes.items():
                if purpose in v["Код землі основний"]:
                    result.append(f"{k} - {v['name']}")
            return result
        
        def get_second_dk_list(value:str):
            result = []
            purpose = value.split(' - ')[0]
            for k, v in dk_codes.items():
                if purpose in v["Код землі другорядний"]:
                    result.append(f"{k} - {v['name']}")
            return result
        
        self.dk_list_view_main.clear()
        self.dk_list_view_main.addItems(get_main_dk_list(value))
        self.dk_list_view_second.clear()
        self.dk_list_view_second.addItems(get_second_dk_list(value))

        if not noclear:
            self.purpose_list_view_main.clear()
            self.purpose_list_view_second.clear()
        
        
        self.functional_list_view_main.clear()
        self.functional_list_view_main.addItems(get_main_functionals_list(value))
        self.functional_list_view_second.clear()
        self.functional_list_view_second.addItems(get_second_functionals_list(value))
            
    def functional_changed(self, value:str, noclear = False):
        def get_main_purposes_list(value:str):
            result = []
            functional = value.split(' - ')[0]
            temp_list = functional_codes[functional]['main'].split(';')
            if len(temp_list) == 0:
                return []
            for item in temp_list:
                if item in purpose_codes:
                    result.append(f"{item} - {purpose_codes[item]['name']}")
                elif item != '':
                    result.append(f"{item} - Невідомий код")
            
            return result
        
        def get_second_purposes_list(value:str):
            result = []
            functional = value.split(' - ')[0]
            temp_list = functional_codes[functional]['secondary'].split(';')
            if len(temp_list) == 0:
                return []
            for item in temp_list:
                if item in purpose_codes:
                    result.append(f"{item} - {purpose_codes[item]['name']}")
                elif item != '':
                    result.append(f"{item} - Невідомий код")
            return result
        
        def get_main_dk_list(value:str):
            result = []
            functional = value.split(' - ')[0]
            temp_list = functional_codes[functional]['main'].split(';')
            if len(temp_list) == 0:
                return []
            temp_main = []
            temp_second = []
            for item in temp_list:
                for k, v in dk_codes.items():
                    if item in v['Код землі основний']:
                        temp_main.append(f"{k} - {v['name']}")
                    if item in v['Код землі другорядний']:
                        temp_second.append(f"{k} - {v['name']}")
            
            code_main = sorted(list(set(temp_main)))
            codes_second = sorted(list(set(temp_second)))
            if code_main and len(code_main) > 0:
                result.append(f"Цільове призначення земель для функціональної зони {functional} вказане як основне в таких будівлях:")
                result.extend(code_main)
            if codes_second and len(codes_second) > 0:
                result.append(f"Цільове призначення земель для функціональної зони {functional} вказане як другорядне в таких будівлях:")
                result.extend(codes_second)
            
            return result
        
        def get_second_dk_list(value:str):
            result = []
            functional = value.split(' - ')[0]
            temp_list = functional_codes[functional]['secondary'].split(';')
            if len(temp_list) == 0:
                return []
            temp_main = []
            temp_second = []
            for item in temp_list:
                for k, v in dk_codes.items():
                    if item in v['Код землі основний']:
                        temp_main.append(f"{k} - {v['name']}")
                    if item in v['Код землі другорядний']:
                        temp_second.append(f"{k} - {v['name']}")
            
            code_main = sorted(list(set(temp_main)))
            codes_second = sorted(list(set(temp_second)))
            if code_main and len(code_main) > 0:
                result.append(f"Цільове призначення земель для функціональної зони {functional} вказане як основне в таких будівлях:")
                result.extend(code_main)
            if codes_second and len(codes_second) > 0:
                result.append(f"Цільове призначення земель для функціональної зони {functional} вказане як другорядне в таких будівлях:")
                result.extend(codes_second)
            
            return result
        
        self.dk_list_view_main.clear()
        self.dk_list_view_main.addItems(get_main_dk_list(value))
        self.dk_list_view_second.clear()
        self.dk_list_view_second.addItems(get_second_dk_list(value))

        self.purpose_list_view_main.clear()
        self.purpose_list_view_main.addItems(get_main_purposes_list(value))
        self.purpose_list_view_second.clear()
        self.purpose_list_view_second.addItems(get_second_purposes_list(value))
        
        if not noclear:
            self.functional_list_view_main.clear()
            self.functional_list_view_second.clear()

app = QApplication(sys.argv)
window = MainWindow()

window.show()

sys.exit(app.exec_())