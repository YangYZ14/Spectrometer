import numpy as np
import pandas as pd
from PySide2.QtWidgets import QApplication
from PySide2.QtUiTools import QUiLoader
from PySide2 import QtCore
import pyqtgraph as pg
import SpectCommand as SC
import Nimax
import threading

pg.setConfigOption('background','w')
pg.setConfigOption('foreground','k')

class Interface:
    def __init__(self):
        self.ui = QUiLoader().load('光谱仪扫描界面.ui')
        self.ui.setWindowTitle('光谱仪扫描')
        # self.ui2 = Interface2()
        self.sc = SC.Horiba_Command()
        self.ni = Nimax.NI(self.ui.doubleSpinBox_4.value()*1000)

        self.plotwin1 = pg.GraphicsLayoutWidget()
        self.ui.horizontalLayout_7.addWidget(self.plotwin1)
        self.p1 = self.plotwin1.addPlot()
        self.p1.showGrid(x=False,y=False)
        self.p1.setLogMode(x=False,y=False)
        self.p1.setLabel('bottom',text='Wavelength',units='nm',color='k')
        self.p1.addLegend()

        self.plotwin2 = pg.GraphicsLayoutWidget()
        self.ui.horizontalLayout_8.addWidget(self.plotwin2)
        self.p2 = self.plotwin2.addPlot()
        self.p2.showGrid(x=False,y=False)
        self.p2.setLogMode(x=False,y=False)
        self.p2.setLabel('bottom',text='Wavelength',units='nm',color='k')
        self.p2.addLegend()

        self.ui.pushButton.clicked.connect(self.start)
        self.ui.pushButton_2.clicked.connect(self.stop)
        self.ui.pushButton_4.clicked.connect(self.set)

    def start(self):
        self.ui.pushButton_4.setEnabled(False)
        self.startWavelength = self.ui.doubleSpinBox.value()
        self.stopWavelength = self.ui.doubleSpinBox_2.value()
        self.stepWavelength = self.ui.doubleSpinBox_3.value()
        self.N = int((self.stopWavelength-self.startWavelength)/self.stepWavelength)
        self.x = np.array(np.array(range(self.N+1))*self.stepWavelength+self.startWavelength)

        self.exposureTime = self.ui.doubleSpinBox_4.value()*1000

        self.ni.setCounterTask(self.exposureTime)
        self.ni.DAQPulseTask.start()

        #圈数
        self.i = 0
        self.running = True
        self.data1 = np.zeros(self.N+1)
        self.data2 = np.zeros(self.N+1)

        self.sc_Thread = threading.Thread(target=self.loop)
        self.sc_Thread.start()

        self.refresh = QtCore.QTimer()
        self.refresh.timeout.connect(self.update)
        self.refresh.start(1000)


    def loop(self):
        while(self.running):
            self.ui.lineEdit_2.setText(str(self.i))
            self.data2 = self.data2 + self.data1
            self.i += 1
            print("圈数：",self.i)
            self.data1 = np.zeros(self.N+1)
            print(self.N)
            if self.i%2:
                #移动到开始位置
                self.ui.lineEdit.setText(str(self.sc.set_Abs_Loc(self.startWavelength)))
                j = 0
                #循环移动读数
                while(j<=self.N):
                    self.ni.DAQCounterTask.start()
                    self.data1[j] = self.ni.Read()
                    print(self.data1[j])
                    self.ui.lineEdit.setText(str(self.sc.set_move(self.stepWavelength)))
                    j += 1
            else:
                self.ui.lineEdit.setText(str(self.sc.set_Abs_Loc(self.stopWavelength)))
                j = 0
                # 循环移动读数
                while (j <= self.N):
                    self.ni.DAQCounterTask.start()
                    self.data1[-j-1] = self.ni.Read()
                    print(self.data1[-j-1])
                    self.ui.lineEdit.setText(str(self.sc.set_move(-self.stepWavelength)))
                    j += 1

    def stop(self):
        self.running = False
        self.sc.set_stop()
        self.ni.DAQPulseTask.stop()
        self.ni.DAQPulseTask.close()
        self.ni.DAQCounterTask.stop()
        self.ni.DAQCounterTask.close()
        self.refresh.stop()
        self.ui.pushButton_4.setEnabled(True)

    def set(self):
        self.ui.lineEdit.setText(str(self.sc.set_Abs_Loc(self.ui.doubleSpinBox_5.value())))
        self.ui.lineEdit.setText(str(self.sc.query_location()))
        self.sc.set_stop()

    #自动保存数据
    def autosave(self):
        c=np.transpose([self.x,self.data2])
        save = pd.DataFrame(c)
        save.to_csv('D:\\Spectrometer\\自动保存数据\\Cavity_test1\\cavity_1' + str(self.i) + 'cycles.csv', index=False,header=False)

    def update(self):
        self.p1.plot(self.x,self.data1,pen='g',clear=True)
        self.p2.plot(self.x,self.data2,pen='g',clear=True)
        self.ui.lineEdit.setText(str(self.sc.query_location()))
        self.autosave()
        # self.ui.lineEdit.setText(str(self.sc.set_move(self.stepWavelength)))


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    stats = Interface()
    stats.ui.show()
    app.exec_()