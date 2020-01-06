import numpy
import Imath
import OpenEXR
from .pixeltype import PixelType

__FITS_HEADERS_ID = "fits_headers"
__TIFF_HEADERS_ID = "tiff_headers"


def __get_pixeltype_from_bitpix(bitpix):
    if bitpix == 8:
        return PixelType.INT8
    elif bitpix == 16:
        return PixelType.INT16
    elif bitpix == 32:
        return PixelType.INT32
    elif bitpix == -32:
        return PixelType.FLOAT32
    elif bitpix == -64:
        return PixelType.FLOAT64
    else:
        raise Exception("Unsupported bitpix value " + str(bitpix))


def __change_array_type(array, pixel_type):
    if pixel_type == PixelType.FLOAT64:
        return numpy.float32(array)
    if pixel_type == PixelType.FLOAT32:
        return numpy.float32(array)
    elif pixel_type == PixelType.FLOAT16:
        return numpy.float16(array)
    elif pixel_type == PixelType.INT32:
        return numpy.int32(array)
    elif pixel_type == PixelType.INT16:
        return numpy.int16(array)
    elif pixel_type == PixelType.INT8:
        return numpy.int8(array)
    elif pixel_type == PixelType.UINT16:
        return numpy.uint16(array)
    else:
        raise Exception("Unsupported pixel_format value " + str(pixel_type))


def __get_channel_from_pixeltype(pixel_type):
    if pixel_type == PixelType.FLOAT32:
        return Imath.Channel(Imath.PixelType(OpenEXR.FLOAT))
    elif pixel_type == PixelType.FLOAT16:
        return Imath.Channel(Imath.PixelType(OpenEXR.HALF))
    else:
        raise Exception("Unsupported pixel_format value " + str(pixel_type))


def __get_pixeltype_from_channel(channel_type):
    if channel_type == Imath.Channel(Imath.PixelType(OpenEXR.FLOAT)):
        return PixelType.FLOAT32
    elif channel_type == Imath.Channel(Imath.PixelType(OpenEXR.HALF)):
        return PixelType.FLOAT16
    else:
        raise Exception("Unsupported channel type " + str(channel_type))


def __get_exrpixel_from_channel(channel_type):
    if channel_type == Imath.Channel(Imath.PixelType(OpenEXR.FLOAT)):
        return Imath.PixelType(OpenEXR.FLOAT)
    elif channel_type == Imath.Channel(Imath.PixelType(OpenEXR.HALF)):
        return Imath.PixelType(OpenEXR.HALF)
    else:
        raise Exception("Unsupported channel type " + str(channel_type))


def __get_bitpix_from_channel(channel_type):
    if channel_type == Imath.Channel(Imath.PixelType(OpenEXR.FLOAT)):
        return -32
    elif channel_type == Imath.Channel(Imath.PixelType(OpenEXR.HALF)):
        return -16
    else:
        raise Exception("Unsupported channel type " + str(channel_type))

def __get_pixeltype_from_tiff(pixel_type):
    # Add more types as they show up
    if pixel_type == "32-bit float":
        return PixelType.FLOAT32
    elif pixel_type == '64-bit float':
        return PixelType.FLOAT64
    else:
        raise Exception("Unsupported pixel value " + str(pixel_type))