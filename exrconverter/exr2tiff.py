import SimpleITK as sitk
import numpy
import OpenEXR
import json
import os
import warnings
from .utils import __TIFF_HEADERS_ID, __get_pixeltype_from_channel, __get_exrpixel_from_channel,\
    __change_array_type
from .pixeltype import PixelType


def convert_directory(path, output_pixel_type=None, verbose=True):
    """
    Converts directory of EXR files to TIFF.
    :param path: path of the directory.
    :param output_pixel_type: If equal to None, the output file image will have the same pixel type or format
                              of that in the input file image. If changing the pixel type is desired, then
                              output_pixel_type can take the values defined by the fields in the class
                              exrconverter.pixeltype.PixelType. Example: output_pixel_type=PixelType.FLOAT32.
                              Since the underlying implementation uses numpy arrays, output_pixel_type can also take
                              numpy dtypes values, For example, output_pixel_type=numpy.float32.
    :param verbose: Boolean variable for deciding whether to print warning messages.
    :example: convert_directory(path='path/to/exr', output_pixel_type=numpy.float32, verbose=True)
    """
    for filename in os.listdir(path):
        if filename[-3:] != 'exr':
            continue
        if verbose:
            print ("Converting: " + filename)
    
        output_filename = path + '/' + filename[:-4] + ".tif"
         
        convert(path + '/' + filename, output_filename, output_pixel_type, verbose)

def convert(input_exr, output_tiff, output_pixel_type=None, verbose=True):
    """
    Converts an input EXR file into a TIFF file. Multiple layers in the input EXR file are created as multiple layers in the output Tiff file. The pixels in the output image file can also be set to a different type as that of
    the pixels in the input image file.
    :param input_exr: path (string) of the input EXR file.
    :param output_tiff: path (string) to the output TIFF file.
    :param output_pixel_type: If equal to None, the output file image will have the same pixel type or format
                              of that in the input file image. If changing the pixel type is desired, then
                              output_pixel_type can take the values defined by the fields in the class
                              exrconverter.pixeltype.PixelType. Example: output_pixel_type=PixelType.FLOAT32.
                              Since the underlying implementation uses numpy arrays, output_pixel_type can also take
                              numpy dtypes values, For example, output_pixel_type=numpy.float32.
    :param verbose: Boolean variable for deciding whether to print warning messages.
    :example: convert(input_exr="/path/to/input_exr.exr", output_tiff="/path/to/output_tiff.tiff",
                      output_pixel_type=numpy.float32, verbose=True)
    """
    exr_file = OpenEXR.InputFile(input_exr)
    exr_header = exr_file.header()
    tiff_headers = json.loads(exr_header[__TIFF_HEADERS_ID])
    
    dw = exr_header['dataWindow']
    image_size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
    
    tiff_image = []
    for channel_index in sorted(exr_header['channels'].keys(), key=lambda x: float(x)): 
        channel_type = exr_header['channels'][channel_index]
        byte_image = exr_file.channel(str(channel_index), __get_exrpixel_from_channel(channel_type))
        pixel_type = __get_pixeltype_from_channel(channel_type)
        if output_pixel_type is None:
            output_pixel_type = pixel_type
        
        image_data = numpy.frombuffer(byte_image, dtype=pixel_type)
        image_data = numpy.reshape(image_data, (image_size[1], image_size[0]))
        
        if output_pixel_type == PixelType.FLOAT16:
            image_data = __change_array_type(image_data, numpy.float32)
            if verbose:
                warnings.warn("Tiff does not support " + str(image_data.dtype) + " images. Converted to FLOAT32 instead.")
        else:          
            image_data = __change_array_type(image_data, output_pixel_type)

        tiff_image.append(image_data)
    
    tiff_image_final = sitk.GetImageFromArray(tiff_image)

    for key in tiff_headers[0].keys():
        tiff_image_final.SetMetaData(key, tiff_headers[0][key])

    for channel in range(tiff_image_final.GetDepth()):
        for key in tiff_headers[channel + 1].keys():
            tiff_image_final[:,:,channel].SetMetaData(key, tiff_headers[channel + 1][key])
    
    sitk.WriteImage(tiff_image_final, output_tiff)

    
        
            