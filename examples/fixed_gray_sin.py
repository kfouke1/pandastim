# -*- coding: utf-8 -*-
"""
pandastim/examples/fixed_gray_sin.py

Part of pandastim package: https://github.com/mattdloring/pandastim
"""
from pandastim import textures, stimuli

sin_grey_tex = textures.SinGrayTex(texture_size = 512,
                                   spatial_frequency = 20)
sin_stim = stimuli.TexFixed(sin_grey_tex,
                            angle = -30,
                            profile_on = False,
                            window_name = 'fixed gray sin example')
sin_stim.run()