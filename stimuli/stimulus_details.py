"""
pandastim/stimuli/stimulus_details.py

defines strict parameters for stimuli to follow according to defined type -- fake static typed

Part of pandastim package: https://github.com/mattdloring/pandastim
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class StimulusDetails:
    """Contains details about a given stimulus"""

    stim_name: str


@dataclass(frozen=True)
class MonocularStimulusDetails(StimulusDetails):
    """
    Contains details about a given whole-field stimulus
    General implementation assumes duration is full time, stationary time is therefore a subset of that time
    ex: 2 s statonary and 10 s duration runs a total of 10 seconds
    """

    # required
    angle: int = 0
    velocity: float = 0.0

    # defaults
    stationary_time: int = 0
    duration: int = -1  # defaults to going forever

    # default texture is a grating, because why not
    texture: textures.TextureBase = textures.GratingGrayTex()
    stim_name: str = f"wholefield-stimulus_{velocity}_{angle}"

    # default master for monocular stimuli -- can be passed in local usages
    master = {
        stim_name: str,
        angle: int,
        velocity: float,
        stationary_time: int,
        duration: int,
        texture: textures.TextureBase,
    }

    def __post_init__(self):
        """Because python isn't static lets force things here"""
        if self.master:
            for k, v in master_types.items():
                assert k in self.__dict__.keys(), f"must provide {k}"
                assert isinstance(getattr(self, k), v), f"{k} must be type: {v}"

    def return_dict(self):
        tex_dict = utils.unpack_tex(self.texture)
        stim_dict = vars(self).copy()
        stim_dict.pop("texture_size")
        stim_dict.pop("texture")
        return {"stimulus": stim_dict, "texture": tex_dict}


@dataclass(frozen=True)
class BinocularStimulusDetails(StimulusDetails):
    """
    Contains details about a given stimulus where each side is controlled independently
    This default implementation assumes the two textures are equal in size -- will likley run with nonequal sizes
    but may look wonk
    """

    # required
    angle: tuple = (0, 0)
    velocity: tuple = (0.0, 0.0)

    # defaults
    stationary_time: tuple = (0, 0)
    duration: tuple = (-1, -1)  # defaults to going forever
    strip_width: int = 8
    position: tuple = (0, 0)
    strip_angle: int = 0

    texture: tuple = (
        textures.GratingGrayTex(),
        textures.GratingGrayTex(),
    )
    stim_name: str = f"binocular-stimulus_{velocity}_{angle}"

    master = {
        stim_name: str,
        angle: tuple,
        velocity: tuple,
        stationary_time: tuple,
        duration: tuple,
        strip_width: int,
        position: tuple,
        strip_angle: int,
        texture: tuple,
    }

    def __post_init__(self):
        """Because python isn't static lets force things here"""
        if self.master:
            for k, v in master_types.items():
                assert k in self.__dict__.keys(), f"must provide {k}"
                assert isinstance(getattr(self, k), v), f"{k} must be type: {v}"

    def return_dict(self):
        tex0_dict = utils.unpack_tex(self.texture[0])
        tex1_dict = utils.unpack_tex(self.texture[1])

        stim_dict = vars(self).copy()
        stim_dict.pop("texture_size")
        stim_dict.pop("texture")
        return {"stimulus": stim_dict, "texture": [tex0_dict, tex1_dict]}
