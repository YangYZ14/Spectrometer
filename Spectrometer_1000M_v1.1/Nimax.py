import nidaqmx
import numpy as np
import time

class NI:
    def __init__(self,pulse_time):
        self.DAQCounterTask = None
        self.DAQPulseTask = None
        self.pulse_time = pulse_time
        self.setCounterTask(self.pulse_time)
        self.TempData = np.zeros(2, dtype=np.uint32)
        self.data = 0

    def setCounterTask(self,pulse_time):
        self.DAQPulseTask = nidaqmx.Task()
        self.DAQPulseTask.co_channels.add_co_pulse_chan_time('Dev1/ctr0',name_to_assign_to_channel='PlsGen',units=nidaqmx.constants.TimeUnits.SECONDS,
            idle_state=nidaqmx.constants.Level.LOW,initial_delay=0,low_time=pulse_time/2*0.001,high_time=pulse_time/2*0.001)
        self.DAQPulseTask.timing.cfg_implicit_timing(sample_mode = nidaqmx.constants.AcquisitionType.CONTINUOUS)
        self.DAQPulseTask.export_signals.ctr_out_event_output_term = '/Dev1/PFI12'

        self.DAQCounterTask = nidaqmx.Task()
        self.DAQCounterTask.ci_channels.add_ci_count_edges_chan(counter='Dev1/ctr2')
        self.DAQCounterTask.timing.cfg_samp_clk_timing(active_edge=nidaqmx.constants.Edge.FALLING,rate=1,
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,samps_per_chan=1000,source='/Dev1/Ctr0InternalOutput')

        # self.DAQCounterTask.triggers.pause_trigger.trig_type = nidaqmx.constants.TriggerType.DIGITAL_LEVEL
        # self.DAQCounterTask.triggers.pause_trigger.dig_lvl_src = '/Dev1/PFI12'
        # self.DAQCounterTask.triggers.pause_trigger.dig_lvl_when = nidaqmx.constants.Level.LOW

    def Read(self, TimeOut=10.0):
        self.TempData = self.DAQCounterTask.read(2,TimeOut)
        self.data = self.TempData[1] - self.TempData[0]
        self.DAQCounterTask.stop()
        return self.data

# NI1 = NI(100)
# NI1.DAQPulseTask.start()
# NI1.DAQCounterTask.start()
# NI1.Read()
# print(NI1.data)
# NI1.DAQCounterTask.stop()
# NI1.DAQPulseTask.stop()
# NI1.DAQPulseTask.close()
# NI1.DAQCounterTask.close()