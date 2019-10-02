from astropy.io import fits
import OpenEXR
import json
import warnings
from .utils import __FITS_HEADERS_ID, __get_pixeltype_from_bitpix, __change_array_type, __get_channel_from_pixeltype


def convert(input_fits, output_exr, output_pixel_type=None):
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
            warnings.warn("Fits file has no images.")
            return

        exr_header = OpenEXR.Header(image_array_shape[1], image_array_shape[0])
        exr_header['channels'] = {}
        exr_data = {}
        fits_headers = []

        for exr_index, fits_index in enumerate(fits_image_indexes):
            hdu = hdu_list[fits_index]
            exr_data[str(exr_index)] = __change_array_type(hdu.data, output_pixel_type)
            exr_header['channels'][str(exr_index)] = __get_channel_from_pixeltype(output_pixel_type)
            fits_headers.append(hdu.header.tostring())

        exr_header[__FITS_HEADERS_ID] = str.encode(json.dumps(fits_headers))

        try:
            exr_file = OpenEXR.OutputFile(output_exr, exr_header)
            exr_file.writePixels(exr_data)
        finally:
            exr_file.close()
