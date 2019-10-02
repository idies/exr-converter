from astropy.io import fits
import numpy
import OpenEXR
import json
import warnings
from .utils import __FITS_HEADERS_ID, __get_pixeltype_from_channel, __get_exrpixel_from_channel,\
    __change_array_type
from .pixeltype import PixelType


def convert(input_exr, output_fits, output_pixel_type=None, verbose=True):

    exr_file = OpenEXR.InputFile(input_exr)
    exr_header = exr_file.header()
    fits_headers = json.loads(exr_header[__FITS_HEADERS_ID])
    dw = exr_header['dataWindow']
    image_size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
    hdu_list = fits.HDUList()

    exr_header = exr_file.header()

    for channel_index in range(len(exr_file.header()['channels'])):

        channel_type = exr_header['channels'][str(channel_index)]

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

        hdu_header = fits.Header.fromstring(fits_headers[channel_index])
        hdu_list.append(fits.ImageHDU(data=hdu_data, header=hdu_header))

    hdu_list.writeto(output_fits, overwrite=True)
