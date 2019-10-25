from PIL import Image
import numpy
import OpenEXR
import Imath
import json
import warnings
from .utils import __FITS_HEADERS_ID, __get_pixeltype_from_channel, __get_exrpixel_from_channel, __change_array_type
from .pixeltype import PixelType

def convert(input_tiff, output_exr, output_pixel_type=None, verbose=True):
    
    tiff_image_indexes = []
    image_array_shape = None
    
    with Image.open('multipage_tiff_example.tif') as tiff:
                
        for index in range(tiff.n_frames):
            tiff.seek(index)
            
            # This might need to be fleshed out more. 
            if image_array_shape is None:
                # 256 is the key for ImageWidth and 257 is the key for ImageLength
                image_array_shape = (tiff.tag[256][0], tiff.tag[257][0])
                tiff_image_indexes.append(index)
            else:
                if (tiff.tag[256], tiff.tag[257]) == image_array_shape:
                    tiff_image_indexes.append(index)
        
        if len(tiff_image_indexes) == 0:
            if verbose:
                warnings.warn("Tiff file has no images")
            return
        
        print (type(image_array_shape[1]))
        exr_header = OpenEXR.Header(image_array_shape[1], image_array_shape[0])
        exr_header['channels'] = {}
        exr_data = {}
        tiff_headers = []

        for exr_index, tiff_index in enumerate(tiff_image_indexes):
            tiff.seek(tiff_index)
            exr_data[str(exr_index)] = __change_array_type(np.array(tiff), output_pixel_type)
            exr_header['channels'][str(exr_index)] = __get_channel_from_pixeltype(output_pixel_type)
            tiff_headers.append(dict(tiff.tag))
            
        exr_header[__TIFF_HEADERS_ID] = str.encode(json.dumps(tiff_headers))

        try:
            exr_file = OpenEXR.OutputFile(output_exr, exr_header)
            exr_file.writePixels(exr_data)
        finally:
            exr_file.close()