import io
import json
import os
import zipfile
import subprocess

import filetype
import requests
from easydict import EasyDict
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QMainWindow

from ConfigManagerSpec_UI import Ui_MainWindow


class ConfigManagerSpec(QMainWindow, Ui_MainWindow):
    exitSignal = QtCore.pyqtSignal()

    def __init__(self, specData=None):
        super(ConfigManagerSpec, self).__init__()
        self.setupUi(self)
        self.biliup_process = None
        # QMetaObject.connectSlotsByName(self)
        if specData:
            self.specData = EasyDict()
            self.initSpecData()
            self.valSpecData(specData)
            self.initFormData()
        else:
            self.specData = EasyDict()
            self.initSpecData()
            self.initFormData()

    def valSpecData(self, input_dict):
        # self.specData.site_name = "bilibili"
        self.specData.room_id = input_dict.get("room_id", "")
        recorder = input_dict.get("recorder", None)
        if recorder is not None:
            self.specData.recorder.keep_raw_record = recorder.get(
                "keep_raw_record", False)
        parser = input_dict.get("parser", None)
        if parser is not None:
            self.specData.parser.interval = parser.get("interval", 30)
            self.specData.parser.up_ratio = parser.get("up_ratio", 2.5)
            self.specData.parser.down_ratio = parser.get("down_ratio", 0.75)
            self.specData.parser.topK = parser.get("topK", 5)
        clipper = input_dict.get("clipper", None)
        if clipper is not None:
            self.specData.clipper.enable_clipper = clipper.get(
                "enable_clipper", True)
            self.specData.clipper.min_length = clipper.get("min_length", 60)
            self.specData.clipper.start_offset = clipper.get("start_offset", 0)
            self.specData.clipper.end_offset = clipper.get("end_offset", 0)
        manual_clipper = input_dict.get("manual_clipper", None)
        if manual_clipper is not None:
            self.specData.manual_clipper.enabled = manual_clipper.get(
                "enabled", False)
            self.specData.manual_clipper.uid = manual_clipper.get("uid", "")
        uploader = input_dict.get("uploader", None)
        if uploader is not None:
            account = uploader.get("account", None)
            if account is not None:
                self.specData.uploader.account.username = account.get(
                    "username", "")
                self.specData.uploader.account.password = account.get(
                    "password", "")
                self.specData.uploader.account.access_token = account.get(
                    "access_token", "")
                self.specData.uploader.account.refresh_token = account.get(
                    "refresh_token", "")
                cookies = account.get("cookies", None)
                if cookies is not None:
                    self.specData.uploader.account.cookies.SESSDATA = cookies.get(
                        "SESSDATA", "")
                    self.specData.uploader.account.cookies.bili_jct = cookies.get(
                        "bili_jct", "")
                    self.specData.uploader.account.cookies.DedeUserID = cookies.get(
                        "DedeUserID", "")
                    self.specData.uploader.account.cookies.DedeUserID__ckMd5 = cookies.get(
                        "DedeUserID__ckMd5", "")
                    self.specData.uploader.account.cookies.sid = cookies.get(
                        "sid", "")
        self.specData.uploader.copyright = uploader.get("copyright", 2)
        record = uploader.get("record", None)
        if record is not None:
            self.specData.uploader.record.upload_record = record.get(
                "upload_record", False)
            self.specData.uploader.record.keep_record_after_upload = record.get(
                "keep_record_after_upload", False)
            self.specData.uploader.record.split_interval = record.get(
                "split_interval", 3600)
            self.specData.uploader.record.title = record.get("title", "")
            self.specData.uploader.record.tid = record.get("tid", 24)
            self.specData.uploader.record.tags = record.get("tags", [])
            self.specData.uploader.record.cover = record.get("cover", "")
            self.specData.uploader.record.desc = record.get("desc", "")
        clips = uploader.get("clips", None)
        if clips is not None:
            self.specData.uploader.clips.upload_clips = clips.get(
                "upload_clips", False)
            self.specData.uploader.clips.keep_clips_after_upload = clips.get(
                "keep_clips_after_upload", False)
            self.specData.uploader.clips.title = clips.get("title", "")
            self.specData.uploader.clips.tid = clips.get("tid", 24)
            self.specData.uploader.clips.tags = clips.get("tags", [])
            self.specData.uploader.clips.cover = clips.get("cover", "")
            self.specData.uploader.clips.desc = clips.get("desc", "")
        self.specData.backup = input_dict.get("backup", False)

    def valEnableUploader(self):
        if self.specData.uploader.account.username != "" and self.specData.uploader.account.password != "":
            self.uploadRecordCheckBox.setEnabled(True)
            self.uploadClipsCheckBox.setEnabled(True)
            self.biliLoginPushButton.setEnabled(True)
        else:
            self.uploadRecordCheckBox.setChecked(False)
            self.uploadRecordCheckBox.setEnabled(False)
            self.uploadClipsCheckBox.setChecked(False)
            self.uploadClipsCheckBox.setEnabled(False)
            self.biliLoginPushButton.setEnabled(False)

    def initSpecData(self):
        # self.specData.site_name = "bilibili"
        self.specData.room_id = ""
        self.specData.recorder = EasyDict()
        self.specData.recorder.keep_raw_record = False
        self.specData.parser = EasyDict()
        self.specData.parser.interval = 30
        self.specData.parser.up_ratio = 2.5
        self.specData.parser.down_ratio = 0.75
        self.specData.parser.topK = 5
        self.specData.clipper = EasyDict()
        self.specData.clipper.enable_clipper = True
        self.specData.clipper.min_length = 30
        self.specData.clipper.start_offset = 0
        self.specData.clipper.end_offset = 0
        self.specData.manual_clipper = EasyDict()
        self.specData.manual_clipper.enabled = False
        self.specData.manual_clipper.uid = ""
        self.specData.uploader = EasyDict()
        self.specData.uploader.account = EasyDict()
        self.specData.uploader.account.username = ""
        self.specData.uploader.account.password = ""
        self.specData.uploader.account.access_token = ""
        self.specData.uploader.account.refresh_token = ""
        self.specData.uploader.account.cookies = EasyDict()
        self.specData.uploader.account.cookies.SESSDATA = ""
        self.specData.uploader.account.cookies.bili_jct = ""
        self.specData.uploader.account.cookies.DedeUserID = ""
        self.specData.uploader.account.cookies.DedeUserID__ckMd5 = ""
        self.specData.uploader.account.cookies.sid = ""
        self.specData.uploader.copyright = 2
        self.specData.uploader.record = EasyDict()
        self.specData.uploader.record.upload_record = False
        self.specData.uploader.record.keep_record_after_upload = False
        self.specData.uploader.record.split_interval = 3600
        self.specData.uploader.record.title = ""
        self.specData.uploader.record.tid = 24
        self.specData.uploader.record.tags = []
        self.specData.uploader.record.cover = ""
        self.specData.uploader.record.desc = ""
        self.specData.uploader.clips = EasyDict()
        self.specData.uploader.clips.upload_clips = False
        self.specData.uploader.clips.keep_clips_after_upload = False
        self.specData.uploader.clips.title = ""
        self.specData.uploader.clips.tid = 24
        self.specData.uploader.clips.tags = []
        self.specData.uploader.clips.cover = ""
        self.specData.uploader.clips.desc = ""
        self.specData.backup = False

    def initFormData(self):
        def fillComboBox(cb, number):
            for i in range(cb.count()):
                text = cb.itemText(i)
                text_num = int(text.split(":")[0])
                if number == text_num:
                    return i
            return 0
        # self.siteSelectorComboBox.setCurrentText()
        self.roomIdLineEdit.setText(self.specData.room_id)
        self.keepRawRecordCheckBox.setChecked(
            self.specData.recorder.keep_raw_record)
        self.baiduCheckBox.setChecked(self.specData.backup)
        self.parseIntervalSpinBox.setValue(self.specData.parser.interval)
        self.upRatioDoubleSpinBox.setValue(self.specData.parser.up_ratio)
        self.downRatioDoubleSpinBox.setValue(self.specData.parser.down_ratio)
        self.topKSpinBox.setValue(self.specData.parser.topK)
        self.enableClipperCheckBox.setChecked(
            self.specData.clipper.enable_clipper)
        self.minLengthSpinBox.setValue(self.specData.clipper.min_length)
        self.beginOffsetSpinBox.setValue(self.specData.clipper.start_offset)
        self.endOffsetSpinBox.setValue(self.specData.clipper.end_offset)
        self.copyrightCheckBox.setChecked(
            self.specData.uploader.copyright == 1)
        self.enableManualClipperCheckBox.setChecked(
            self.specData.manual_clipper.enabled)
        self.manualClipperControllerLineEdit.setText(
            self.specData.manual_clipper.uid)
        self.accountLineEdit.setText(self.specData.uploader.account.username)
        self.passwordLineEdit.setText(self.specData.uploader.account.password)
        self.uploadRecordCheckBox.setChecked(
            self.specData.uploader.record.upload_record)
        self.keepRecordCheckBox.setChecked(
            self.specData.uploader.record.keep_record_after_upload)
        self.splitIntervalSpinBox.setValue(
            self.specData.uploader.record.split_interval)
        self.recordTitleLineEdit.setText(self.specData.uploader.record.title)
        self.recordTidComboBox.setCurrentIndex(fillComboBox(
            self.recordTidComboBox, self.specData.uploader.record.tid))
        self.recordTagsLineEdit.setText(
            " ".join(self.specData.uploader.record.tags))
        self.recordCoverPathLineEdit.setText(
            os.path.abspath(self.specData.uploader.record.cover) if self.specData.uploader.record.cover else "")
        self.recordDescPlainTextEdit.setPlainText(
            self.specData.uploader.record.desc)
        self.uploadClipsCheckBox.setChecked(
            self.specData.uploader.clips.upload_clips)
        self.keepClipsCheckBox.setChecked(
            self.specData.uploader.clips.keep_clips_after_upload)
        self.clipsTitleLineEdit.setText(self.specData.uploader.clips.title)
        self.clipsTidComboBox.setCurrentIndex(fillComboBox(
            self.clipsTidComboBox, self.specData.uploader.clips.tid))
        self.clipsTagsLineEdit.setText(
            " ".join(self.specData.uploader.clips.tags))
        self.clipsCoverPathLineEdit.setText(
            os.path.abspath(self.specData.uploader.clips.cover) if self.specData.uploader.clips.cover else "")
        self.clipsDescPlainTextEdit.setPlainText(
            self.specData.uploader.clips.desc)

        self.valEnableUploader()

    @pyqtSlot(str)
    def on_siteSelector_currentTextChanged(self, text):
        pass

    @pyqtSlot(str)
    def on_roomIdLineEdit_textChanged(self, text):
        if text.isdigit():
            self.specData.room_id = text
        else:
            self.roomIdLineEdit.setText("")

    @pyqtSlot(int)
    def on_keepRawRecordCheckBox_stateChanged(self, state):
        self.specData.recorder.keep_raw_record = (state == Qt.Checked)

    @pyqtSlot(int)
    def on_baiduCheckBox_stateChanged(self, state):
        self.specData.backup = (state == Qt.Checked)

    @pyqtSlot(int)
    def on_parseIntervalSpinBox_valueChanged(self, number):
        self.specData.parser.interval = number

    @pyqtSlot(float)
    def on_upRatioDoubleSpinBox_valueChanged(self, number):
        self.specData.parser.up_ratio = number

    @pyqtSlot(float)
    def on_downRatioDoubleSpinBox_valueChanged(self, number):
        self.specData.parser.down_ratio = number

    @pyqtSlot(int)
    def on_topKSpinBox_valueChanged(self, number):
        self.specData.parser.topK = number

    @pyqtSlot(int)
    def on_enableClipperCheckBox_stateChanged(self, state):
        self.specData.clipper.enable_clipper = (state == Qt.Checked)

    @pyqtSlot(int)
    def on_beginOffsetSpinBox_valueChanged(self, number):
        self.specData.clipper.start_offset = number

    @pyqtSlot(int)
    def on_endOffsetSpinBox_valueChanged(self, number):
        self.specData.clipper.end_offset = number

    @pyqtSlot(int)
    def on_minLengthSpinBox_valueChanged(self, number):
        self.specData.clipper.min_length = number

    @pyqtSlot(int)
    def on_enableManualClipperCheckBox_stateChanged(self, state):
        self.specData.manual_clipper.enabled = (state == Qt.Checked)

    @pyqtSlot(str)
    def on_manualClipperControllerLineEdit_textChanged(self, text):
        if text.isdigit():
            self.specData.manual_clipper.uid = text
        else:
            self.manualClipperControllerLineEdit.setText("")

    @pyqtSlot(str)
    def on_accountLineEdit_textChanged(self, text):
        self.specData.uploader.account.username = text
        self.valEnableUploader()

    @pyqtSlot(str)
    def on_passwordLineEdit_textChanged(self, text):
        self.specData.uploader.account.password = text
        self.valEnableUploader()

    # @pyqtSlot(str)
    # def on_accessTokenLineEdit_textChanged(self, text):
    #     self.specData.uploader.account.access_token = text
    #     self.valEnableUploader()

    # @pyqtSlot(str)
    # def on_refreshTokenEdit_textChanged(self, text):
    #     self.specData.uploader.account.refresh_token = text
    #     self.valEnableUploader()

    @pyqtSlot()
    def on_biliLoginPushButton_clicked(self):
        biliup_filename = "./biliup.exe"
        if not os.path.exists(biliup_filename):
            r = QMessageBox.warning(self, "警告！", "未检测到biliup程序，点击确认将会自动下载最新版本到本地。",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if r == QMessageBox.Yes:
                git_api_resp = requests.get(
                    "https://api.github.com/repos/ForgQi/biliup-rs/releases/latest").json()
                for asset in git_api_resp.get("assets", []):
                    if asset['name'].find('x86_64-windows') != -1:
                        with open(biliup_filename, "wb") as file:
                            response = requests.get(asset['browser_download_url'])
                            z = zipfile.ZipFile(io.BytesIO(response.content))
                            file.write(z.read(os.path.join(os.path.splitext(asset['name'])[0]+"/biliup.exe")))
                    else:
                        r = QMessageBox.critical(self, "错误！", "无法获取biliup！")
            else:
                return
        r = QMessageBox.information(
            self, "注意！", "即将使用biliup进行一次B站登录以获取鉴权信息，请根据打开窗口上的提示进行操作。", QMessageBox.Yes, QMessageBox.Yes)
        if r == QMessageBox.Yes:
            if self.biliup_process is None:
                self.biliup_process = subprocess.Popen(f'start /wait biliup.exe login', shell=True)
                self.biliup_process.wait()
                self.write_cookies()
        else:
            return

    def write_cookies(self):
        cookies_path = './cookies.json'
        if os.path.exists(cookies_path):
            with open(cookies_path,"r",encoding="utf-8") as f:
                cookies_info = json.load(f)
            for cookie_item in cookies_info['cookie_info']['cookies']:
                self.specData.uploader.account.cookies[cookie_item['name']] = cookie_item['value']
            self.specData.uploader.account.access_token = cookies_info['token_info']['access_token']
            self.specData.uploader.account.refresh_token = cookies_info['token_info']['refresh_token']
        else:
            r = QMessageBox.critical(self, "错误！", "Cookies文件不正确，请重新进行鉴权！")

    @pyqtSlot(int)
    def on_copyrightCheckBox_stateChanged(self, state):
        if state == Qt.Checked:
            r = QMessageBox.warning(self, "警告！", "录播和自动切片在未授权情况下使用“自制”类型投稿可能导致稿件无法通过等后果！请进行确认！",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if r == QMessageBox.Yes:
                self.specData.uploader.copyright = 1
            else:
                self.specData.uploader.copyright = 2
        else:
            self.specData.uploader.copyright = 2
        self.copyrightCheckBox.setChecked(
            self.specData.uploader.copyright == 1)

    @pyqtSlot(int)
    def on_uploadRecordCheckBox_stateChanged(self, state):
        self.specData.uploader.record.upload_record = (state == Qt.Checked)

    @pyqtSlot(int)
    def on_keepRecordCheckBox_stateChanged(self, state):
        self.specData.uploader.record.keep_record_after_upload = (
            state == Qt.Checked)

    @pyqtSlot(int)
    def on_splitIntervalSpinBox_valueChanged(self, number):
        self.specData.uploader.record.split_interval = number

    @pyqtSlot(str)
    def on_recordTitleLineEdit_textChanged(self, text):
        self.specData.uploader.record.title = text

    @pyqtSlot(str)
    def on_recordTidComboBox_currentTextChanged(self, text):
        self.specData.uploader.record.tid = int(text.split(":")[0])

    @pyqtSlot(str)
    def on_recordTagsLineEdit_textChanged(self, text):
        self.specData.uploader.record.tags = text.split(" ")

    @pyqtSlot(str)
    def on_recordCoverPathLineEdit_textChanged(self, text):
        if os.path.isfile(text) and filetype.is_image(text):
            self.specData.uploader.record.title = os.path.abspath(text)
        else:
            self.recordCoverPathLineEdit.setText("")

    @pyqtSlot()
    def on_recordCoverBrowserPushButton_clicked(self):
        openfile_name, _ = QFileDialog.getOpenFileName(
            self, '选择封面图像', './', 'Image file(*.jpg *.png *.webp)')
        if os.path.exists(openfile_name) and filetype.is_image(openfile_name):
            self.specData.uploader.record.title = os.path.abspath(
                openfile_name)
            self.recordCoverPathLineEdit.setText(
                os.path.abspath(openfile_name))
        else:
            r = QMessageBox.critical(self, "错误！", "不正确的图像！")

    @pyqtSlot()
    def on_recordDescPlainTextEdit_textChanged(self):
        self.specData.uploader.record.desc = self.recordDescPlainTextEdit.toPlainText()

    @pyqtSlot(int)
    def on_uploadClipsCheckBox_stateChanged(self, state):
        self.specData.uploader.clips.upload_clips = (state == Qt.Checked)

    @pyqtSlot(int)
    def on_keepClipsCheckBox_stateChanged(self, state):
        self.specData.uploader.clips.keep_clips_after_upload = (
            state == Qt.Checked)

    @pyqtSlot(str)
    def on_clipsTitleLineEdit_textChanged(self, text):
        self.specData.uploader.clips.title = text

    @pyqtSlot(str)
    def on_clipsTidComboBox_currentTextChanged(self, text):
        self.specData.uploader.clips.tid = int(text.split(":")[0])

    @pyqtSlot(str)
    def on_clipsTagsLineEdit_textChanged(self, text):
        self.specData.uploader.clips.tags = text.split(" ")

    @pyqtSlot(str)
    def on_clipsCoverPathLineEdit_textChanged(self, text):
        if os.path.isfile(text) and filetype.is_image(text):
            self.specData.uploader.clips.title = os.path.abspath(text)
        else:
            self.clipsCoverBrowserPathLineEdit.setText("")

    @pyqtSlot()
    def on_clipsCoverBrowserPushButton_clicked(self):
        openfile_name, _ = QFileDialog.getOpenFileName(
            self, '选择封面图像', './', 'Image file(*.jpg *.png *.webp)')
        if os.path.exists(openfile_name) and filetype.is_image(openfile_name):
            self.specData.uploader.clips.title = os.path.abspath(openfile_name)
            self.clipsCoverBrowserPathLineEdit.setText(
                os.path.abspath(openfile_name))
        else:
            r = QMessageBox.critical(self, "错误！", "不正确的图像！")

    @pyqtSlot()
    def on_clipsDescPlainTextEdit_textChanged(self):
        self.specData.uploader.clips.desc = self.clipsDescPlainTextEdit.toPlainText()

    def closeEvent(self, event):
        self.exitSignal.emit()
