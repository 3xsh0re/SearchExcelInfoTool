import sys
import pandas as pd
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QCheckBox, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap, QFont
# 读取社工库.xlxs文件
global data_frame
# 复选框模式:
# 000->普通搜索;200->身份证;020->手机号;002->邮箱;
# 220->身份证+手机号;202->身份证+邮箱;
# 022->手机号+邮箱;222->身份证+手机号+邮箱
global mode
mode = '000'

# 判断是人名还是手机号
def judge_name_or_phone(search_string):
    # 定义正则表达式
    # 11位手机号
    pattern_phone = r'^\d{11}$'
    # 纯中文字符和·
    pattern_name = r'^[\u4e00-\u9fa5·]+$'
    if re.match(pattern_name,search_string):
        # 表示是人名查询
        return 1
    elif re.match(pattern_phone,search_string):
        # 表示是手机号查询
        return 2
    else:
        # 不合法字符
        return 0
    
# 定义窗口类
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Social-Work-Lib Search ——by 3xsh0re")
        self.setGeometry(200, 100, 1520, 880)
        self.setFixedSize(self.width(), self.height())

        # 设置窗口背景图片
        background_image = QPixmap("./src/background.jpeg")
        background_label = QLabel(self)
        background_label.setPixmap(background_image)
        background_label.setGeometry(0, 0, 1520, 880)

        win_icon = QIcon("./src/title.ico")
        self.setWindowIcon(win_icon)

        layout = QVBoxLayout()

        # 使用水平布局放置搜索框和按钮
        hbox = QHBoxLayout()

        # 设置搜索框
        font_content = QFont("宋体",11)
        self.search_box = QLineEdit()
        self.search_box.setFont(font_content)
        self.search_box.setPlaceholderText("请输入人名或者手机号")
        self.search_box.setStyleSheet("""
            QLineEdit { 
                border-radius: 13px; 
                border: 2px solid #4CAF50;
                font-family: KaiTi;
                padding: 8px;
            }
        """)
        hbox.addWidget(self.search_box)

        self.search_button = QPushButton("查询")
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-family: SimSun;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #398037;
            }
        """)
        self.search_button.clicked.connect(self.handle_search)
        hbox.addWidget(self.search_button)
        
        # 将layout和hbox垂直布局
        layout.addLayout(hbox)

        # 使用水平布局放置复选框
        hcheckbox = QHBoxLayout()
        font_checkbox = QFont("楷体", 13)

        self.checkbox_1 = QCheckBox("含有身份证信息")
        self.checkbox_1.setFont(font_checkbox)
        self.checkbox_1.setStyleSheet("""
            QCheckBox {
                color: white;
                font-family: KaiTi;
            }
        """)
        hcheckbox.addWidget(self.checkbox_1)
        self.checkbox_1.stateChanged.connect(lambda: self.btnstate(self.checkbox_1))

        self.checkbox_2 = QCheckBox("含有手机号信息")
        self.checkbox_2.setFont(font_checkbox)
        self.checkbox_2.setStyleSheet("""
            QCheckBox {
                color: white;
                font-family: KaiTi;
            }
        """)
        hcheckbox.addWidget(self.checkbox_2)
        self.checkbox_2.stateChanged.connect(lambda: self.btnstate(self.checkbox_2))

        self.checkbox_3 = QCheckBox("含有邮箱信息")
        self.checkbox_3.setFont(font_checkbox)
        self.checkbox_3.setStyleSheet("""
            QCheckBox {
                color: white;
                font-family: KaiTi;
            }
        """)
        hcheckbox.addWidget(self.checkbox_3)
        self.checkbox_3.stateChanged.connect(lambda: self.btnstate(self.checkbox_3))

        # 将layout和hcheckbox垂直布局
        layout.addLayout(hcheckbox)

        # 设置文件选择按钮
        self.file_button = QPushButton("选择社工库^_^")
        self.file_button.clicked.connect(self.select_file)
        self.file_button.setFont(font_content)
        self.file_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-family: SimSun;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #398037;
            }
        """)
        layout.addWidget(self.file_button)

        # 设置表格控件
        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet("""
            QTableWidget { 
                border: 6px solid #4CAF50;
                border-radius: 14px; 
                font-family: KaiTi
            }
        """)
        self.table_widget.setColumnCount(5)
        font = QFont("楷体", 15, QFont.Bold)
        self.table_widget.setFont(font_content)
        self.table_widget.horizontalHeader().setFont(font)
        self.table_widget.setHorizontalHeaderLabels(["姓名", "身份证号", "手机号", "住址", "邮箱"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_widget)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    # 处理搜索出来的内容
    def handle_search(self):
        try:
            # 获取搜索框内容
            results = self.search(self.search_box.text())
            if results == 0 or len(results) == 0:
                self.table_widget.setRowCount(1)
                self.table_widget.setItem(0, 0, QTableWidgetItem("查不到哟~"))
                self.table_widget.setItem(0, 1, QTableWidgetItem("可能名字输错^_^"))
                self.table_widget.setItem(0, 2, QTableWidgetItem("小库信息不多^<>^"))
                self.table_widget.setItem(0, 3, QTableWidgetItem("手机号错了?"))
                self.table_widget.setItem(0, 4, QTableWidgetItem("Sad~~~"))
            else:
                self.table_widget.setRowCount(len(results))
                num = 0
                for info in results:
                    if (num == len(results)):
                        break
                    self.table_widget.setItem(num, 0, QTableWidgetItem(str(info[0])))
                    self.table_widget.setItem(num, 1, QTableWidgetItem(str(info[1])))
                    self.table_widget.setItem(num, 2, QTableWidgetItem(str(info[2])))
                    self.table_widget.setItem(num, 3, QTableWidgetItem(str(info[3])))
                    self.table_widget.setItem(num, 4, QTableWidgetItem(str(info[4])))
                    num+=1
        except Exception as e:
            error_dialog = QMessageBox()
            icon = QIcon("./src/error.ico")
            error_dialog.setWindowIcon(icon)
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle("Sad~~~")
            error_dialog.setText("怎么没有选择社工库文件捏？")
            error_dialog.exec_()

    # 搜索函数
    def search(self,search_string):
        global mode
        # 处理未选择文件的情况
        if len(data_frame) == 0:
            error_dialog = QMessageBox()
            icon = QIcon("./src/error.ico")
            error_dialog.setWindowIcon(icon)
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle("Sad~~~")
            error_dialog.setText("怎么没有选择社工库文件捏？")
            error_dialog.exec_()
            return 0
        else:
            if mode == "000": # 普通搜索
                # 判断字符串是否合法
                flag = judge_name_or_phone(search_string)
                if flag == 1:
                    name_list = data_frame['姓名']
                    # 获取行号
                    results = name_list[name_list==search_string].index
                    # 获取行里的数据
                    row_values = data_frame.iloc[results].values
                    return_results = []
                    for i in range(len(results)):
                        return_results.append(row_values[i])
                    return return_results
                elif flag == 2:
                    # 获取手机号列表
                    phone_list = data_frame['手机号']
                    results = phone_list[phone_list==int(search_string)].index
                    # 返回对应行号
                    row_values = data_frame.iloc[results].values
                    return_results = []
                    for i in range(len(results)):
                        return_results.append(row_values[i])
                    return return_results
                else:
                    return 0
            else: # 非普通模式
                if mode == "200": # 身份证
                    return_results = []
                    # 遍历 DataFrame 行
                    for row in data_frame.itertuples():
                        R = list(row)
                        # row 是一个命名元组，其中包含了当前行的数据
                        if type(R[2]) is not float:
                            R.pop(0)
                            return_results.append(R)
                    return return_results
                elif mode == "020": # 手机号
                    return_results = []
                    # 遍历 DataFrame 行
                    for row in data_frame.itertuples():
                        R = list(row)
                        # row 是一个命名元组，其中包含了当前行的数据
                        if type(R[3]) is not float:
                            R.pop(0)
                            return_results.append(R)
                    return return_results
                elif mode == "002":# 邮箱
                    return_results = []
                    # 遍历 DataFrame 行
                    for row in data_frame.itertuples():
                        R = list(row)
                        # row 是一个命名元组，其中包含了当前行的数据
                        if type(R[5]) is not float:
                            R.pop(0)
                            return_results.append(R)
                    return return_results
                elif mode == "220": # 身份证+手机号
                    return_results = []
                    # 遍历 DataFrame 行
                    for row in data_frame.itertuples():
                        R = list(row)
                        # row 是一个命名元组，其中包含了当前行的数据
                        if type(R[2]) is not float and type(R[3]) is not float:
                            R.pop(0)
                            return_results.append(R)
                    return return_results
                elif mode == "202": # 身份证+邮箱
                    return_results = []
                    # 遍历 DataFrame 行
                    for row in data_frame.itertuples():
                        R = list(row)
                        # row 是一个命名元组，其中包含了当前行的数据
                        if type(R[2]) is not float and type(R[5]) is not float:
                            R.pop(0)
                            return_results.append(R)
                    return return_results
                elif mode == "022": # 手机号+邮箱
                    return_results = []
                    # 遍历 DataFrame 行
                    for row in data_frame.itertuples():
                        R = list(row)
                        # row 是一个命名元组，其中包含了当前行的数据
                        if type(R[3]) is not float and type(R[5]) is not float:
                            R.pop(0)
                            return_results.append(R)
                    return return_results
                elif mode == "222": # 身份证+手机号+邮箱
                    return_results = []
                    # 遍历 DataFrame 行
                    for row in data_frame.itertuples():
                        R = list(row)
                        # row 是一个命名元组，其中包含了当前行的数据
                        if type(R[2]) is not float and type(R[3]) is not float and type(R[5]) is not float:
                            R.pop(0)
                            return_results.append(R)
                    return return_results
                else:
                    return 0
                    
            
    
    # 复选框状态
    def btnstate(self, btn):
        global mode
        chk1Status = str(self.checkbox_1.checkState())
        chk2Status = str(self.checkbox_2.checkState())
        chk3Status = str(self.checkbox_3.checkState())
        mode = chk1Status+chk2Status+chk3Status
        print(mode)

    # 文件选择函数
    def select_file(self):
        try:
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.ExistingFile)  # 设置为选择现有文件
            file_dialog.setNameFilters(["社工库表格 (*.xlsx)"])  # 设置文件过滤器
            file_dialog.exec_()
            file_paths = file_dialog.selectedFiles()
            file_path = file_paths[0]
            if file_path:
                global data_frame
                data_frame = pd.read_excel(file_path)
                success_dialog = QMessageBox()
                icon = QIcon("./src/success.ico")
                success_dialog.setWindowIcon(icon)
                success_dialog.setWindowTitle("Success!!!")
                success_dialog.setText(f"你的社工库路径是：{file_path}")
                F = file_path.split("/")
                self.file_button.setText(f"你选择的社工库是：{F[-1]} || 点击我换一个^_^")
                success_dialog.exec_()
        except Exception as e:
            error_dialog = QMessageBox()
            icon = QIcon("./src/error.ico")
            error_dialog.setWindowIcon(icon)
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle("Sad~~~")
            error_dialog.setText("怎么没有选择社工库文件捏？")
            error_dialog.exec_()

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("错误")
        error_dialog.setText("程序发生发生未知错误")
        error_dialog.setInformativeText(str(e))
        error_dialog.exec_()
