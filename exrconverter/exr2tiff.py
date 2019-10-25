from PIL import Image
import numpy
import OpenEXR
import Imath
import json
import warnings
from .utils import __FITS_HEADERS_ID, __get_pixeltype_from_channel, __get_exrpixel_from_channel,\
    __change_array_type
from .pixeltype import PixelType

def convert(input_exr, output_tiff, output_pixel_type=None, verbose=True):
    
    exr_file = OpenEXR.InputFile(input_exr)
    exr_header = exr_file.header()
    tiff_headers = json.loads(exr_header[__TIFF_HEADERS_ID])
    dw = exr_header['dataWindow']
    image_size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
    exr_header = exr_file.header()
    tiff_image_list = []
    
    for channel_idex in range(len(exr_file.header()['channels'])):
        
        channel_type = exr_header['channels'][str(channel_index)]
        byte_image = exr_file.channel(str(channel_index), __get_exrpixel_from_channel(channel_type))
        pixel_type = __get_pixeltype_from_channel(channel_type)
        
        if output_pixel_type is None:
            output_pixel_type = pixel_type
        
        image_data = numpy.frombuffer(byte_image, dtype=pixel_type)
        # Make sure these should be switched here
        image_data_shape = (image_size[1], image_size[0])
        
        # Pretty sure TIFF supports 16 bit!!!
        image_data = __change_array_type(image_data, output_pixel_type)
        
        # Might have to specify type here
        image = Image.fromarray(image_data)
        
        # Not sure that this is the right thing to do here. Need to add tags to each image
        image.tag = tiff_headers[channel_index]
        
        tiff_image_list.append(image)
    
    if len(tiff_image_list) == 0:
        warnings.warn("No image provided.")
        
    elif len(tiff_image_list) == 1:
        tiff_image_list[0].save(output_tiff, format = "tiff")
        
    else:
        tiff_image_list[0].save(output_tiff, format = "tiff", append_images = tiff_image_list[1:], save_all = True)
        
    
        
            