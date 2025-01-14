# -*- coding: utf-8 -*-
"""
pandastim/examples/input_control_simple.py

Run with publish_random2.py or else it will just show one stimulus forever.

Part of pandastim package: https://github.com/EricThomson/pandastim
"""
from pandastim import textures, stimuli, utils
from utils import port_provider
from examples.publish_random2 import randomPublish2

import multiprocessing as mp
from datetime import datetime as dt


def inputStimControlSimple(port="1234"):
    #Set up thread to monitor the publisher
    sub = utils.Subscriber(topic = "stim", port = port)
    monitor = utils.Monitor(sub)

    # Create list of textures, and parameter list for the two textures
    # Note parameters include a 'stim_type' ('s' for single texture, 'b' for binocular)
    tex1 = textures.SinRgbTex(rgb = (255, 0, 0))
    params1 = {'stim_type': 's', 'angle': 45, 'velocity': 0.1}
    tex2 = textures.GratingGrayTex(spatial_frequency = 20)
    params2 = {'stim_type': 's', 'angle': 80, 'velocity': -0.05}
    stim_texts = [tex1, tex2]
    stim_params = [params1, params2]

    # Set up filepath for saving
    current_dt = dt.now()
    filename = current_dt.strftime(("ics_%Y%m%d_%H%M%S.txt"))
    save_dir = r'./examples'
    file_path = save_dir + filename

    # Run the show!
    frame_rate = 30
    closed_loop = stimuli.InputControlStim(stim_texts,
                                           stim_params,
                                           profile_on = False,
                                           fps = frame_rate,
                                           save_path = file_path)
    closed_loop.run()

    # Stuff that will be run after you close the panda3d window
    monitor.kill()
    if closed_loop.filestream:
        closed_loop.filestream.close()


if __name__ == '__main__':

    port = str(port_provider())

    randomPublisher = mp.Process(target=randomPublish2, args=(port,))
    inputStimControlStimSimple = mp.Process(target=inputStimControlSimple, args=(port,))

    inputStimControlStimSimple.start()
    randomPublisher.start()

    inputStimControlStimSimple.join()
    randomPublisher.join()

    if not inputStimControlStimSimple.is_alive():
        randomPublisher.terminate()
