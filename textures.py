"""
pandastim/textures.py
Texture classes defined for display in ShowBase stimulus classes. 

Part of pandastim package: https://github.com/EricThomson/pandastim

First defines the abstract base class, TextureBase. This defines the attributes
of the textures, but leaves `create_texture` undefined, to be implemented
in each subclass as a numpy array that looks how you want.

Component types (texture data types in panda3d):
https://www.panda3d.org/reference/python/classpanda3d_1_1core_1_1Texture.html#a81f78fc173dedefe5a049c0aa3eed2c0
"""

try:
    import cv2
except:
    print('error importing cv2')

import math

import numpy as np
try:
    import matplotlib.pyplot as plt
except:
    print('error import matplotlib')

from panda3d.core import Texture

from pandastim import utils


class TextureBase:
    """
    Base class for stimuli: subclass this when making specific stimuli.
    You need to implement the create_texture() method, and any parameters
    needed for the texture function.
    """
    def __init__(self, texture_size = 512, texture_name = "stimulus"):
        self.texture_size = texture_size
        self.texture_name = texture_name
        # Create texture
        self.texture_array = self.create_texture()
        self.texture = Texture(self.texture_name)
        # Set texture formatting (greyscale or rgb have different settings)
        if self.texture_array.ndim == 2:
            self.texture.setup2dTexture(self.texture_size, self.texture_size,
                                        Texture.T_unsigned_byte, 
                                        Texture.F_luminance)
            self.texture.setRamImageAs(self.texture_array, "L")
        elif self.texture_array.ndim == 3:
            self.texture.setup2dTexture(self.texture_size, self.texture_size,
                                        Texture.T_unsigned_byte, 
                                        Texture.F_rgb8)
            self.texture.setRamImageAs(self.texture_array, "RGB")

    def create_texture(self):
        """ 
        Create 2d numpy array for stimulus: either nxmx1 (grayscale) or nxm x 3 (rgb)
        """
        pass
    
    def view(self):
        """
        Plot the texture using matplotlib. Useful for debugging.
        """
        plt.imshow(self.texture_array, vmin = 0, vmax = 255)
        if self.texture_array.ndim == 2:
            plt.set_cmap('gray')
            
        plt.title(self.texture_name)
        plt.show()
        
    def __str__(self):
        """
        Return the string you want print(Tex) to show, and to save to file 
        when saving catalog of stimuli.
        """
        pass
    

class RgbTex(TextureBase):
    """
    Full field at given color (e.g., a red card).
    """
    def __init__(self, texture_size = 512,  texture_name = "rgb_field", rgb = (0, 255, 0)):
        self.rgb = rgb
        super().__init__(texture_size = texture_size, texture_name = texture_name)

    def create_texture(self):
        if not (all([x >= 0 for x in self.rgb]) and all([x <= 255 for x in self.rgb])):
            raise ValueError("rgb values must lie in [0,255]")
        x = np.linspace(-self.texture_size/2, self.texture_size/2, self.texture_size)
        y = np.linspace(-self.texture_size/2, self.texture_size/2, self.texture_size)
        X, Y = np.meshgrid(x, y)
        rgb_texture = np.zeros((self.texture_size, self.texture_size, 3), dtype = np.uint8)
        rgb_texture[..., 0] = self.rgb[0]
        rgb_texture[..., 1] = self.rgb[1]
        rgb_texture[..., 2] = self.rgb[2]
        return rgb_texture
    
    def __str__(self):
        return f"{type(self).__name__} size:{self.texture_size} rgb:{self.rgb}"


class CircleGrayTex(TextureBase):
    """ 
    Filled circle: grayscale on grayscale with circle_radius, centered at circle_center
    with face color fg_intensity on background bg_intensity. Center position is in pixels
    from center of image.
    """
    def __init__(self, texture_size = 512,  texture_name = "gray_circle", circle_center = (0,0),
                 circle_radius = 100, bg_intensity = 0, fg_intensity  = 255):
        self.center = circle_center
        self.radius = circle_radius
        self.bg_intensity = bg_intensity
        self.fg_intensity = fg_intensity
        super().__init__(texture_size = texture_size, texture_name = texture_name)
        
    def create_texture(self):
        min_int = np.min([self.fg_intensity, self.bg_intensity])
        max_int = np.max([self.fg_intensity, self.bg_intensity])
        if max_int > 255 or min_int < 0:
            raise ValueError('Circle intensity must lie in [0, 255]')
        x = np.linspace(-self.texture_size/2, self.texture_size/2, self.texture_size)
        y = np.linspace(-self.texture_size/2, self.texture_size/2, self.texture_size)
        X, Y = np.meshgrid(x, y)
        circle_texture = self.bg_intensity*np.ones((self.texture_size,self.texture_size), dtype = np.uint8)
        circle_mask = (X - self.center[0])**2 + (Y - self.center[1])**2 <= self.radius**2
        circle_texture[circle_mask] = self.fg_intensity
        return np.uint8(circle_texture)

    def __str__(self):
        part1 =  f"{type(self).__name__} size:{self.texture_size} center:{self.center} "
        part2 = f"radius:{self.radius} bg:{self.bg_intensity} fg:{self.fg_intensity}"
        return part1 + part2
  
  
class SinGrayTex(TextureBase):
    """
    Grayscale sinusoidal grating texture.

    To do:
        Currently doesn't handle phase or contrast (usually handled by ShowBase)
    """
    def __init__(self, texture_size = 512, texture_name = "sin_gray", spatial_frequency = 10):
        self.frequency = spatial_frequency
        super().__init__(texture_size = texture_size, texture_name = texture_name)

    def create_texture(self):
        x = np.linspace(0, 2*np.pi, self.texture_size + 1)
        y = np.linspace(0, 2*np.pi, self.texture_size + 1)
        array, Y = np.meshgrid(x[: self.texture_size],y[: self.texture_size])
        return utils.sin_byte(array, freq = self.frequency) 
    
    def __str__(self):
        return f"{type(self).__name__} size:{self.texture_size} frequency:{self.frequency}"
    
    
class SinRgbTex(TextureBase):
    """
    Sinusoid that goes from black to the given rgb value. 

    To do:
        Currently doesn't handle phase, contrast 
        Would be nice to have it cycle between two different colors, not just rgb/black.
    """
    def __init__(self, texture_size = 512, texture_name = "sin_rgb", 
                 spatial_frequency = 10, rgb = (255, 0, 0)):
        self.frequency = spatial_frequency
        self.rgb = rgb
        super().__init__(texture_size = texture_size, texture_name = texture_name)
    
    def create_texture(self):
        if not (all([x >= 0 for x in self.rgb]) and all([x <= 255 for x in self.rgb])):
            raise ValueError("SinRgbTex.sin_texture_rgb(): rgb values must lie in [0,255]")
        x = np.linspace(0, 2*np.pi, self.texture_size+1)
        y = np.linspace(0, 2*np.pi, self.texture_size+1)
        array, Y = np.meshgrid(x[: self.texture_size],y[: self.texture_size])
        R = np.uint8((self.rgb[0]/255)*utils.sin_byte(array, freq = self.frequency))
        G = np.uint8((self.rgb[1]/255)*utils.sin_byte(array, freq = self.frequency))
        B = np.uint8((self.rgb[2]/255)*utils.sin_byte(array, freq = self.frequency))
        rgb_sin = np.zeros((self.texture_size, self.texture_size, 3), dtype = np.uint8)
        rgb_sin[...,0] = R
        rgb_sin[...,1] = G
        rgb_sin[...,2] = B
        return rgb_sin
    
    def __str__(self):
        return f"{type(self).__name__} size:{self.texture_size} frequency:{self.frequency} rgb:{self.rgb}"
    
    
class GratingGrayTex(TextureBase):
    """
    Grayscale 2d square wave (grating)
    """
    def __init__(self, texture_size = 512,  texture_name = "grating_gray", 
                 spatial_frequency = 10):
        self.frequency = spatial_frequency
        super().__init__(texture_size = texture_size, texture_name = texture_name)
    
    def create_texture(self):
        x = np.linspace(0, 2*np.pi, self.texture_size+1)
        y = np.linspace(0, 2*np.pi, self.texture_size+1)
        X, Y = np.meshgrid(x[: self.texture_size],y[: self.texture_size])
        return utils.grating_byte(X, freq = self.frequency)
    
    def __str__(self):
        return f"{type(self).__name__} size:{self.texture_size} frequency:{self.frequency}"
    
    
class GratingRgbTex(TextureBase):
    """
    Rgb 2d square wave (grating) stimulus class (goes from black to rgb val)
    """
    def __init__(self, texture_size = 512, texture_name = "grating_rgb", 
                 spatial_frequency = 10, rgb = (255, 0, 0)):
        self.frequency = spatial_frequency
        self.rgb = rgb
        super().__init__(texture_size = texture_size, texture_name = texture_name)
    
    def create_texture(self):
        x = np.linspace(0, 2*np.pi, self.texture_size+1)
        y = np.linspace(0, 2*np.pi, self.texture_size+1)
        X, Y = np.meshgrid(x[: self.texture_size],y[: self.texture_size])
        R = np.uint8((self.rgb[0]/255)*utils.grating_byte(X, freq = self.frequency))
        G = np.uint8((self.rgb[1]/255)*utils.grating_byte(X, freq = self.frequency))
        B = np.uint8((self.rgb[2]/255)*utils.grating_byte(X, freq = self.frequency))
        rgb_grating = np.zeros((self.texture_size, self.texture_size, 3), dtype = np.uint8)
        rgb_grating[...,0] = R
        rgb_grating[...,1] = G
        rgb_grating[...,2] = B
        return rgb_grating 
        
    def __str__(self):
        return f"{type(self).__name__} size:{self.texture_size} frequency:{self.frequency} rgb:{self.rgb}"


class BlankTex(TextureBase):
    """
    Grayscale 2d square wave (grating)
    """

    def __init__(self, texture_size=512, texture_name="blank_tex"):
        super().__init__(texture_size=texture_size, texture_name=texture_name)

    def create_texture(self):
        tex = np.zeros(self.texture_size)
        return np.uint8(tex)

    def __str__(self):
        return f"{type(self).__name__} size:{self.texture_size} "

'''
All XY classes require textures to be formatted as a tuple (x,y), but otherwise function similarly.
'''


class TextureBaseXY:
    """
    Base class for all XY stimuli: subclass this when making specific stimuli.
    You need to implement the create_texture() method, and any parameters
    needed for the texture function. These support non-square shaped windows and textures
    """

    def __init__(self, texture_size=(512, 512), texture_name="stimulus"):
        self.texture_size = texture_size
        self.texture_name = texture_name
        # Create texture
        self.texture_array = self.create_texture()
        self.texture = Texture(self.texture_name)
        # Set texture formatting (greyscale or rgb have different settings)
        if self.texture_array.ndim == 2:
            self.texture.setup2dTexture(self.texture_size[0], self.texture_size[1],
                                        Texture.T_unsigned_byte,
                                        Texture.F_luminance)
            self.texture.setRamImageAs(self.texture_array, "L")
        elif self.texture_array.ndim == 3:
            self.texture.setup2dTexture(self.texture_size[0], self.texture_size[1],
                                        Texture.T_unsigned_byte,
                                        Texture.F_rgb8)
            self.texture.setRamImageAs(self.texture_array, "RGB")

    def create_texture(self):
        """
        Create 2d numpy array for stimulus: either nxmx1 (grayscale) or nxm x 3 (rgb)
        """
        pass

    def view(self):
        """
        Plot the texture using matplotlib. Useful for debugging.
        """
        plt.imshow(self.texture_array, vmin=0, vmax=255)
        if self.texture_array.ndim == 2:
            plt.set_cmap('gray')

        plt.title(self.texture_name)
        plt.gca().invert_yaxis()
        plt.show()

    def __str__(self):
        """
        Return the string you want print(Tex) to show, and to save to file
        when saving catalog of stimuli.
        """
        pass


class BlankTexXY(TextureBaseXY):
    """
    Grayscale 2d square wave (grating)
    """

    def __init__(self, texture_size=(512, 512), texture_name="blank_tex"):
        super().__init__(texture_size=texture_size, texture_name=texture_name)

    def create_texture(self):
        tex = np.zeros(self.texture_size)
        return np.uint8(tex)

    def __str__(self):
        return f"{type(self).__name__} size:{self.texture_size} "


class GratingGrayTexXY(TextureBaseXY):
    """
    Grayscale 2d square wave (grating)
    """

    def __init__(self, texture_size=(512, 512), texture_name="grating_gray",
                 spatial_frequency=10, dark_val=0, light_val=255):
        self.frequency = spatial_frequency
        self.dark_val = dark_val
        self.light_val = light_val
        super().__init__(texture_size=texture_size, texture_name=texture_name)

    def create_texture(self):
        x = np.linspace(0, 2 * np.pi, self.texture_size[0] + 1)
        y = np.linspace(0, 2 * np.pi, self.texture_size[1] + 1)
        X, Y = np.meshgrid(x[: self.texture_size[0]], y[: self.texture_size[1]])
        tex = utils.grating_byte(X, freq=self.frequency)
        tex[tex==0] = self.dark_val
        tex[tex==255] = self.light_val
        return tex

    def __str__(self):
        return f"{type(self).__name__} size:{self.texture_size} frequency:{self.frequency}"


class CalibrationTriangles(TextureBaseXY):
    """
    Filled circle: grayscale on grayscale with circle_radius, centered at circle_center
    with face color fg_intensity on background bg_intensity. Center position is in pixels
    from center of image.
    """

    def __init__(self, texture_size=(1024, 1024), texture_name="circs", tri_size=50,
                 circle_radius=7, x_off=500, y_off=0
                 ):

        self.texture_size = texture_size

        self.tri_size = tri_size
        self.x_offset = x_off
        self.y_offset = y_off

        self.radius = circle_radius

        self.midx = self.texture_size[0]//2
        self.midy = self.texture_size[1]//2

        self.pt1 = (int((self.midx + self.x_offset - (self.tri_size * math.sqrt(3)) // 2)),
                    int((self.midy + self.y_offset + self.tri_size // 2)))

        self.pt2 = (int((self.midx + self.x_offset + (self.tri_size * math.sqrt(3)) // 2)),
                    int((self.midy + self.y_offset - self.tri_size // 2)))

        self.pt3 = (int((self.midx + self.x_offset - (self.tri_size * math.sqrt(3)) // 2)),
                    int((self.midy + self.y_offset - self.tri_size // 2)))

        super().__init__(texture_size=texture_size, texture_name=texture_name)

    def create_texture(self):
        circle_texture = np.zeros((self.texture_size[1], self.texture_size[0]))

        [cv2.circle(circle_texture, i, self.radius, 255, -1) for i in [self.pt1, self.pt2, self.pt3]]

        output = np.uint8(circle_texture)

        return output

    def __str__(self):
        return f"{type(self).__name__} size:{self.texture_size} center:{self.midx, self.midy} radius:{self.radius}"

    def projct_coords(self):
        return np.array([self.pt1, self.pt2, self.pt3])


class RadialSinCube(TextureBaseXY):
    def __init__(self, texture_size=(1024,1024), phase=0, period=32, texture_name='radial_sin_centering'):
        self.phase = phase
        self.period = period
        super().__init__(texture_size=texture_size, texture_name=texture_name)

    def create_texture(self):
        x = np.linspace(-self.period*np.pi, self.period*np.pi, self.texture_size[0])
        y = np.linspace(-self.period*np.pi, self.period*np.pi, self.texture_size[1])
        return np.round((2*np.pi/self.period)*np.sin(np.sqrt(x[None, :]**2 + y[:, None]**2)+self.phase)*127+127).astype(np.uint8)

    def __str__(self):
        return f"{type(self).__name__} size:{self.texture_size} period:{self.period} phase: {self.phase}"

# %%
if __name__ == '__main__':
    example = 5
    if example == 0:
        pink_rgb = RgbTex(rgb = (255, 150, 150))
        
        pink_rgb.view()
    
    if example == 1:
        gray_circ = CircleGrayTex(circle_center = (0, 150), 
                                  circle_radius = 75,
                                  bg_intensity = 50, 
                                  fg_intensity = 200)
        gray_circ.view()

    if example == 2:
        gray_sin = SinGrayTex(texture_size = 512, 
                              texture_name = "SinGrayTex()",
                              spatial_frequency = 4)
        gray_sin.view()
        
    elif example == 3:
        red_sin = SinRgbTex(texture_size = 1024, 
                            texture_name = 'red SinRgbTex()', 
                            spatial_frequency = 20, 
                            rgb = (255, 0, 0))
        red_sin.view()
        
    elif example == 4:
        gray_grate = GratingGrayTex(spatial_frequency = 15)
        gray_grate.view()
        
    elif example == 5:
        rgb_grate = GratingRgbTex(rgb = (255, 0 , 0), spatial_frequency = 20)
        rgb_grate.view()
