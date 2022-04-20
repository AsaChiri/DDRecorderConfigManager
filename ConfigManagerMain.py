import os
import sys
import json
import traceback
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from easydict import EasyDict

from ConfigManagerMainWindow_UI import Ui_MainWindow
from ConfigManagerSpec import ConfigManagerSpec
def initData():
    return {
        "root": {
            "check_interval": 60,
            "print_interval": 10,
            "data_path": "./",
            "logger": {
                "log_path": "./log",
                "log_level": "INFO"
            },
            "request_header": {},
            "uploader": {
                "upload_by_edit": False,
                "thread_pool_workers": 1,
                "max_retry": 3
            },
            "enable_baiduyun": False
        },
        "spec": []
    }


class ConfigManagerMain(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(ConfigManagerMain,self).__init__()
        self.setupUi(self)
        # QMetaObject.connectSlotsByName(self)

        self.data = EasyDict(initData())
        self.specs = []
        self.fill_form_data()
        self.buttonGroupSavePushButton.setEnabled(False)
        self.dataPathPushButton.setEnabled(False)
        self.specConfigAddButton.setEnabled(False)
        self.specConfigDeleteButton.setEnabled(False)

    def fill_data(self, input_dict):
        root = input_dict.get("root", None)
        if root is not None:
            self.data.root.check_interval = root.get("check_interval", 60)
            self.data.root.print_interval = root.get("print_interval", 10)
            self.data.root.data_path = root.get("data_path", "./")
            logger = root.get("logger", None)
            if logger is not None:
                self.data.root.logger.log_path = logger.get(
                    "log_path", "./log")
                self.data.root.logger.log_level = logger.get(
                    "log_level", "INFO")
            self.data.root.request_header = root.get("request_header", {})
            uploader = root.get("uploader", None)
            if uploader is not None:
                self.data.root.uploader.upload_by_edit = uploader.get(
                    "upload_by_edit", False)
                self.data.root.uploader.thread_pool_workers = uploader.get(
                    "thread_pool_workers", 1)
                self.data.root.uploader.max_retry = uploader.get(
                    "max_retry", 3)
            self.data.root.enable_baiduyun = root.get("enable_baiduyun", False)
        self.data.spec = input_dict.get("spec", [])

    def fill_spec_table(self,spec,row_idx):
        self.specConfigTableWidget.setItem(row_idx,0,QTableWidgetItem("Bilibili"))
        self.specConfigTableWidget.setItem(row_idx,1,QTableWidgetItem(spec.room_id))
        self.specConfigTableWidget.setItem(row_idx,2,QTableWidgetItem("开启" if spec.clipper.enable_clipper else "关闭"))
        self.specConfigTableWidget.setItem(row_idx,3,QTableWidgetItem("开启" if spec.uploader.record.upload_record else "关闭"))
        self.specConfigTableWidget.setItem(row_idx,4,QTableWidgetItem("开启" if spec.uploader.clips.upload_clips else "关闭"))
        self.specConfigTableWidget.setItem(row_idx,5,QTableWidgetItem("开启" if spec.backup else "关闭"))

    def add_spec_row(self,spec):
        row_idx = self.specConfigTableWidget.rowCount()
        self.specConfigTableWidget.insertRow(row_idx)
        self.fill_spec_table(spec,row_idx)
        
    def clear_table(self):
        r = self.specConfigTableWidget.rowCount()
        for i in range(r,-1,-1):
            self.specConfigTableWidget.removeRow(i)

    def fill_form_data(self):
        self.checkIntervalSpinBox.setValue(self.data.root.check_interval)
        self.displayIntervalSpinBox.setValue(self.data.root.print_interval)
        self.dataPathLineEdit.setText(os.path.abspath(self.data.root.data_path))
        # self.maxUploadThreadSpinBox.setValue(self.data.root.uploader.thread_pool_workers)
        # self.maxRetrySpinBox.setValue(self.data.root.uploader.max_retry)
        # self.uploadByEditCheckBox.setChecked(self.data.root.uploader.upload_by_edit)
        self.clear_table()
        for spec in self.data.spec:
            cm_spec = ConfigManagerSpec(spec)
            self.specs.append(cm_spec)
            self.add_spec_row(cm_spec.specData)


    @pyqtSlot()
    def on_configFileViewerPushButton_clicked(self):
        openfile_name,_ = QFileDialog.getOpenFileName(
            self, '选择配置文件', './', 'JSON files(*.json)')
        self.file_path = openfile_name
        try:
            with open(self.file_path, "r", encoding="UTF-8") as f:
                input_data = json.load(f)
                self.fill_data(input_data)
            self.fill_form_data()
            self.buttonGroupSavePushButton.setEnabled(True)
            self.dataPathPushButton.setEnabled(True)
            self.specConfigAddButton.setEnabled(True)
            self.specConfigDeleteButton.setEnabled(True)
            self.configFileViewerFilePathLineEdit.setText(
                os.path.abspath(self.file_path))
        except Exception as e:
            r = QMessageBox.critical(self,"错误！","读取指定的配置文件时发生错误！")
        
    @pyqtSlot(int)
    def on_checkIntervalSpinBox_valueChanged(self,value):
        self.data.root.check_interval = value

    @pyqtSlot(int)
    def on_displayIntervalSpinBox_valueChanged(self,value):
        self.data.root.check_print_interval = value

    @pyqtSlot()
    def on_dataPathPushButton_clicked(self):
        data_path = QFileDialog.getExistingDirectory(self,"选取文件夹","./")
        self.data.root.data_path = data_path
        self.dataPathLineEdit.setText(os.path.abspath(self.data.root.data_path))

    # @pyqtSlot(int)
    # def on_maxUploadThreadSpinBox_valueChanged(self,value):
    #     self.data.root.uploader.thread_pool_workers = value

    # @pyqtSlot(int)
    # def on_maxRetrySpinBox_valueChanged(self,value):
    #     self.data.root.uploader.max_retry = value

    # @pyqtSlot(int)
    # def on_uploadByEditCheckBox_stateChanged(self, state):
    #     self.data.root.uploader.upload_by_edit = (state == Qt.Checked)

    @pyqtSlot()
    def on_specConfigAddButton_clicked(self):
        self.specConfigAddButton.setEnabled(False)
        self.specConfigDeleteButton.setEnabled(False)
        cm_spec = ConfigManagerSpec()
        self.specs.append(cm_spec)
        self.specs[-1].exitSignal.connect(self.flush_table)
        self.specs[-1].show()
        self.data.spec.append(dict(self.specs[-1].specData))
        self.add_spec_row(cm_spec.specData)


    @pyqtSlot()
    def on_specConfigDeleteButton_clicked(self):
        row_idx = self.specConfigTableWidget.selectedIndexes()[0].row()
        print(row_idx,)
        self.specConfigTableWidget.removeRow(row_idx)
        del self.specs[row_idx]
        del self.data.spec[row_idx]

    @pyqtSlot(int,int)
    def on_specConfigTableWidget_cellDoubleClicked(self,row_idx,col_idx):
        self.specConfigAddButton.setEnabled(False)
        self.specConfigDeleteButton.setEnabled(False)
        self.specs[row_idx].exitSignal.connect(self.flush_table)
        self.specs[row_idx].show()
        

        
    def flush_table(self):
        for idx,spec in enumerate(self.specs):
            self.data.spec[idx] = dict(spec.specData)
            self.fill_spec_table(spec.specData,idx)
        self.specConfigAddButton.setEnabled(True)
        self.specConfigDeleteButton.setEnabled(True)

    @pyqtSlot()
    def on_buttonGroupSavePushButton_clicked(self):
        backup = False
        for spec in self.data.spec:
            if spec.get("backup",False):
                backup = True
                break
        self.data.root.enable_baiduyun = backup
        with open(self.configFileViewerFilePathLineEdit.text(),"w",encoding="UTF-8") as f:
            json.dump(dict(self.data),f,ensure_ascii=False)
            r = QMessageBox.information(self,"保存成功！","配置文件已成功保存。")

    @pyqtSlot()
    def on_buttonGroupCancelPushButton_clicked(self):
        self.data = EasyDict(initData())
        self.specs = []
        self.configFileViewerFilePathLineEdit.setText("")
        self.fill_form_data()
        self.buttonGroupSavePushButton.setEnabled(False)
        self.dataPathPushButton.setEnabled(False)
        self.specConfigAddButton.setEnabled(False)
        self.specConfigDeleteButton.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
 
    window = ConfigManagerMain()
    window.show()
 
    sys.exit(app.exec_())