from PyQt5 import QtWidgets, uic
from PyQt5.Qt import QApplication

from pandastim import textures, stimuli, utils

import qdarkstyle
import zmq
import numpy as np
import multiprocessing as mp


class PandasController(QtWidgets.QMainWindow):
    def __init__(self):
        super(PandasController, self).__init__()
        uic.loadUi('gui_layout.ui', self)
        self.show()
        self.updateButton.clicked.connect(self.update_stimuli)

        self.pandas_port = utils.port_provider()

        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.bind('tcp://*:' + str(self.pandas_port))
        self.stimulus_topic = 'stim'

        self.max_frequency = 250

        self.pandas = mp.Process(target=self.spawn_pandas, args=(self.pandas_port, self.max_frequency,))
        self.pandas.start()

        self.wf_freq.setMaximum(self.max_frequency)

    def update_stimuli(self):
        curr_tab = self.tabs.currentIndex()
        if curr_tab == 0:
            stim = {'stim_type': 's', 'angle': self.wf_angle.value(), 'velocity': self.wf_vel.value(),
                    'stationary_time': self.wf_stat.value(), 'stim_time': self.wf_stim_time.value(), 'freq': self.wf_freq.value()}
            self._socket.send_string(self.stimulus_topic, zmq.SNDMORE)
            self._socket.send_pyobj(stim)

    def closeEvent(self, event):
        self.pandas.terminate()

    @staticmethod
    def spawn_pandas(port=5005, freq_max=101):
        tex_size = (1024, 1024)
        freqs = np.arange(freq_max)

        input_textures = {'freq': {}, 'blank': textures.BlankTexXY(texture_size=tex_size)}
        for f in freqs:
            input_textures['freq'][f] = textures.GratingGrayTexXY(texture_size=tex_size, spatial_frequency=f)

        stimulation = stimuli.ClosedLoopStimChoice(textures=input_textures, gui=True)

        sub = utils.Subscriber(topic="stim", port=port)
        monitor = utils.MonitorDataPass(sub)
        stimulation.run()

if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    wind = PandasController()
    wind.show()
    app.exec()