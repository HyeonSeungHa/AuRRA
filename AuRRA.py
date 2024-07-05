import sys
import os
import io
import time
import traceback
import urllib.request

from PIL import Image
import requests
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtCore import QDir, QUrl, Qt, QBasicTimer
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pyqtgraph as pg
import numpy as np
import soundfile as sf
import pymysql
from requests import get
import datetime

import json


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('AuRRA')

        ######################################### Action
        self.url = None
        self.url_api = None
        self.gb_rows = None
        self.success_url = None
        self.day = 0

        specImageAction = QAction('&이미지 추출', self)
        specImageAction.setShortcut('Ctrl+S')
        specImageAction.setStatusTip('Spectogram Image')
        specImageAction.triggered.connect(self.specimage)

        devEnv = QAction('&개발', self)
        devEnv.setShortcut('Ctrl+D')
        devEnv.triggered.connect(self.dev)

        admEnv = QAction('&운영', self)
        admEnv.setShortcut('Ctrl+A')
        admEnv.triggered.connect(self.adm)

        oneDayAction = QAction('&1일 전', self)
        oneDayAction.triggered.connect(self.oneDay)

        threeDayAction = QAction('&3일 전', self)
        threeDayAction.triggered.connect(self.threeDay)

        sevenDayAction = QAction('&7일 전',self)
        sevenDayAction.triggered.connect(self.sevenDay)

        tenDayAction = QAction('&10일 전',self)
        tenDayAction.triggered.connect(self.tenDay)
        ######################################### Action

        ######################################### MenuBar AddAction

        menuBar = self.menuBar()
        envMenu = menuBar.addMenu('&환경')

        apiMenu = menuBar.addMenu('&Api 호출')
        cleanupMenu = menuBar.addMenu('&음원 파일 정리')
        envMenu.addAction(devEnv)
        envMenu.addAction(admEnv)
        apiMenu.addAction(specImageAction)
        cleanupMenu.addAction(oneDayAction)
        cleanupMenu.addAction(threeDayAction)
        cleanupMenu.addAction(sevenDayAction)
        cleanupMenu.addAction(tenDayAction)
        ######################################### MenuBar AddAction


    def initUI(self):

        font_path = 'C:\Windows\Fonts\gulim.ttc'
        font = font_manager.FontProperties(fname=font_path).get_name()
        rc('font', family=font)

        # 변수 선언
        self.params = {
            "gid": "string",
            "is_dev_file": 0,
            "file_key": "string",
            "usr_mngt_unq_no": "string",
            "anls_req_seq": "string",
            "result_url": "req_server 주소",
            "data_gb": "string",
            "stdd_qlty_mtrx_seq": "string"
            }
        self.req_url = 'req_server 주소'
        
        self.usr_mngt_unq_no = None
        self.anls_req_seq = None
        self.ax = None
        self.clntco_req_mngt_no = None
        self.wav_count = 0
        self.split_count = 0
        self.img_count = 0

        self.audio_path = None
        self.fileid = None
        self.position1 = None
        self.samplerate = None
        self.y = None
        self.ny = None
        self.start = None
        self.rows = None

        self.rows_detl = None
        self.car_num = None
        self.client_name = None
        self.res = None
        self.res_json = None
        self.raw_gid = None
        self.wav_gid = None

        self.split_wav_path = None
        self.split_img_path = None
        self.file_size = None
        self.remark = None
        self.strmvdo_gid = None
        self.split_video_path = None

        self.psnl_crp_gb_code = None
        self.aostc_rfng_cln_yn_co = None
        self.aostc_rfng_mthd_gb_co = None
        self.qlty_anls_rslt_code = None

        self.image_gid = None
        self.image_plain_gid = None
        self.rda_fan = None
        self.datetime = None
        
        # 사용자 선언
        self.fst_usr_unq_no = 'U21091600001'
        self.lst_usr_unq_no = 'U21091600001'

        ######################################### Home Screen Setting

        self.Player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.playBtn = QPushButton('재생')
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.textBtn = QPushButton('시작점')
        self.textBtn.setFixedSize(80, 20)
        self.insertBtn = QPushButton('음원 세부정보 저장')


        self.sec4 = QPushButton('4초 편집')
        self.sec4.setFixedSize(80,20)
        self.sec3 = QPushButton('3초 편집')
        self.sec3.setFixedSize(80,20)
        self.pure = QRadioButton('팬 미포함')
        self.pure.setFixedSize(80, 20)
        self.fan = QRadioButton('팬 포함')
        self.fan.setFixedSize(80, 20)
        self.inquiryBtn = QPushButton('조회')

        self.insertBtn_wav_feature = QPushButton('특징 값 저장')
        self.insertBtn_wav_feature.setFixedSize(80,20)
        ######################################### Add QSlider

        self.seekSlider1 = QSlider()

        self.seekSlider1.setOrientation(Qt.Horizontal)
        self.seekSlider1.setRange(0, 0)


        ######################################### Add QSlider

        ######################################### Add QBasicTimer

        self.timer = QBasicTimer()

        ######################################### Add QBasicTimer

        ######################################### Add QComboBox


        self.comboBox_aostc_rfng_cln_yn = QtWidgets.QComboBox()
        self.comboBox_aostc_rfng_mthd_gb = QtWidgets.QComboBox()
        self.comboBox_qlty_anls_rslt_code = QtWidgets.QComboBox()
        self.comboBoxSetting()

        self.comboBox_aostc_rfng_mthd_gb.setFixedSize(100,20)
        self.comboBox_aostc_rfng_cln_yn.setFixedSize(100,20)
        self.comboBox_qlty_anls_rslt_code.setFixedSize(130,20)

        ######################################### Add QComboBox

        ######################################### Add textEdit

        self.textbox = QLineEdit(self)
        self.textbox.setFixedSize(80, 20)
        self.date_inquiry_textbox = QLineEdit(self)
        self.date_inquiry_textbox.setFixedSize(100,20)
        self.date_inquiry_textbox.setInputMask('0000-00-00')
        self.date_inquiry_textbox.setPlaceholderText('ex)2021-09-15')

        self.opr_syps_textEdit = QPlainTextEdit(self)
        self.opr_syps_textEdit.setFixedSize(380,50)
        self.remark_textEdit = QPlainTextEdit(self)

        self.remark_textEdit.setFixedSize(550,70)
        ######################################### Add textEdit


        ######################################### Add QTableWidget

        self.tableWidget = QTableWidget(self)
        self.tableWidget.cellClicked.connect(self.cellclicked_event)
        self.tableWidget_detl = QTableWidget(self)
        self.tableWidget_detl.setFixedSize(950, 300)
        self.tableWidget_detl.cellClicked.connect(self.cellclicked_event_download)

        ######################################### Add QTableWidget

        ######################################### Add QLabel

        self.seekSliderLabel1 = QLabel('0')
        self.seekSliderLabel2 = QLabel('0')

        self.state_label = QLabel('진행 상황 : ')
        self.state = QLabel(' ')
        self.inquiryLabel = QLabel('분석 일시')
        self.aostc_rfng_cln_yn_label = QLabel('음향 정련 완료 여부')
        self.aostc_rfng_cln_yn_label.setFixedSize(120,20)
        self.aostc_rfng_cln_yn_label.setAlignment(Qt.AlignCenter)
        self.aostc_rfng_mthd_gb_label = QLabel('음향 정련 방법 구분')
        self.aostc_rfng_mthd_gb_label.setFixedSize(120,20)
        self.aostc_rfng_mthd_gb_label.setAlignment(Qt.AlignCenter)
        self.qlty_anls_rslt_code_label = QLabel('품질 분석 결과')
        self.qlty_anls_rslt_code_label.setFixedSize(120, 20)
        self.qlty_anls_rslt_code_label.setAlignment(Qt.AlignCenter)
        self.remark_label = QLabel('비고')
        self.remark_label.setAlignment(Qt.AlignCenter)

        ######################################### Add QLabel

        ######################################### Add Layout

        self.controlArea = QVBoxLayout()
        self.titleLayout = QHBoxLayout()
        self.controlsGridLayout = QGridLayout()
        self.tableLayout = QVBoxLayout()
        self.data_detlLayout = QGridLayout()
        self.canvas_inquiry_table = QHBoxLayout()
        self.canvas_data_detllayout = QVBoxLayout()
        self.inquiryLayout = QHBoxLayout()
        self.inquiryLayout.addStretch(10)
        self.qhlayout = QHBoxLayout()
        self.qvlayout = QVBoxLayout()
        self.controlsGridLayout2 = QGridLayout()
        ######################################### Add Layout

        ######################################### Matplotlib Canvas

        self.canvas = FigureCanvas(Figure())
        self.canvas_spec = FigureCanvas(Figure())
        
        ######################################### Matplotlib Canvas



        ######################################### Connect

        self.playBtn.clicked.connect(self.playHandler)
        self.textBtn.clicked.connect(self.startinsert)
        self.insertBtn.clicked.connect(self.insertHandler)
        self.inquiryBtn.clicked.connect(self.date_inquiry)
        self.comboBox_aostc_rfng_cln_yn.activated[str].connect(self.aostc_rfng_cln_yn_activated)
        self.comboBox_aostc_rfng_mthd_gb.activated[str].connect(self.aostc_rfng_mthd_gb_activated)
        self.comboBox_qlty_anls_rslt_code.activated[str].connect(self.qlty_anls_rslt_code_activated)
        self.pure.clicked.connect(self.purewav)
        self.fan.clicked.connect(self.fanwav)
        self.sec4.clicked.connect(self.secfoursplit)
        self.sec3.clicked.connect(self.secthreesplit)
        self.insertBtn_wav_feature.clicked.connect(self.insertWavHandler)
        self.seekSlider1.sliderMoved.connect(self.setPosition)

        ######################################### Connect


        ######################################### AddWidget

        wid = QWidget(self)
        self.setCentralWidget(wid)
        self.titleLayout.addWidget(self.title)

        self.controlsGridLayout.setColumnStretch(5, 1)
        self.controlsGridLayout.setColumnStretch(6, 1)
        self.controlsGridLayout.setColumnStretch(7, 1)
        self.controlsGridLayout.setColumnStretch(8, 1)
        self.controlsGridLayout.setColumnStretch(9, 1)
        self.controlsGridLayout.setColumnStretch(10, 1)
        self.controlsGridLayout.setColumnStretch(11, 1)
        self.controlsGridLayout.setColumnStretch(12, 1)
        self.seekSliderLabel1.setAlignment(Qt.AlignTop)
        self.seekSliderLabel2.setAlignment(Qt.AlignTop)
        self.controlsGridLayout.addWidget(self.seekSliderLabel1, 0, 0)
        self.controlsGridLayout.addWidget(self.seekSliderLabel2, 0, 13)
        self.controlsGridLayout.addWidget(self.playBtn, 1, 0)
        self.controlsGridLayout.addWidget(self.seekSlider1, 1, 1, 1, 12)

        self.controlsGridLayout.addWidget(self.textbox, 2, 0)
        self.controlsGridLayout.addWidget(self.textBtn, 2, 1)
        self.controlsGridLayout.addWidget(self.pure, 2, 2)
        self.controlsGridLayout.addWidget(self.fan, 2, 3)
        self.controlsGridLayout.addWidget(self.sec4, 2, 4)
        self.controlsGridLayout.addWidget(self.sec3, 2, 5)
        self.controlsGridLayout.setColumnStretch(1,1)
        self.controlsGridLayout.setColumnStretch(2,1)
        self.controlsGridLayout.setColumnStretch(3,1)
        self.controlsGridLayout.setColumnStretch(4,1)
        self.controlsGridLayout.setRowStretch(3,1)
        self.controlsGridLayout.setContentsMargins(0, 0, 0, 0)
        self.data_detlLayout.setColumnStretch(0,1)
        self.data_detlLayout.setColumnStretch(1,1)
        self.data_detlLayout.setColumnStretch(2,1)
        self.data_detlLayout.setColumnStretch(3,1)

        self.data_detlLayout.addWidget(self.aostc_rfng_cln_yn_label, 0, 0)
        self.data_detlLayout.addWidget(self.comboBox_aostc_rfng_cln_yn, 0, 1)
        self.data_detlLayout.addWidget(self.aostc_rfng_mthd_gb_label, 0, 2)
        self.data_detlLayout.addWidget(self.comboBox_aostc_rfng_mthd_gb, 0, 3)
        self.data_detlLayout.addWidget(self.qlty_anls_rslt_code_label, 0, 4)
        self.data_detlLayout.addWidget(self.comboBox_qlty_anls_rslt_code, 0, 5)

        self.data_detlLayout.addWidget(self.remark_label, 2, 0)
        self.data_detlLayout.addWidget(self.remark_textEdit, 2, 1, 1, 3)

        self.data_detlLayout.addWidget(self.insertBtn, 2, 4)
        self.data_detlLayout.addWidget(self.insertBtn_wav_feature, 2, 5)

        self.inquiryLayout.addWidget(self.state_label)
        self.inquiryLayout.addWidget(self.state)
        self.inquiryLayout.addStretch(80)
        self.inquiryLayout.addWidget(self.inquiryLabel)
        self.inquiryLayout.addWidget(self.date_inquiry_textbox)
        self.inquiryLayout.addWidget(self.inquiryBtn)
        self.tableLayout.addLayout(self.inquiryLayout)
        self.tableLayout.addWidget(self.tableWidget)
        self.tableLayout.addWidget(self.tableWidget_detl)

        self.canvas_data_detllayout.addWidget(self.canvas)
        self.canvas_data_detllayout.addWidget(self.canvas_spec)
        self.canvas_data_detllayout.addLayout(self.controlsGridLayout)
        self.canvas_data_detllayout.addLayout(self.data_detlLayout)

        self.qhlayout.addLayout(self.data_detlLayout)
        self.qhlayout.addLayout(self.qvlayout)

        self.qvlayout.addLayout(self.controlsGridLayout)
        self.canvas_inquiry_table.addLayout(self.tableLayout)
        self.canvas_inquiry_table.addLayout(self.canvas_data_detllayout)


        self.controlArea.addLayout(self.titleLayout)
        self.controlArea.addLayout(self.canvas_inquiry_table)

        self.Player.stateChanged.connect(self.mediaStateChanged)
        self.Player.positionChanged.connect(self.positionChanged)
        self.Player.durationChanged.connect(self.durationChanged)
        wid.setLayout(self.controlArea)

    ######################################### AddWidget

    ######################################### Home Screen Setting

    ######################################### Event Handler

    # 에러 발생 시
    def handleError(self):
        print(f"Error: {self.Player.errorString()}")

    def dev(self):
        try:
            # 파일 경로 지정
            self.split_path = './splitwav_cus_dev/'
            self.download_path = './download_wav_cus_dev/'
            self.img_path = './splitimg_cus_dev/'

            # 디렉토리 유/무 확인 없을 시 생성
            os.makedirs(self.split_path, exist_ok=True)
            os.makedirs(self.download_path, exist_ok=True)
            os.makedirs(self.img_path, exist_ok=True)

            self.is_dev_file = 1
            self.conn = pymysql.connect(host="DB접속 주소",
                        port=13306, user='사용자',
                        passwd='비밀번호',
                        db='DB',
                        charset='utf8')  # 한글처리 (charset = 'utf8')
            self.url = '음원파일을 다운 받는 주소'
            self.url_api = '음원 편집 후 후처리 API 주소'
            self.success_url = '작업 완료 후 보내는 주소'
            self.setWindowTitle('AuRRA(개발)')
            self.title = QLabel('AuRRA(개발)')
            self.title.setFixedWidth(200)
            self.title.setFont(QFont('D2Coding', 14, QFont.Bold))
            self.initUI()
            return QMessageBox.question(self, 'Message','환경 : 개발', QMessageBox.Yes)
        except:
            print(traceback.format_exc())


    def adm(self):
        message = QMessageBox.question(self, 'Message', "환경을 운영으로 연결하시겠습니까?", QMessageBox.Yes | QMessageBox.No,QMessageBox.No)
        if message == QMessageBox.Yes:
            try:
                # 파일 경로 지정
                self.split_path = './splitwav_cus_adm/'
                self.download_path = './download_wav_cus_adm/'
                self.img_path = './splitimg_cus_adm/'

                # 디렉토리 유/무 확인 없을 시 생성
                os.makedirs(self.split_path, exist_ok=True)
                os.makedirs(self.download_path, exist_ok=True)
                os.makedirs(self.img_path, exist_ok=True)
                
                self.is_dev_file = 0
                self.conn = pymysql.connect(host="DB접속 주소",
                                port=13306, user='사용자',
                                passwd='비밀번호',
                                db='DB',
                                charset='utf8')  # 한글처리 (charset = 'utf8')
                self.url = '음원파일을 다운 받는 주소'
                self.url_api = '음원 편집 후 후처리 API 주소'
                self.success_url = '작업 완료 후 보내는 주소'
                self.setWindowTitle('AuRRA(운영)')
                self.title = QLabel('AuRRA(운영)')
                self.title.setFixedWidth(210)
                self.title.setFont(QFont('D2Coding', 18, QFont.Bold))
                self.title.setStyleSheet("Color : red")
                self.initUI()
                return QMessageBox.question(self, 'Message', '환경 : 운영', QMessageBox.Yes)
            except:
                print(traceback.format_exc())
        else:
            pass
    
    def comboBoxSetting(self):
        # 편집시 수작업/자동화 선택 콤보박스
        cur_rfng_mthd_gb = self.conn.cursor()
        self.conn.ping(reconnect=True)
        sql_rfng_mthd_gb = "SELECT CODE_DETL_NM, CODE_DETL_ID FROM TAA_C_DETL_LIST WHERE COMM_CODE_ID = '314'"
        cur_rfng_mthd_gb.execute(sql_rfng_mthd_gb)
        cur_rfng_mthd_gb.close()
        rows_rfng_mthd_gb = cur_rfng_mthd_gb.fetchall()
        self.conn.close()

        # 편집 후 결과 선택 콤보박스
        cur_qlty_ansl_rslt_code = self.conn.cursor()
        self.conn.ping(reconnect=True)
        sql_qlty_ansl_rslt_code = "SELECT CODE_DETL_NM, CODE_DETL_ID FROM TAA_C_DETL_LIST WHERE COMM_CODE_ID = '316'"
        cur_qlty_ansl_rslt_code.execute(sql_qlty_ansl_rslt_code)
        rows_qlty_ansl_rslt_code = cur_qlty_ansl_rslt_code.fetchall()
        self.conn.close()

        for i in rows_rfng_mthd_gb:
            self.comboBox_aostc_rfng_mthd_gb.addItem(i[0], i[1])
        self.comboBox_aostc_rfng_mthd_gb.setCurrentIndex(1)
        self.aostc_rfng_mthd_gb_co = self.comboBox_aostc_rfng_mthd_gb.itemData(self.comboBox_aostc_rfng_mthd_gb.currentIndex())

        # 작업 완료 여부 
        for k in rows_qlty_ansl_rslt_code:
            self.comboBox_qlty_anls_rslt_code.addItem(k[0], k[1])
        self.comboBox_qlty_anls_rslt_code.setCurrentIndex(0)
        self.qlty_anls_rslt_code = self.comboBox_qlty_anls_rslt_code.itemData(self.comboBox_qlty_anls_rslt_code.currentIndex())
        rfng_cln_yn = (('완료', 'Y'), ('미완료', 'N'))

        for j in rfng_cln_yn:
            self.comboBox_aostc_rfng_cln_yn.addItem(j[0], j[1])
        self.comboBox_aostc_rfng_cln_yn.setCurrentIndex(0)
        self.aostc_rfng_cln_yn_co = self.comboBox_aostc_rfng_cln_yn.itemData(self.comboBox_aostc_rfng_cln_yn.currentIndex())

    # 선택한 기간내 파일 정리 함수
    def oneDay(self):
        try:
            self.day = 1
            self.cleanupDir()

        except:
            print(traceback.format_exc())

    # 선택한 기간내 파일 정리 함수
    def threeDay(self):
        try:
            self.day = 3
            self.cleanupDir()
        except:
            print(traceback.format_exc())

    # 선택한 기간내 파일 정리 함수
    def sevenDay(self):
        try:
            self.day = 7
            self.cleanupDir()
        except:
            print(traceback.format_exc())

    # 선택한 기간내 파일 정리 함수
    def tenDay(self):
        try:
            self.day = 10
            self.cleanupDir()
        except:
            print(traceback.format_exc())

    # 파일 정리 함수
    def cleanupDir(self):
        try:
            car_wav_path = self.download_path
            car_wav_list = os.listdir(car_wav_path)

            car_split_path = self.split_path
            car_split_list = os.listdir(car_split_path)

            car_img_path = self.img_path
            car_img_list = os.listdir(car_img_path)

            now = datetime.datetime.now()
            before = now - datetime.timedelta(days=self.day)

            for fname_wav in car_wav_list:

                ctime_wav = os.path.getctime(car_wav_path + fname_wav)
                file_date_wav = datetime.datetime.fromtimestamp(ctime_wav).strftime('%Y-%m-%d')

                if file_date_wav <= before.strftime('%Y-%m-%d'):
                    os.remove(car_wav_path + fname_wav)
                    self.wav_count += 1
                else:
                    pass

            for fname_split in car_split_list:

                ctime_split = os.path.getctime(car_split_path + fname_split)
                file_date_split = datetime.datetime.fromtimestamp(ctime_split).strftime('%Y-%m-%d')

                if file_date_split <= before.strftime('%Y-%m-%d'):
                    os.remove(car_split_path + fname_split)
                    self.split_count += 1
                else:
                    pass

            for fname_img in car_img_list:

                ctime_img = os.path.getctime(car_img_path + fname_img)
                file_date_img = datetime.datetime.fromtimestamp(ctime_img).strftime('%Y-%m-%d')

                if file_date_img <= before.strftime('%Y-%m-%d'):
                    os.remove(car_img_path + fname_img)
                    self.img_count += 1
                else:
                    pass
            QMessageBox.question(self, 'Message', f'{self.day}일전 파일 삭제\n원본  : {self.wav_count}, 편집 : {self.split_count}, 이미지 : {self.img_count} 삭제 완료' , QMessageBox.Yes)
            self.initUI()
        except AttributeError:
            QMessageBox.question(self, 'Message', '환경을 먼저 선택해주세요.', QMessageBox.Yes)
            pass

        except:
            print(traceback.format_exc())
            pass



    # QFileDialog를 이용해 파일 열기
    def openFile(self):

        try:
            
            # # 리스트 형태의 파일 경로 (ex - ['C:/.../.../.wav'])
            
            self.audio_path = f'{self.download_path}{self.car_num}.wav'

            # 미디어 콘텐츠 구성
            self.Player.setMedia(
                QMediaContent(QUrl.fromLocalFile(self.audio_path)))
            self.playBtn.setEnabled(True)
            # wav 파일 읽기
            (file_dir, file_id) = os.path.split(self.audio_path)
            self.fileid = file_id

            y, sr = sf.read(self.audio_path)
            self.y = y
            self.samplerate = sr
            # 1차원 배열 만들기
            time = np.linspace(0, len(y) / sr, len(y))

            # wav 파일 시각화
            self.ax = self.canvas.figure.subplots()
            self.ax.plot(time, y, color='b', label='speech waveform')
            self.ax.set_ylabel("Amplitude")
            self.ax.set_xlabel("Time [s]")
            self.ax.set_title(file_id)

            self.ax2 = self.ax.twinx()
            self.ax2.axvline(x=0, color='red')
            self.canvas.draw()

            pass
        except IndexError:
            pass

        except RuntimeError:
            print (traceback.format_exc())
            return QMessageBox.question(self, 'Message', '파일을 다시 확인해주세요.', QMessageBox.Yes)
            pass


        pass

    # DB 데이터를 조회하는 함수
    def Inquiry(self):
        try:
            self.initUI()
            self.setTableWidgetData()
            self.state.setText('조회')

        except:
            print (traceback.format_exc())
            pass

    # 사용자 관리 고유 번호로 조회할 경우
    def date_inquiry(self):
        try:
            if self.date_inquiry_textbox.text() == '--':
                self.Inquiry()
    
            else:
                cur = self.conn.cursor()
                self.conn.ping(reconnect=True)
                # 작업해야할 음원들을(특정조건에 맞는) 사용자가 설정한 날짜에 맞춰 DB에서 불러오는 쿼리문
                sql = f"SELECT \
                        req.CLNTCO_REQ_MNGT_NO, \
                        req.USR_MNGT_UNQ_NO, \
                        req.ANLS_REQ_SEQ, \
                        cusr.CUST_MNGT_UNQ_NO, \
                        cusr.CUST_NM,\
		                carnum.CAR_REG_NO,\
                        (SELECT code.CODE_DETL_NM FROM TAA_C_DETL_LIST code \
                        WHERE code.COMM_CODE_ID = '113' AND code.CODE_DETL_ID = cusr.PSNL_CRP_GB) AS PSNL_CRP_NM, \
                        req.ANLS_DTTM,\
                        req.CUST_CAR_INFO_LST_YN\
                    FROM TBD_L_CUST_REQ_ATP_DTA req  \
                    LEFT OUTER JOIN ( \
                        SELECT \
                          usr.USR_MNGT_UNQ_NO, \
                          usr.USR_NM, \
                          usr.CUST_MNGT_UNQ_NO, \
                          cust.CUST_NM, \
                          cust.PSNL_CRP_GB \
                    FROM TAA_M_USER_INFO usr \
                    INNER JOIN TBA_M_CUST_INFO cust ON usr.CUST_MNGT_UNQ_NO = cust.CUST_MNGT_UNQ_NO \
                    ) cusr \
                    ON req.USR_MNGT_UNQ_NO = cusr.USR_MNGT_UNQ_NO\
                    LEFT OUTER JOIN TAB_L_CAR_PRDT_LIST carnum \
                    ON carnum.CAR_PRDT_MNGT_NO = req.CAR_PRDT_MNGT_NO \
                    WHERE DATE_FORMAT(req.ANLS_DTTM, '%Y-%m-%d') = DATE_FORMAT('{self.date_inquiry_textbox.text()}', '%Y-%m-%d')\
                    ORDER BY req.ANLS_DTTM DESC"
                cur.execute(sql)
                self.gb_rows = cur.fetchall()
                self.Inquiry()
                self.gb_setTableWidgetData()
                self.conn.close()
                self.state.setText('조회')

                return self.gb_rows

        except pymysql.err.Error:
            pass

        except:
            print(traceback.format_exc())



    # 첫번째 테이블 쿼리문 - 차량데이터 수집내역
    def selectTableList(self):
        try:
            cur = self.conn.cursor()
            self.conn.ping(reconnect=True)
            # 작업해야할 음원들을(특정조건에 맞는) DB에서 불러오는 쿼리문
            sql = f"SELECT \
                        req.CLNTCO_REQ_MNGT_NO, \
                        req.USR_MNGT_UNQ_NO, \
                        req.ANLS_REQ_SEQ, \
                            CASE \
                                WHEN qlty.AOSTC_RAW_FILE_GID IS NOT NULL AND qlty.AOSTC_RFNG_FILE_GID IS NOT NULL \
                                THEN '정련 완료' \
                                WHEN qlty.AOSTC_RAW_FILE_GID IS NOT NULL AND qlty.AOSTC_RFNG_FILE_GID IS NULL AND req.QLTY_ANLS_RSLT_CODE IS NULL\
                                THEN '정련 미완료' \
                                WHEN qlty.AOSTC_RAW_FILE_GID IS NULL AND req.QLTY_ANLS_RSLT_CODE IS NULL\
                                THEN '원본 없음' \
                                WHEN req.QLTY_ANLS_RSLT_CODE != '00'\
                                THEN '정련 불가' \
                            END AS AOSTC_RFNG_PRCS_GB, \
                        cusr.CUST_NM,\
		                carnum.CAR_REG_NO,\
                        (SELECT splc.SPLC_NM FROM TAC_M_SPLC_INFO splc\
                            WHERE splc.SPLC_MNGT_UNQ_NO = cusr.SPLC_MNGT_UNQ_NO) AS SPLC_NM,\
                        req.ANLS_DTTM,\
                        req.CUST_CAR_INFO_LST_YN\
                    FROM TBD_L_CUST_REQ_ATP_DTA req  \
                    INNER JOIN TBD_L_CUST_REQ_ATP_DTA_QLTY qlty ON req.USR_MNGT_UNQ_NO = qlty.USR_MNGT_UNQ_NO \
                    AND req.ANLS_REQ_SEQ = qlty.ANLS_REQ_SEQ \
                    LEFT OUTER JOIN ( \
                        SELECT \
                          usr.USR_MNGT_UNQ_NO, \
                          usr.USR_NM, \
                          usr.CUST_MNGT_UNQ_NO, \
                          cust.CUST_NM, \
                          cust.PSNL_CRP_GB, \
                          cust.SPLC_MNGT_UNQ_NO \
                    FROM TAA_M_USER_INFO usr \
                    INNER JOIN TBA_M_CUST_INFO cust ON usr.CUST_MNGT_UNQ_NO = cust.CUST_MNGT_UNQ_NO \
                    ) cusr \
                    ON req.USR_MNGT_UNQ_NO = cusr.USR_MNGT_UNQ_NO \
                    LEFT OUTER JOIN TAB_L_CAR_PRDT_LIST carnum \
                    ON carnum.CAR_PRDT_MNGT_NO = req.CAR_PRDT_MNGT_NO\
                    WHERE qlty.AOSTC_RAW_FILE_GID IS NOT NULL AND qlty.AOSTC_RFNG_FILE_GID IS NULL AND req.QLTY_ANLS_RSLT_CODE IS NULL \
                    ORDER BY req.ANLS_DTTM DESC"
        
            cur.execute(sql)
            self.rows = cur.fetchall()

            self.conn.close()
            return self.rows
        except IndexError:
            print(traceback.format_exc())


    # 두번째 테이블 쿼리문 - 차량데이터 수집 세부내역
    def selectTableList_detl(self):
        try:
            cur_detl = self.conn.cursor()
            self.conn.ping(reconnect=True)
            sql_detl = f"SELECT USR_MNGT_UNQ_NO,\
                            ANLS_REQ_SEQ,\
                            AOSTC_RAW_FILE_GID,\
                            AOSTC_RFNG_FILE_GID\
                        FROM TBD_L_CUST_REQ_ATP_DTA_QLTY WHERE USR_MNGT_UNQ_NO = '{self.usr_mngt_unq_no}' AND ANLS_REQ_SEQ = '{self.anls_req_seq}'"

            cur_detl.execute(sql_detl)
            self.rows_detl = cur_detl.fetchall()
            self.conn.close()
            return self.rows_detl
        except:
            print(traceback.format_exc())
            return None

    # 첫번째 테이블 구성(특정 시간으로 조회 시) - 작업해야될 데이터를 특정 시간으로 조회 후 출력
    def gb_setTableWidgetData(self):
        try:

            self.tableWidget.setRowCount(len(self.gb_rows))
            self.tableWidget.setColumnCount(len(self.gb_rows[0]))

            column_headers = ['고객사 요청 관리 번호','사용자 관리 고유 번호', '분석 요청 일련 번호', '고객 관리 고유 번호', '고객 명', '차량 번호', '공급사 명', '분석 일시', '고객 차량 정보 최종 여부']
            self.tableWidget.setHorizontalHeaderLabels(column_headers)

            for i in range(len(self.gb_rows)):
                for j in range(len(self.gb_rows[0])):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(self.gb_rows[i][j])))
                    self.tableWidget.item(i,j).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

                    if j == 3:
                        self.tableWidget.setColumnWidth(j, int(self.width() * 0.5 / 10))
                    else:
                        self.tableWidget.setColumnWidth(j, int(self.width() * 0.7 / 10))
        except IndexError:
            QMessageBox.question(self, 'Message', '데이터가 없습니다.', QMessageBox.Yes)
            pass
        except:
            print(traceback.format_exc())
            pass
    # 첫번째 테이블 구성 - 작업해야될 데이터를 출력
    def setTableWidgetData(self):
        try:
                self.rows = self.selectTableList()
                self.tableWidget.setRowCount(len(self.rows))
                self.tableWidget.setColumnCount(len(self.rows[0]))
                header = self.tableWidget.horizontalHeader()

                column_headers = ['고객사 요청 관리 번호','사용자 관리 번호', '분석 요청 일련 번호', '정련 상태', '고객 명', '차량 번호','공급사 명', '분석 일시', '차량 정보 최종 여부']
                self.tableWidget.setHorizontalHeaderLabels(column_headers)


                for i in range(len(self.rows)):
                    for j in range(len(self.rows[0])):
                        self.tableWidget.setItem(i, j, QTableWidgetItem(str(self.rows[i][j])))
                        self.tableWidget.item(i, j).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        header.setSectionResizeMode(j, QHeaderView.ResizeToContents)
                        
        except IndexError:
            return QMessageBox.question(self, 'Message', '데이터가 없습니다', QMessageBox.Yes)

        except:
            print (traceback.format_exc())

            pass

    # 두번째 테이블 구성 - 음원 데이터의 고유 ID 값을 출력

    def setTableWidgetData_detl(self):
        try:
            self.rows_detl = self.selectTableList_detl()
            self.tableWidget_detl.setRowCount(len(self.rows_detl))
            self.tableWidget_detl.setColumnCount(len(self.rows_detl[0]))

            column_headers = ['사용자 관리 고유 번호', '분석 요청 일련 번호', 'RAW 파일 GID', '정련 파일 GID']
            self.tableWidget_detl.setHorizontalHeaderLabels(column_headers)

            for i in range(len(self.rows_detl)):
                for j in range(len(self.rows_detl[0])):
                    self.tableWidget_detl.setItem(i, j, QTableWidgetItem(str(self.rows_detl[i][j])))
                    self.tableWidget_detl.item(i, j).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.tableWidget_detl.setColumnWidth(j, int(self.width() * 1/10))
        except:
            print(traceback.format_exc())
            return QMessageBox.question(self, 'Message', '음향 데이터가 없습니다 !', QMessageBox.Yes)
            pass

    # 시작점
    def startinsert(self):

        self.start = self.textbox.text()

        return QMessageBox.question(self, 'Message', f'시작점 : {self.start}초', QMessageBox.Yes)
    
    # 4초 편집
    def secfoursplit(self):

        self.ny =  self.y[int(self.start) * self.samplerate : (int(self.start) + 4) * self.samplerate]

        QMessageBox.question(self, 'Message', '4초 편집', QMessageBox.Yes)

        self.splitHandler()

    # 3초 편집
    def secthreesplit(self):

        self.ny = self.y[int(self.start) * self.samplerate : (int(self.start) + 3) * self.samplerate]

        QMessageBox.question(self, 'Message', '3초 편집', QMessageBox.Yes)

        self.splitHandler()

    # pure wav
    def purewav(self):

        self.rda_fan = 'P'

        return QMessageBox.question(self, 'Message', 'Pure wav', QMessageBox.Yes)
    
    # Include Fan wav
    def fanwav(self):

        self.rda_fan = 'F'

        return QMessageBox.question(self, 'Message', 'Include Fan wav', QMessageBox.Yes)

    def aostc_rfng_cln_yn_activated(self, text):

        self.aostc_rfng_cln_yn_co = self.comboBox_aostc_rfng_cln_yn.itemData(self.comboBox_aostc_rfng_cln_yn.currentIndex())


    def aostc_rfng_mthd_gb_activated(self, text):

        self.aostc_rfng_mthd_gb_co = self.comboBox_aostc_rfng_mthd_gb.itemData(self.comboBox_aostc_rfng_mthd_gb.currentIndex())

    def qlty_anls_rslt_code_activated(self, text):

        self.qlty_anls_rslt_code = self.comboBox_qlty_anls_rslt_code.itemData(self.comboBox_qlty_anls_rslt_code.currentIndex())

    
    # wav_api에 요청을 보내 편집된 음원의 이미지 추출
    def specimage(self):
        try:

            self.params['gid'] = self.wav_gid
            self.params['is_dev_file'] = self.is_dev_file
            self.params['file_key'] = 'CUST_WAV_SPECTRO_PNG'
            
            res = requests.post(f'{self.url_api}/extract_spectro_png/log', json=self.params).json()
            time.sleep(1)
            
            get_data = requests.get(f'{self.req_url}/getData/{res["task_id"]}').json()
            
            self.image_gid = get_data['gid']
            
            self.state.setText('조회 > 음원 다운 > 편집 > 세부내역 업데이트 > 이미지 추출')
            QMessageBox.question(self, 'Message', f'이미지 추출 : {self.car_num} !', QMessageBox.Yes)

            self.specplainimage()

        except:
            print(traceback.format_exc())
            pass

    def specplainimage(self):
        try:
            
            self.params['file_key'] = 'CUST_WAV_SPECTRO_PNG'
            
            res = requests.post(f'{self.url_api}/extract_spectro_png/plain', json=self.params).json()
            time.sleep(1)

            get_data = requests.get(f'{self.req_url}/getData/{res["task_id"]}').json()

            self.image_plain_gid = get_data['gid']
            
            self.state.setText('조회 > 음원 다운 > 편집 > 세부내역 업데이트 > 이미지 추출')
            QMessageBox.question(self, 'Message', f'이미지 추출 plain : {self.car_num} !', QMessageBox.Yes)

            self.specvideo()

        except:
            print(traceback.format_exc())
            pass

    def specvideo(self):
        try:
            
            self.params['file_key'] = 'CUST_WAV_SPECTRO_MP4'
            
            res = requests.post(f'{self.url_api}/make_mp4', json=self.params).json()
            time.sleep(1)
            
            get_data = requests.get(f'{self.req_url}/getData/{res["task_id"]}').json()

            self.strmvdo_gid = get_data['gid']
            
            self.state.setText('조회 > 음원 다운 > 편집 > 세부내역 업데이트 > 이미지 추출 > 비디오 추출')
            QMessageBox.question(self, 'Message', f'video 추출 : {self.car_num} !', QMessageBox.Yes)

            self.insertWavHandler()

        except:
            print(traceback.format_exc())
            pass

    # 첫번째 테이블에서 차량 번호 클릭시 차량번호, 데이터 수신일자, 수신 일련번호가 변수롤 저장
    def cellclicked_event(self, row, col):
        try:
           
            self.usr_mngt_unq_no = self.tableWidget.item(row, 1).text()
            self.anls_req_seq = self.tableWidget.item(row, 2).text()
            self.client_name = self.tableWidget.item(row, 4).text()
            self.car_num = self.tableWidget.item(row,5).text()
            self.cust_car_info_lst_yn = self.tableWidget.item(row, 8).text()
            # 데이터 불러오기
            self.setTableWidgetData_detl()
        except:
            print(traceback.format_exc())
            return QMessageBox.question(self, 'Message', 'DB 연결 확인해주세요 ! ', QMessageBox.Yes)
            pass

    # 두번째 테이블에서 파일 gid 클릭 시 파일 gid, 데이터 일련번호, 변경 일련번호가 변수에 저장
    def cellclicked_event_download(self, row1, col1):
        message = QMessageBox.question(self, 'Message', '다운로드 하시겠습니까?', QMessageBox.Yes | QMessageBox.No,QMessageBox.No)
        if message == QMessageBox.Yes:
            try:
            
                self.raw_gid = self.tableWidget_detl.item(row1, 2).text()

                url = f'{self.url}/fileManager/download?fileId=%s' % (self.raw_gid)

                self.download(url, self.download_path + self.car_num + '.wav')
                self.openFile()
                self.state.setText('조회 > 음원 다운')
            except:
                print(traceback.format_exc())
                pass
        else:
            pass
    # 파일 다운로드
    def download(self, url, file_name):
        try:
            with open(file_name, "wb") as file:
                response = get(url)
                file.write(response.content)
            return QMessageBox.question(self, 'Message', f'다운로드 한 파일 : {self.car_num} !', QMessageBox.Yes)
        except:
            print(traceback.format_exc())
            pass

    # 재생
    def playHandler(self):
        try:
            if self.Player.state() == QMediaPlayer.PlayingState:
                self.playBtn.setText("Play")
                self.Player.pause()
            else:
                self.playBtn.setText("Pause")
                self.Player.play()
                
        except:
            print(traceback.format_exc())
            pass

    # 편집
    def splitHandler(self):
        try:
            now = datetime.datetime.now()
            self.datetime = now.strftime('%Y_%m_%d_%H_%M')
            sf.write(self.split_path + self.datetime + '_' + self.rda_fan + '_' + 'split_' + self.fileid.split('.')[0] + '.wav', self.ny, self.samplerate)
            QMessageBox.question(self, 'Message', 'Split Success!', QMessageBox.Yes)
            # 보내고자하는 파일을 'rb'(바이너리 리드)방식 열고
            self.split_wav_path = self.split_path + self.datetime + '_' + self.rda_fan + '_' + 'split_' + self.fileid.split('.')[0] + '.wav'
            (file_dir, file_id) = os.path.split(self.split_wav_path)
            time = np.linspace(0, len(self.ny) / self.samplerate, len(self.ny))

            self.Player.setMedia(
                QMediaContent(QUrl.fromLocalFile(self.split_wav_path)))

            self.ax.cla()
            self.ax2.cla()
            self.ax.plot(time, self.ny, color='b', label='speech waveform')
            self.ax.set_ylabel("Amplitude")
            self.ax.set_xlabel("Time [s]")
            self.ax.set_title(file_id)
            self.ax2.axvline(x=0, color='red')
            self.canvas.draw()
            pass

            wav_file = open(self.split_wav_path, 'rb')
            # 파이썬 딕셔너리 형식으로 file 설정
            upload_fild = {'file': wav_file}
            # String 포맷
            key_data = {'key': 'CUST_REQ_ATP_DTA'}

            self.file_size = os.path.getsize(self.split_path + self.datetime + '_' + self.rda_fan + '_' + 'split_' + self.fileid.split('.')[0] + '.wav')

            # request.post방식으로 파일전송.
            self.res = requests.post(f'{self.url}/fileManager/upload', files=upload_fild, data=key_data)
            self.res_json = self.res.json()

            self.wav_gid = self.res_json['fileGid']

            self.textBtn.setEnabled(False)
            self.sec4.setEnabled(False)
            self.sec3.setEnabled(False)
            self.pure.setEnabled(False)
            self.fan.setEnabled(False)
            self.state.setText('조회 > 음원 다운 > 편집')
            self.insertHandler()
        except:
            print(traceback.format_exc())
            pass

    # insert 버튼 클릭 시 차량 수집 세부내역 테이블에 insert
    def insertHandler(self):
        try:
            self.remark = self.remark_textEdit.toPlainText()
            cur = self.conn.cursor()
            self.conn.ping(reconnect=True)
            if self.qlty_anls_rslt_code != '00':
                sql = f"UPDATE TBD_L_CUST_REQ_ATP_DTA SET\
                                            AOSTC_RFNG_CLN_YN = '{self.aostc_rfng_cln_yn_co}',\
                                            QLTY_ANLS_RSLT_CODE = '{self.qlty_anls_rslt_code}',\
                                            REMARK = '{self.remark}',\
                                            LST_USR_MNGT_UNQ_NO = '{self.lst_usr_unq_no}',\
                                            LST_CHNG_DTTM = NOW() \
                                        WHERE USR_MNGT_UNQ_NO = '{self.usr_mngt_unq_no}' AND ANLS_REQ_SEQ = '{self.anls_req_seq}'"

                cur.execute(sql)
                self.conn.commit()
                self.conn.close()
                print(self.qlty_anls_rslt_code)
                QMessageBox.question(self, 'Message', f'편집 불가 : {self.car_num}.', QMessageBox.Yes)
                self.Inquiry()

            else:
                self.remark = f'시작점 : {self.start}초 \n끝점 : {int(self.start) + 4}초'
                sql = f"UPDATE TBD_L_CUST_REQ_ATP_DTA SET\
                            ANLS_DTTM = NOW(),\
                            AOSTC_RFNG_CLN_YN = '{self.aostc_rfng_cln_yn_co}',\
                            AOSTC_RFNG_CLN_DTTM = NOW(),\
                            AOSTC_RFNG_MTHD_GB = '{self.aostc_rfng_mthd_gb_co}',\
                            RFNG_PRCS_USR_MNGT_UNQ_NO = '{self.lst_usr_unq_no}',\
                            QLTY_ANLS_RSLT_CODE = '{self.qlty_anls_rslt_code}',\
                            REMARK = '{self.remark}',\
                            LST_USR_MNGT_UNQ_NO = '{self.lst_usr_unq_no}',\
                            LST_CHNG_DTTM = NOW() \
                        WHERE USR_MNGT_UNQ_NO = '{self.usr_mngt_unq_no}' AND ANLS_REQ_SEQ = '{self.anls_req_seq}'"
                cur.execute(sql)
                self.conn.commit()
                self.conn.close()
                self.state.setText('조회 > 음원 다운 > 편집 > 세부내역 업데이트')
                self.insertBtn.setEnabled(False)
                self.comboBox_aostc_rfng_cln_yn.setEnabled(False)
                self.comboBox_aostc_rfng_mthd_gb.setEnabled(False)
                self.comboBox_qlty_anls_rslt_code.setEnabled(False)
                
                QMessageBox.question(self, 'Message', f'데이터 내역 업데이트 완료 : {self.car_num}.', QMessageBox.Yes)
        except pymysql.err.OperationalError:
            QMessageBox.question(self, 'Message', 'DB 연결이 끊어졌습니다. DB 연결을 다시해주세요.', QMessageBox.Yes)
            print(traceback.format_exc())
            pass
        except pymysql.err.DataError:
            QMessageBox.question(self, 'Message', '데이터 세부정보 저장 실패 : 데이터 구분, 데이터 세부 구분, 보정 상태 코드를 선택해주세요.',
                                 QMessageBox.Yes)

        except pymysql.err.InterfaceError:
            QMessageBox.question(self, 'Message', 'DB 연결이 끊어졌습니다. DB 연결을 다시해주세요.', QMessageBox.Yes)
            pass
        except:
            print(traceback.format_exc())

    # Wav feature insert 버튼 클릭 시 고객 요청 비정형 데이터 품질 내역 테이블로 insert
    def insertWavHandler(self):
        try:
            cur = self.conn.cursor()
            self.conn.ping(reconnect=True)
            sql = f"UPDATE TBD_L_CUST_REQ_ATP_DTA_QLTY SET\
                        AOSTC_RFNG_FILE_GID = '{self.wav_gid}',\
                        VSLZ_FILE_GID = '{self.image_gid}',\
                        VSLZ_PLAIN_FILE_GID = '{self.image_plain_gid}', \
                        VSLZ_STRMVDO_FILE_GID = '{self.strmvdo_gid}', \
                        LST_USR_MNGT_UNQ_NO = '{self.lst_usr_unq_no}',\
                        LST_CHNG_DTTM = NOW() \
                    WHERE USR_MNGT_UNQ_NO = '{self.usr_mngt_unq_no}' AND ANLS_REQ_SEQ = '{self.anls_req_seq}'"
            cur.execute(sql)
            self.conn.commit()
            self.conn.close()
            self.insertBtn_wav_feature.setEnabled(False)
            QMessageBox.question(self, 'Message', f'음원 특징 값 저장 완료 : {self.car_num} !', QMessageBox.Yes)

            try:
                # 작업 완료 후 완료 메세지를 보내는 API
                if self.cust_car_info_lst_yn == 'Y':
                    headers = {'SVCKEY': 'OCMOBILE','Content-Type': 'application/json'}
                    data = {'usr_mngt_unq_no': f'{self.usr_mngt_unq_no}', 'anls_req_seq': f'{self.anls_req_seq}'}
                    res = requests.post(self.success_url, headers=headers, data=json.dumps(data))
                    res_json = res.json()
                    
                    time.sleep(1)
                    QMessageBox.question(self, 'Message', f'코드 : {res_json['result_code']}\n메세지 : {res_json['result_msg']}', QMessageBox.Yes)
                    self.Inquiry()
                else:
                    QMessageBox.question(self, 'Message', f'고객 차량 정보 최종 여부 : {self.cust_car_info_lst_yn}', QMessageBox.Yes)
                    self.Inquiry()
            except:
                print(traceback.format_exc())
                pass
        except:
            print(traceback.format_exc())
            pass

    # 미디어 현재 상태 (play. pause)
    def mediaStateChanged(self, state):
        try:
            if self.Player.state() == QMediaPlayer.PlayingState:
                self.playBtn.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
            else:
                self.playBtn.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))
        except:
            print(traceback.format_exc())
            pass

    # 음원과 슬라이더 연결
    def positionChanged(self, position):
        try:
            self.seekSlider1.setValue(position // 1000)
            self.seekSliderLabel1.setText(str(position // 1000))
            self.ax2.cla()
            self.ax2.axvline(x=position // 1000, color='red')
            self.canvas.draw()

        except AttributeError:
            pass

        except:
            print(traceback.format_exc())
            pass

    def durationChanged(self, duration):
        try:
            self.seekSlider1.setRange(0, duration // 1000)
            self.seekSliderLabel2.setText(str(duration // 1000))
    
        except:
            print(traceback.format_exc())
            pass

    def setPosition(self, position):
        try:
            self.Player.setPosition(position // 1000)
            self.seekSliderLabel1.setText(str(position))
            self.position1 = position
        except:
            print(traceback.format_exc())
            pass

    ######################################### Event Handler

    pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_player = MainWindow()
    my_player.resize(1800, 1000)
    my_player.show()
    sys.exit(app.exec_())
