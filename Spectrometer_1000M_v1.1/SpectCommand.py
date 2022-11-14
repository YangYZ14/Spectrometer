# yyz
# 2022.11.12
# Spectrometer Pyvisa Command

import pyvisa
import time
import re

class Horiba_Command():
    # 初始化并连接串口
    def __init__(self,adress='ASRL5::INSTR'):
        self.rm = pyvisa.ResourceManager()
        self.Horiba = self.rm.open_resource('ASRL5::INSTR',baud_rate = 19200, data_bits = 8, write_termination= '\r', read_termination = '\r')
        print("版本信息："+self.Horiba.query('*IDN?'))

    # 初始化并输出当前位置
    def set_zero(self,wavelength):
        self.Horiba.write('G0,'+str(wavelength*4000)+'\n')
        m=self.Horiba.query_ascii_values('H0\n',converter='s')
        i = [x.isdigit() for x in m[0]].index(True)
        n=float(m[0][i:])/4000
        print("成功初始化到位置："+str(n)+"nm")
        return n

    # 查询当前位置
    def query_location(self):
        m = self.Horiba.query_ascii_values('H0\n',converter='s')
        i = [x.isdigit() for x in m[0]].index(True)
        n = float(m[0][i:])/4000
        # print("当前位置为："+str(n)+"nm")
        return n

    # 设置步进长度并步进
    def set_move(self,wavelength):
        self.Horiba.query_ascii_values('H0\n',converter='s')
        m = self.Horiba.query_ascii_values('H0\n', converter='s')
        i = [x.isdigit() for x in m[0]].index(True)
        n = temp = float(m[0][i:])
        self.Horiba.write('F0,' + str(wavelength * 4000) + '\n')
        while abs(n-temp-wavelength*4000)>10:
            m = self.Horiba.query_ascii_values('H0\n',converter='s')
            i = [x.isdigit() for x in m[0]].index(True)
            n = float(m[0][i:])
        # print("步进到："+str(n)+"nm")
        return n/4000

    # 运行过程中停止运行
    def set_stop(self):
        self.Horiba.write('L')
        print("运行停止")

    # 移动到绝对位置
    def set_Abs_Loc(self,wavelength):
        m = self.Horiba.query_ascii_values('H0\n', converter='s')
        i = [x.isdigit() for x in m[0]].index(True)
        n = float(m[0][i:])
        self.Horiba.write('F0,'+str(wavelength*4000-n)+'\n')
        while abs(n-wavelength*4000)>10:
            m = self.Horiba.query_ascii_values('H0\n',converter='s')
            i = [x.isdigit() for x in m[0]].index(True)
            n = float(m[0][i:])
        print("已移动到："+str(n/4000)+"nm")
        return n/4000
