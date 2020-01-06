import SimpleITK as sitk
import numpy
import OpenEXR
import Imath
import json
import warnings
import os
from .utils import __get_pixeltype_from_channel, __get_exrpixel_from_channel, __change_array_type, __get_channel_from_pixeltype, __TIFF_HEADERS_ID
from .pixeltype import PixelType
    
def convert_directory(path, compression=None, output_pixel_type=None, verbose=True):
    """
    Converts directory of TIFF files to EXR.
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
    :example: convert_directory(path='path/to/tif', output_pixel_type=numpy.float32, verbose=True)
    """
    
    for filename in os.listdir(path):
        if filename[-4:] == 'tiff':
            output_filename = path + '/' + filename[:-5] + ".exr"
        elif filename[-3:] == 'tif':
            output_filename = path + '/' + filename[:-4] + ".exr"
        else:
            continue
        
        if verbose:
            print ("Converting: " + filename)
         
        convert(path + '/' + filename, output_filename, compression, output_pixel_type, verbose)

def convert(input_tiff, output_exr, compression=None, output_pixel_type=None, verbose=True):
    """
    Converts an input Tiff file into a EXR file. Multiple layers in the input Tiff file are created as multiple layers in the output EXR file. The pixels in the output image file can also be set to a different type as that of
    the pixels in the input image file.
    :param input_tiff: path (string) of the input TIFF file.
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
    :example: convert(input_tiff="/path/to/input_tiff.tiff", output_exr="/path/to/output_exr.exr",
                      output_pixel_type=numpy.float32, verbose=True)
    """
    reader = sitk.ImageFileReader()
    reader.SetImageIO("TIFFImageIO")
    reader.SetFileName(input_tiff)
    tiff_image = reader.Execute()
    tiff_image_array = sitk.GetArrayFromImage(tiff_image)
    
    if not output_pixel_type:
        tiff_image.GetPixelIDType()
        # Need to fill this in. 

    image_array_shape = tiff_image.GetSize()
    
    exr_header = OpenEXR.Header(image_array_shape[0], image_array_shape[1])
    # exr_header['compression'] = Imath.Compression(Imath.Compression.PIZ_COMPRESSION)

    compression_options = {'NO' : Imath.Compression.NO_COMPRESSION, 'RLE' : Imath.Compression.RLE_COMPRESSION, 'ZIPS' : Imath.Compression.ZIPS_COMPRESSION,
                            'ZIP' : Imath.Compression.ZIP_COMPRESSION, 'PIZ' : Imath.Compression.PIZ_COMPRESSION, 'PXR24' : Imath.Compression.PXR24_COMPRESSION,
                            'B44' : Imath.Compression.B44_COMPRESSION, 'B44A' : Imath.Compression.B44A_COMPRESSION,'DWAA' : Imath.Compression.DWAA_COMPRESSION, 
                            'DWAB' : Imath.Compression.DWAB_COMPRESSION
                            }
    
    if compression:
        exr_header['compression'] = Imath.Compression(compression_options[compression])

    exr_header['channels'] = {}
    exr_data = {}
    tiff_headers = []
    
    meta_data = {}
    for key in tiff_image.GetMetaDataKeys():
        meta_data[key] = tiff_image.GetMetaData(key)
    tiff_headers.append(meta_data)
    
    for channel in range(tiff_image.GetDepth()):
        exr_data[str(channel)] = __change_array_type(tiff_image_array[channel], output_pixel_type)
        exr_header['channels'][str(channel)] = __get_channel_from_pixeltype(output_pixel_type)
        
        meta_data = {}
        for key in tiff_image[:,:,channel].GetMetaDataKeys():
            meta_data[key] = tiff_image[:,:,channel].GetMetaData(key)
        tiff_headers.append(meta_data)
        
    exr_header[__TIFF_HEADERS_ID] = str.encode(json.dumps(tiff_headers))
    
    try:
        
        exr_file = OpenEXR.OutputFile(output_exr, exr_header)
        exr_file.writePixels(exr_data)

    finally:
        exr_file.close()

        