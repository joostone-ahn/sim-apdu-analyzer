import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import msg_item
import port
import msg_sum
import msg_app
import msg_prot
import clipboard

BoldFont = QtGui.QFont()
BoldFont.setBold(True)

CourierNewFont = QtGui.QFont()
CourierNewFont.setFamily("Courier New")
# CourierNewFont.setFamily("Consolas")


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

        self.SEARCH_te = QPlainTextEdit()
        self.SEARCH_te.setFont(CourierNewFont)
        


        self.SUM_label = QLabel()
        self.SUM_label.setText("Summary")
        self.SUM_label.setFont(CourierNewFont)
        self.SUM_list = MyQListWidget()
        self.SUM_list.setAutoScroll(True)
        self.SUM_list.setFixedWidth(610)
        self.SUM_list.setFixedHeight(400)
        self.SUM_list.setFont(CourierNewFont)
        self.SUM_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        SUM_vbox = QVBoxLayout()
        SUM_vbox.addWidget(self.SUM_label)
        SUM_vbox.addWidget(self.SUM_list)

        self.SUM_list.selection_changed.connect(self.clicked_rst)

        self.Prot_label = QLabel()
        self.Prot_label.setText("Protocol-Level Analysis")
        self.Prot_label.setFont(CourierNewFont)
        self.Prot_list = QTextBrowser()
        self.Prot_list.setFixedWidth(610)
        self.Prot_list.setFixedHeight(400)
        self.Prot_list.setFont(CourierNewFont)
        Prot_vbox = QVBoxLayout()
        Prot_vbox.addWidget(self.Prot_label)
        Prot_vbox.addWidget(self.Prot_list)

        hbox3 = QHBoxLayout()
        hbox3.addLayout(SUM_vbox)
        hbox3.addLayout(Prot_vbox)
        hbox3.addStretch()

        self.SIM_Info_label = QLabel()
        self.SIM_Info_label.setText("SIM information and OTA updated")
        self.SIM_Info_label.setFont(CourierNewFont)
        self.SIM_Info_list = QTextBrowser()
        self.SIM_Info_list.setFixedWidth(610)
        self.SIM_Info_list.setFixedHeight(400)
        self.SIM_Info_list.setFont(CourierNewFont)
        SUM_File_vbox = QVBoxLayout()
        SUM_File_vbox.addWidget(self.SIM_Info_label)
        SUM_File_vbox.addWidget(self.SIM_Info_list)

        self.App_label = QLabel()
        self.App_label.setText("Application-Level Analysis")
        self.App_label.setFont(CourierNewFont)
        self.App_list = QTextBrowser()
        self.App_list.setFont(CourierNewFont)
        self.App_list.setFixedWidth(610)
        self.App_list.setFixedHeight(400)
        App_vbox = QVBoxLayout()
        App_vbox.addWidget(self.App_label)
        App_vbox.addWidget(self.App_list)

        hbox4 = QHBoxLayout()
        hbox4.addLayout(SUM_File_vbox)
        hbox4.addLayout(App_vbox)
        hbox4.addStretch()

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addWidget(QLabel())
        vbox.addLayout(hbox3)
        vbox.addWidget(QLabel())
        vbox.addLayout(hbox4)
        vbox.addStretch()
        vbox.addWidget(QLabel())
        vbox.addWidget(QLabel("Copyright 2022. JUSEOK AHN<ajs3013@lguplus.co.kr> all rights reserved."))

        self.setLayout(vbox)
        self.setWindowTitle('Dual SIM APDU Analyzer v2.1')
        # self.showMaximized()
        self.setGeometry(110, 50, 0, 0)
        self.show()


    @pyqtSlot()
    def comb_changed(self):
        if self.opened_label.text() or '19B7' in self.paste_te.toPlainText():
            self.SUM_list.clear()
            self.App_list.clear()
            self.Prot_list.clear()
            self.SIM_Info_list.clear()
            self.exe_btn.setEnabled(True)
            self.clipboard_btn.setDisabled(True)
            self.open_btn.setDisabled(True)
            self.exe_label.clear()

    @pyqtSlot()
    def open_file(self):
        self.SUM_list.clear()
        self.App_list.clear()
        self.Prot_list.clear()
        self.SIM_Info_list.clear()

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

        if '[0x19B7]' not in self.msg_all[0]:
            self.msg_start, self.msg_end, self.msg_SN, self.msg_port, self.msg_type, self.msg_data \
                = msg_item.process(self.msg_all)
            self.load_type = 'File'
        else:
            self.msg_start, self.msg_end, self.msg_SN, self.msg_port, self.msg_type, self.msg_data \
                = msg_item.process2(self.msg_all)
            self.load_type = 'Paste'

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
        self.SIM_Info_list.clear()

        self.msg_all = clipboard.paste()
        self.msg_all = self.msg_all.split('\r')
        for n in range(len(self.msg_all)):
            if '\n' in self.msg_all[n]:
                self.msg_all[n] = self.msg_all[n].replace('\n','')

        self.msg_start, self.msg_end, self.msg_SN, self.msg_port, self.msg_type, self.msg_data \
            = msg_item.process2(self.msg_all)

        if debug_mode:
            print('[Clipboard]')
            print('msg_start :', len(self.msg_start), self.msg_start)
            print('msg_end   :', len(self.msg_end), self.msg_end)
            print('msg_SN    :', len(self.msg_SN), self.msg_SN)
            print('msg_port  :', len(self.msg_port), self.msg_port)
            print('msg_type  :', len(self.msg_type), self.msg_type)
            print('msg_data  :', len(self.msg_data), self.msg_data)
            print()

        if self.msg_data:
            self.opened_label.setText('APDU logs included in clipboard (%d lines)'%len(self.msg_all))
            self.open_btn.setDisabled(True)
            self.clipboard_btn.setDisabled(True)
            self.exe_btn.setEnabled(True)
            self.exe_label.clear()
            self.comb_box.setEnabled(True)
            self.load_type = 'Paste'
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
        self.SIM_Info_list.clear()
        self.exe_btn.setDisabled(True)
        self.open_btn.setEnabled(True)
        self.clipboard_btn.setEnabled(True)

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
        self.sum_rst, self.sum_log_ch, self.sum_log_ch_id, self.sum_cmd, self.sum_read, self.sum_error, self.sum_remote \
            = msg_sum.rst(sum_input, self.load_type)
        for n in self.sum_rst:
            self.SUM_list.addItem(n)

        sum_remote_show = ''
        for n in self.sum_remote:
            if len(n)==2:
                sum_remote_show += '-' * 80 + '\n'
                sum_remote_show += '%20s'%n[0] + '   '
                if '\n' in n[1]:
                    item_list = n[1].split('\n')
                    for m in range(len(item_list)):
                        if m > 0: sum_remote_show += ' '*23
                        sum_remote_show += item_list[m] + '\n'
                else:
                    sum_remote_show += n[1].replace('   ', ' ') + '\n'
            if len(n)>2:
                sum_remote_show += '-' * 80 + '\n'
                sum_remote_show += '%20s'%n[0] + '   '
                if '\n' in n[1] or '\n' in n[2]:
                    if '\n' in n[1]:
                        item_list = n[1].split('\n')
                        for m in range(len(item_list)):
                            if m > 0: sum_remote_show += ' '*23
                            sum_remote_show += item_list[m] + '\n'
                    if '\n' in n[2]:
                        item_list = n[2].split('\n')
                        for m in range(len(item_list)):
                            if m > 0: sum_remote_show += '%20s'%'>>>' + '   '
                            sum_remote_show += item_list[m] + '\n'
                else:
                    sum_remote_show += n[1].replace('   ', ' ') + '\n'
                    sum_remote_show += '%20s'%'>>>' + '   ' + n[2].replace('   ', ' ') + '\n'
        if sum_remote_show:
            sum_remote_show += '-' * 80
            self.SIM_Info_list.setText(sum_remote_show)

        if debug_mode :
            print('[ SUMMARY FILTER ]')
            print('sum_rst       :', len(self.sum_rst), self.sum_rst)
            print('sum_log_ch    :', len(self.sum_log_ch), self.sum_log_ch)
            print('sum_log_ch_id :', len(self.sum_log_ch_id), self.sum_log_ch_id)
            print('sum_cmd       :', len(self.sum_cmd), self.sum_cmd)
            print('sum_read      :', len(self.sum_read), self.sum_read)
            print('sum_error     :', len(self.sum_error), self.sum_error)
            print('sum_remote    :', len(self.sum_remote), self.sum_remote)
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
                prot_rst = msg_prot.rst(prot_rst_input, item_num, self.load_type)
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

    # @pyqtSlot()
    # def save_msg(self):
    #     save_contents =''
    #
    #     for n in range(len(self.sum_rst)):
    #         save_contents += '='*150 + '\n'
    #         save_contents += self.sum_rst[n] + '\n'
    #         save_contents += '='*150 + '\n'
    #         prot_rst_input = self.msg_all, self.prot_start, self.prot_type, self.prot_data, n
    #         prot_rst = msg_prot.rst(prot_rst_input)
    #         for m in prot_rst[1:]:
    #             save_contents += m +'\n'
    #         save_contents += '\n'
    #
    #     save_path = QFileDialog.getSaveFileName(self,'Save file','',"Text files(*.txt)")
    #     fp = open(save_path[0], "w")
    #     fp.write(save_contents)
    #     fp.close()
    #
    #     self.saved_label.setText(save_path[0])
    #     self.save_btn.setDisabled(True)

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