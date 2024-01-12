import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor
import msg_item
import port
import msg_sum
import msg_app
import msg_prot
import msg_files
import clipboard
import pandas as pd

BoldFont = QtGui.QFont()
BoldFont.setBold(True)

CourierNewFont = QtGui.QFont()
CourierNewFont.setFamily("Courier New")
# CourierNewFont.setFamily("Consolas")

style_sheet = "background-color: black; color: white;"

debug_mode = 0

class Basic_GUI(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.open_btn = QPushButton("Open file")
        self.open_btn.setFont(CourierNewFont)
        self.open_btn.setFixedWidth(120)
        self.open_btn.setCheckable(False)

        self.open_btn.clicked.connect(self.open_file)

        self.clipboard_btn = QPushButton("Clipboard")
        self.clipboard_btn.setFont(CourierNewFont)
        self.clipboard_btn.setFixedWidth(120)
        self.clipboard_btn.setCheckable(False)

        self.clipboard_btn.clicked.connect(self.load_clipboard)

        self.opened_label = QLabel()

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.open_btn)
        hbox1.addWidget(self.clipboard_btn)
        hbox1.addWidget(self.opened_label)
        hbox1.addStretch()

        self.comb_box = QComboBox()
        self.comb_box.addItem("SIM1")
        self.comb_box.addItem("SIM2")
        self.comb_box.setFixedWidth(120)
        self.comb_box.setFont(CourierNewFont)
        self.comb_box.setDisabled(True)

        self.comb_box.currentIndexChanged.connect(self.comb_changed)

        self.exe_btn = QPushButton("Execute")
        self.exe_btn.setFixedWidth(120)
        self.exe_btn.setCheckable(False)
        self.exe_btn.setFont(CourierNewFont)
        self.exe_btn.setDisabled(True)

        self.exe_btn.clicked.connect(self.exe_msg)

        self.exe_label = QLabel()

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.comb_box)
        hbox2.addWidget(self.exe_btn)
        hbox2.addWidget(self.exe_label)
        hbox2.addStretch()

        self.SUM_label = QLabel()
        self.SUM_label.setText("Summary")
        self.SUM_label.setFont(CourierNewFont)
        self.SUM_list = MyQListWidget()
        self.SUM_list.setAutoScroll(True)
        self.SUM_list.setFixedWidth(700)
        self.SUM_list.setFont(CourierNewFont)
        self.SUM_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.SUM_list.setStyleSheet(style_sheet)
        SUM_vbox = QVBoxLayout()
        SUM_vbox.addWidget(self.SUM_label)
        SUM_vbox.addWidget(self.SUM_list)

        self.SUM_list.selection_changed.connect(self.clicked_rst)

        self.Prot_label = QLabel()
        self.Prot_label.setText("Protocol-Level Analysis")
        self.Prot_label.setFont(CourierNewFont)
        self.Prot_list = QTextBrowser()
        self.Prot_list.setFixedWidth(610)
        self.Prot_list.setFixedHeight(380)
        self.Prot_list.setFont(CourierNewFont)
        self.Prot_list.setStyleSheet(style_sheet)
        Prot_vbox = QVBoxLayout()
        Prot_vbox.addWidget(self.Prot_label)
        Prot_vbox.addWidget(self.Prot_list)

        self.App_label = QLabel()
        self.App_label.setText("Application-Level Analysis")
        self.App_label.setFont(CourierNewFont)
        self.App_list = QTextBrowser()
        self.App_list.setFont(CourierNewFont)
        self.App_list.setStyleSheet(style_sheet)
        self.App_list.setFixedWidth(610)
        self.App_list.setFixedHeight(380)
        App_vbox = QVBoxLayout()
        App_vbox.addWidget(self.App_label)
        App_vbox.addWidget(self.App_list)

        ProtApp_vbox = QVBoxLayout()
        ProtApp_vbox.addLayout(Prot_vbox)
        ProtApp_vbox.addWidget(QLabel())
        ProtApp_vbox.addLayout(App_vbox)
        ProtApp_vbox.addStretch()

        hbox3 = QHBoxLayout()
        hbox3.addLayout(SUM_vbox)
        hbox3.addLayout(ProtApp_vbox)
        hbox3.addStretch()

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addWidget(QLabel())

        self.tabs = QTabWidget()

        tab1 = QWidget()
        tab1.setLayout(hbox3)
        self.tabs.addTab(tab1, "APDU")

        tab2 = QWidget()
        self.File_system = QTextBrowser()
        self.File_system.setStyleSheet(style_sheet)
        File_vbox = QVBoxLayout()
        File_vbox.addWidget(self.File_system)
        tab2.setLayout(File_vbox)
        self.tabs.addTab(tab2, "File System")
        self.tabs.setFont(CourierNewFont)


        vbox.addWidget(self.tabs)
        vbox.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(vbox)
        main_layout.addWidget(QLabel())
        copyright_label = QLabel("Copyright 2022. JUSEOK AHN<ajs3013@lguplus.co.kr> all rights reserved.")
        main_layout.addWidget(copyright_label)

        self.setLayout(main_layout)
        self.setWindowTitle('SIM APDU Analyzer v3.0')
        self.setGeometry(110, 50, 0, 0)
        self.show()

    @pyqtSlot()
    def comb_changed(self):
        if self.opened_label.text() or '19B7' in self.paste_te.toPlainText():
            self.SUM_list.clear()
            self.App_list.clear()
            self.Prot_list.clear()
            self.File_system.clear()

            self.exe_btn.setEnabled(True)
            self.clipboard_btn.setDisabled(True)
            self.open_btn.setDisabled(True)
            self.exe_label.clear()

    @pyqtSlot()
    def open_file(self):
        self.SUM_list.clear()
        self.App_list.clear()
        self.Prot_list.clear()
        self.File_system.clear()

        fname = QFileDialog.getOpenFileName(self,'Load file','',"Text files(*.txt)")
        opened_file = fname[0]
        if fname[0]:
            f = open(fname[0],'rt',encoding='UTF8') #https://m.blog.naver.com/yejoon3117/221058408177
            with f:
                try:
                    self.msg_all = f.readlines()
                except:
                    print("read fail")
                for n in range(len(self.msg_all)):
                    self.msg_all[n] = self.msg_all[n].replace('\n', '')

        # QCAT logs
        if '[0x19B7]' not in self.msg_all[0]:
            self.msg_start, self.msg_end, self.msg_SN, self.msg_port, self.msg_type, self.msg_data \
                = msg_item.process(self.msg_all)

        # Clipboard logs (QXDM)
        elif '[0x19B7]' in self.msg_all[0]:
            for n in range(len(self.msg_all)):
                self.msg_all[n] = ' '.join(self.msg_all[n].split())
            msg_filter = []
            line_end = True
            for line in self.msg_all:
                if line.split(' ')[0] == '[0x19B7]':
                    msg_filter.append(line)
                    if '{' in line:
                        if '}' in line: line_end = True
                        else: line_end = False
                    else: line_end = True
                else:
                    if line_end is False:
                        msg_filter.append(line)
                        if '}' in line: line_end = True
            self.msg_all = msg_filter
            self.msg_start, self.msg_end, self.msg_SN, self.msg_port, self.msg_type, self.msg_data \
                = msg_item.process2(self.msg_all)

        if debug_mode:
            print('[File Name]', opened_file)
            print('msg_start :', len(self.msg_start), self.msg_start)
            print('msg_end   :', len(self.msg_end), self.msg_end)
            print('msg_SN    :', len(self.msg_SN), self.msg_SN)
            print('msg_port  :', len(self.msg_port), self.msg_port)
            print('msg_type  :', len(self.msg_type), self.msg_type)
            print('msg_data  :', len(self.msg_data), self.msg_data)
            print()

        if self.msg_data:
            self.opened_label.setText('APDU logs included in <'+opened_file+'>')
            self.open_btn.setDisabled(True)
            self.clipboard_btn.setDisabled(True)
            self.exe_btn.setEnabled(True)
            self.exe_label.clear()
            self.comb_box.setEnabled(True)
        else:
            self.opened_label.setText('APDU logs "NOT" included in <'+opened_file+'>')
            self.open_btn.setEnabled(True)
            self.clipboard_btn.setEnabled(True)
            self.exe_btn.setDisabled(True)
            self.exe_label.clear()
            self.comb_box.setDisabled(True)

    @pyqtSlot()
    def load_clipboard(self):
        self.SUM_list.clear()
        self.App_list.clear()
        self.Prot_list.clear()
        self.File_system.clear()

        self.msg_all = clipboard.paste()
        self.msg_all = self.msg_all.split('\r')
        for n in range(len(self.msg_all)):
            if '\n' in self.msg_all[n]:
                self.msg_all[n] = self.msg_all[n].replace('\n', '')

        # QXDM
        if '19B7' in self.msg_all[0]:
            for n in range(len(self.msg_all)):
                self.msg_all[n] = ' '.join(self.msg_all[n].split())
            msg_filter = []
            line_end = True
            for line in self.msg_all:
                if line.split(' ')[0] == '[0x19B7]':
                    msg_filter.append(line)
                    if '{' in line:
                        if '}' in line: line_end = True
                        else: line_end = False
                    else: line_end = True
                else:
                    if line_end is False:
                        msg_filter.append(line)
                        if '}' in line: line_end = True
            self.msg_all = msg_filter
            self.msg_start, self.msg_end, self.msg_SN, self.msg_port, self.msg_type, self.msg_data \
                = msg_item.process2(self.msg_all)

        # Shannon DM
        elif 'USIM_MAIN' in self.msg_all[0]:
            for msg in self.msg_all:
                print(msg.split('\t'))
            self.msg_data = ''
        else:
            self.msg_data = ''

        if debug_mode:
            print('[Clipboard]')
            print('msg_start :', len(self.msg_start), self.msg_start)
            print('msg_end   :', len(self.msg_end), self.msg_end)
            print('msg_SN    :', len(self.msg_SN), self.msg_SN)
            print('msg_port  :', len(self.msg_port), self.msg_port)
            print('msg_type  :', len(self.msg_type), self.msg_type)
            # print('msg_data  :', len(self.msg_data), self.msg_data)
            print()

        if self.msg_data:
            self.opened_label.setText('APDU logs included in clipboard (%d lines)'%len(self.msg_all))
            self.open_btn.setDisabled(True)
            self.clipboard_btn.setDisabled(True)
            self.exe_btn.setEnabled(True)
            self.exe_label.clear()
            self.comb_box.setEnabled(True)
        else:
            self.opened_label.setText('APDU logs "NOT" included in clipboard (%d lines)'%len(self.msg_all))
            self.open_btn.setEnabled(True)
            self.clipboard_btn.setEnabled(True)
            self.exe_btn.setDisabled(True)
            self.exe_label.clear()
            self.comb_box.setDisabled(True)

    @pyqtSlot()
    def exe_msg(self):
        self.SUM_list.clear()
        self.App_list.clear()
        self.Prot_list.clear()
        self.File_system.clear()

        self.exe_btn.setDisabled(True)
        self.open_btn.setEnabled(True)
        self.clipboard_btn.setEnabled(True)

        self.tabs.setCurrentIndex(0)

        port_num = self.comb_box.currentIndex()+1

        port_index =[]
        for n in range(len(self.msg_port)):
            if self.msg_port[n] == port_num:
                port_index.append(n)

        port_input = self.msg_all, self.msg_start, self.msg_end, self.msg_SN, self.msg_type, self.msg_data
        self.exe_start, self.exe_end, self.exe_type, self.exe_data = port.process(port_input, port_index)

        if debug_mode :
            print('[ SIM PORT', port_num, ']')
            print('exe_start  :', len(self.exe_start), self.exe_start)
            print('exe_end    :', len(self.exe_end), self.exe_end)
            print('exe_type   :', len(self.exe_type), self.exe_type)
            print('exe_data   :', len(self.exe_data), self.exe_data)
            print('')

        prot_input = self.exe_start, self.exe_end, self.exe_type, self.exe_data
        self.prot_start, self.prot_end, self.prot_type, self.prot_data = msg_prot.process(prot_input)

        if debug_mode :
            print('[ PROTOCOL LEVEL FILTER ]')
            print('prot_start :', len(self.prot_start), self.prot_start)
            print('prot_end   :', len(self.prot_end), self.prot_end)
            print('prot_type  :', len(self.prot_type), self.prot_type)
            print('prot_data  :', len(self.prot_data), self.prot_data)
            print()

        sum_input = self.msg_all, self.prot_start, self.prot_type, self.prot_data
        self.sum_rst, self.sum_log_ch, self.sum_log_ch_id, self.sum_cmd, self.sum_read, self.sum_error \
            = msg_sum.rst(sum_input)

        msg_files.process(self.sum_rst, self.sum_read, self.sum_log_ch, self.sum_log_ch_id)

        for line in self.sum_rst:
            item = QListWidgetItem(line)
            self.SUM_list.addItem(item)

            red_items = ['ERROR']
            magenta_items = ['Re-Sync']
            grey_items = ['(X)','(*)','Unknown']
            yellow_items = ['ENVELOPE','REFRESH']
            cyan_items = ['RESET', 'POWER']
            lightblue_items = ['MANAGE CHANNEL']
            lightgreen_items = ['AUTHENTICATE']

            if any(red_item in line for red_item in red_items):
                item.setFont(BoldFont)
                item.setForeground(QColor("red"))
            elif any(magenta_item in line for magenta_item in magenta_items):
                item.setForeground(QColor("magenta"))
            elif any(grey_item in line for grey_item in grey_items):
                item.setForeground(QColor("gray"))
            elif any(yellow_item in line for yellow_item in yellow_items):
                item.setForeground(QColor("yellow"))
            elif any(cyan_item in line for cyan_item in cyan_items):
                item.setForeground(QColor("cyan"))
            elif any(lightblue_item in line for lightblue_item in lightblue_items):
                item.setForeground(QColor("lightblue"))
            elif any(lightgreen_item in line for lightgreen_item in lightgreen_items):
                item.setForeground(QColor("lightgreen"))



        if debug_mode :
            print('[ SUMMARY FILTER ]')
            print('sum_rst       :', len(self.sum_rst), self.sum_rst)
            print('sum_log_ch    :', len(self.sum_log_ch), self.sum_log_ch)
            print('sum_log_ch_id :', len(self.sum_log_ch_id), self.sum_log_ch_id)
            print('sum_cmd       :', len(self.sum_cmd), self.sum_cmd)
            print('sum_read      :', len(self.sum_read), self.sum_read)
            print('sum_error     :', len(self.sum_error), self.sum_error)
            print()

        self.exe_label.setText("Complete")

    @pyqtSlot()
    def clicked_rst(self):
        if self.SUM_list.selected_items != set():
            selected_list = sorted(list(self.SUM_list.selected_items))
            # print(selected_list)
            # item_num = self.SUM_list.currentRow()

            prot_rst_show = ''
            for item_num in selected_list:
                prot_rst_input = self.msg_all, self.prot_start, self.prot_type, self.prot_data
                prot_rst = msg_prot.rst(prot_rst_input, item_num)
                if prot_rst: prot_rst_show += '=' * 80 + '\n'
                for n in prot_rst:
                    prot_rst_show += n +'\n'
            if prot_rst and len(selected_list)>0: prot_rst_show += '=' * 80
            self.Prot_list.setPlainText(prot_rst_show)

            app_rst_show = ''
            for item_num in selected_list:
                app_rst_input = self.prot_type, self.sum_cmd, self.sum_log_ch, self.sum_log_ch_id
                app_rst = msg_app.rst(app_rst_input, self.sum_read, self.sum_error, item_num)
                if app_rst: app_rst_show += '=' * 80 + '\n'
                for n in app_rst:
                    app_rst_show +=n +'\n'
            if app_rst and len(selected_list)>0: app_rst_show += '=' * 80
            self.App_list.setPlainText(app_rst_show)

class MyQListWidget(QListWidget):

    selection_changed = pyqtSignal(object)

    def __init__(self):
        QListWidget.__init__(self)
        self.selected_items = set()
        self.itemSelectionChanged.connect(self.sth_changed)

    def sth_changed(self):
        newly_selected_items = set([n.row() for n in self.selectedIndexes()])
        if newly_selected_items != self.selected_items:
            self.selected_items = newly_selected_items
        self.selection_changed.emit(self)

    def mousePressEvent(self, event):
        QListWidget.mousePressEvent(self, event)
        self.sth_changed()

    def mouseReleaseEvent(self, event):
        QListWidget.mouseReleaseEvent(self, event)
        self.sth_changed()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Basic_GUI()
    sys.exit(app.exec_())