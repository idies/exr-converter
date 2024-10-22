from astropy.io import fits
import OpenEXR
import os
import json
import Imath
import warnings
from .utils import __FITS_HEADERS_ID, __get_pixeltype_from_bitpix, __change_array_type, __get_channel_from_pixeltype

def convert_directory(path, compression=None, output_pixel_type=None, verbose=True):
    """
    Converts directory of FITS files to EXR.
    :param path: path of the directory.
    :param compression: If equal to None, the output file will have ZIP_COMPRESSION (this is the exr default). 
                        Options are 'NONE', 'RLE', 'ZIPS', 'ZIPS', 'PIZ', 'PXR24', 'B44'. 'B44A', 'DWAA', or 'DWAB'.
    :param output_pixel_type: If equal to None, the output file image will have the same pixel type or format
                              of that in the input file image. If changing the pixel type is desired, then
                              output_pixel_type can take the values defined by the fields in the class
                              exrconverter.pixeltype.PixelType. Example: output_pixel_type=PixelType.FLOAT32.
                              Since the underlying implementation uses numpy arrays, output_pixel_type can also take
                              numpy dtypes values, For example, output_pixel_type=numpy.float32.
    :param verbose: Boolean variable for deciding whether to print warning messages.
    :example: convert_directory(path='path/to/fits', output_pixel_type=numpy.float32, verbose=True)
    """
    
    for filename in os.listdir(path):
        if filename[-4:] == 'fits':
            output_filename = path + '/' + filename[:-5] + ".exr"
        else:
            continue
        
        if verbose:
            print ("Converting: " + filename)
         
        convert(path + '/' + filename, output_filename, compression, output_pixel_type, verbose)

def convert(input_fits, output_exr, compression=None, output_pixel_type=None, verbose=True):
    """
    Converts an input FITS file into an EXR file. If the FITS file contains several HDUs, the code finds the
    first 2D image HDUs that are of the same dimensions, and writes them as layers in the output EXR file.
    The pixels in the output image file can also be set to a different type as that of the pixels in the input
    image file.
    :param input_fits: path (string) of the input FITS file.
    :param output_exr: path (string) to the output EXR file.
    :param compression: If equal to None, the output file will have ZIP_COMPRESSION (this is the exr default). 
                        Options are 'NONE', 'RLE', 'ZIPS', 'ZIPS', 'PIZ', 'PXR24', 'B44'. 'B44A', 'DWAA', or 'DWAB'.
    :param output_pixel_type: If equal to None, the output file image will have the same pixel type or format
                              of that in the input file image. If changing the pixel type is desired, then
                              output_pixel_type can take the values defined by the fields in the class
                              exrconverter.pixeltype.PixelType. Example: output_pixel_type=PixelType.FLOAT32.
                              Since the underlying implementation uses numpy arrays, output_pixel_type can also take
                              numpy dtypes values, For example, output_pixel_type=numpy.float32.
    :param verbose: Boolean variable for deciding whether to print warning messages.
    :example: convert(input_fits="/path/to/input_fits.fits", output_exr="/path/to/output_exr.exr",
                      output_pixel_type=numpy.float32, verbose=True)
    """

    fits_image_indexes = []  # will contain the indexes of HDUs (within the fits file) that contain images.
    image_array_shape = None

    with fits.open(input_fits) as hdu_list:

        for index, hdu in enumerate(hdu_list):
            if hdu.is_image:
                if len(hdu.data.shape) == 2:  # only 2D arrays for now

                    if image_array_shape is None:
                        image_array_shape = hdu.data.shape
                        fits_image_indexes.append(index)
                        if output_pixel_type is None:
                            output_pixel_type = __get_pixeltype_from_bitpix(bitpix=hdu.header["BITPIX"])
                    else:
                        if hdu.data.shape == image_array_shape \
                                and output_pixel_type == __get_pixeltype_from_bitpix(bitpix=hdu.header["BITPIX"]):
                            fits_image_indexes.append(index)

        if len(fits_image_indexes) == 0:
            if verbose:
                warnings.warn("Fits file has no images.")
            return

        exr_header = OpenEXR.Header(image_array_shape[1], image_array_shape[0])

        compression_options = {'NO' : Imath.Compression.NO_COMPRESSION, 'RLE' : Imath.Compression.RLE_COMPRESSION, 'ZIPS' : Imath.Compression.ZIPS_COMPRESSION,
                            'ZIP' : Imath.Compression.ZIP_COMPRESSION, 'PIZ' : Imath.Compression.PIZ_COMPRESSION, 'PXR24' : Imath.Compression.PXR24_COMPRESSION,
                            'B44' : Imath.Compression.B44_COMPRESSION, 'B44A' : Imath.Compression.B44A_COMPRESSION,'DWAA' : Imath.Compression.DWAA_COMPRESSION, 
                            'DWAB' : Imath.Compression.DWAB_COMPRESSION
                            }
    
        if compression:
            exr_header['compression'] = Imath.Compression(compression_options[compression])

        exr_header['channels'] = {}
        exr_data = {}
        fits_headers = []

        for exr_index, fits_index in enumerate(fits_image_indexes):
            hdu = hdu_list[fits_index]
            exr_data[str(exr_index)] = __change_array_type(hdu.data, output_pixel_type)
            exr_header['channels'][str(exr_index)] = __get_channel_from_pixeltype(output_pixel_type)
            fits_headers.append(
                hdu.header.tostring())

        exr_header[__FITS_HEADERS_ID] = str.encode(json.dumps(fits_headers))

        try:
            exr_file = OpenEXR.OutputFile(output_exr, exr_header)
            exr_file.writePixels(exr_data)
        finally:
            exr_file.close()
