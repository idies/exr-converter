from astropy.io import fits
import numpy
import os
import OpenEXR
import json
import warnings
from .utils import __FITS_HEADERS_ID, __get_pixeltype_from_channel, __get_exrpixel_from_channel,\
    __change_array_type
from .pixeltype import PixelType

def convert_directory(path, output_pixel_type=None, verbose=True):
    """
    Converts directory of EXR files to FITS.
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
        if filename[-3:] == "exr":
            output_filename = path + '/' + filename[:-4] + ".fits"
        else:
            continue
        
        if verbose:
            print ("Converting: " + filename)
         
        convert(path + '/' + filename, output_filename, output_pixel_type, verbose)

def convert(input_exr, output_fits, output_pixel_type=None, verbose=True):
    """
    Converts an input EXR file into a FITS file. Multiple layers in the input EXR file are created as multiple image
    HDUs in the output FITS file. The pixels in the output image file can also be set to a different type as that of
    the pixels in the input image file.
    :param input_exr: path (string) of the input EXR file.
    :param output_fits: path (string) to the output FITS file.
    :param output_pixel_type: If equal to None, the output file image will have the same pixel type or format
                              of that in the input file image. If changing the pixel type is desired, then
                              output_pixel_type can take the values defined by the fields in the class
                              exrconverter.pixeltype.PixelType. Example: output_pixel_type=PixelType.FLOAT32.
                              Since the underlying implementation uses numpy arrays, output_pixel_type can also take
                              numpy dtypes values, For example, output_pixel_type=numpy.float32.
    :param verbose: Boolean variable for deciding whether to print warning messages.
    :example: convert(input_exr="/path/to/input_exr.exr", output_fits="/path/to/input_exr.exr",
                      output_pixel_type=numpy.float32, verbose=True)
    """

    exr_file = OpenEXR.InputFile(input_exr)
    exr_header = exr_file.header()
    if exr_header.get(__FITS_HEADERS_ID) is not None:
        fits_headers = json.loads(exr_header[__FITS_HEADERS_ID])
    else:
        fits_headers = None

    dw = exr_header['dataWindow']
    image_size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
    hdu_list = fits.HDUList()

    exr_header = exr_file.header()

    for channel_index in sorted(exr_header['channels'].keys(), key=lambda x: float(x)):
        channel_type = exr_header['channels'][channel_index]
        byte_image = exr_file.channel(str(channel_index), __get_exrpixel_from_channel(channel_type))
        pixel_type = __get_pixeltype_from_channel(channel_type)

        if output_pixel_type is None:
            output_pixel_type = pixel_type

        hdu_data = numpy.frombuffer(byte_image, dtype=pixel_type)
        hdu_data.shape = (image_size[1], image_size[0])

        if output_pixel_type == PixelType.FLOAT16:
            hdu_data = __change_array_type(hdu_data, numpy.float32)
            if verbose:
                warnings.warn("Fits does not support " + str(hdu_data.dtype) + " images. Converted to FLOAT32 instead.")
        else:
            hdu_data = __change_array_type(hdu_data, output_pixel_type)

        if fits_headers is None:
            hdu_list.append(fits.ImageHDU(data=hdu_data))
        else:
            hdu_header = fits.Header.fromstring(fits_headers[int(channel_index)])
            hdu_list.append(fits.ImageHDU(data=hdu_data, header=hdu_header))

    hdu_list.writeto(output_fits, overwrite=True)
