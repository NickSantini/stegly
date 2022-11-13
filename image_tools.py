import cv2
import numpy as np
import colour as cs
from colour.algebra import vector_dot

HORIZ_AXIS = 1
VERT_AXIS  = 0

# Standard quantization table as defined by JPEG
JPEG_STD_LUM_QUANT_TABLE = np.asarray([
                                        [16, 11, 10, 16,  24, 40,   51,  61],
                                        [12, 12, 14, 19,  26, 58,   60,  55],
                                        [14, 13, 16, 24,  40, 57,   69,  56],
                                        [14, 17, 22, 29,  51, 87,   80,  62],
                                        [18, 22, 37, 56,  68, 109, 103,  77],
                                        [24, 36, 55, 64,  81, 104, 113,  92],
                                        [49, 64, 78, 87, 103, 121, 120, 101],
                                        [72, 92, 95, 98, 112, 100, 103,  99]
                                      ],
                                      dtype = np.float64)
class YCOCGR_Image(object):
    def __init__(self, raw_image):
        padded_image = resize_image(raw_image)
        f32_image = to_f32(padded_image)
        image = rgb2ycocgr(f32_image)
        self.height, self.width = image.shape[:2]
        self.channels = [
                         split_image_into_8x8_blocks(image[:,:,0]),
                         split_image_into_8x8_blocks(image[:,:,1]),
                         split_image_into_8x8_blocks(image[:,:,2]),
                        ]

def stitch_8x8_blocks_back_together(Nc, block_segments):
    image_rows = []
    temp = []
    for i in range(len(block_segments)):
        if i > 0 and not(i % int(Nc / 8)):
            image_rows.append(temp)
            temp = [block_segments[i]]
        else:
            temp.append(block_segments[i])
    image_rows.append(temp)

    return np.block(image_rows)

def split_image_into_8x8_blocks(image):
    blocks = []
    for vert_slice in np.vsplit(image, int(image.shape[0] / 8)):
        for horiz_slice in np.hsplit(vert_slice, int(image.shape[1] / 8)):
            blocks.append(horiz_slice)
    return blocks

def resize_image(image):
    height, width   = image.shape[:2]
    while(height % 8): height += 1 # Rows
    while(width  % 8): width  += 1 # Cols
    valid_dim = (width, height)
    padded_image = cv2.resize(image, valid_dim)
    return padded_image

def to_f32(image):
    return np.float32(image)

def rgb2ycocgr(image):
    MATRIX_RGB_TO_YCOCGR = np.array(
        [
            [1 / 4, 1 / 2, 1 / 4],
            [1, 0, -1],
            [-1 / 2, 1, -1 / 2],
        ]
    )
    return vector_dot(MATRIX_RGB_TO_YCOCGR, image)
    #return np.einsum("...ij,...j->...i", np.asarray(list(MATRIX_RGB_TO_YCOCGR), np.float32), np.asarray(list(im), np.float32))

def ycocgr2rgb(image):
    MATRIX_YCOCGR_TO_RGB = np.array(
        [
            [1, 1 / 2, -1 / 2],
            [1, 0, 1/2],
            [1, -1 / 2, -1 / 2],
        ]
    )
    return vector_dot(MATRIX_YCOCGR_TO_RGB, image)
    #return np.einsum("...ij,...j->...i", np.asarray(list(MATRIX_YCOCGR_TO_RGB), np.float32), np.asarray(list(im), np.float32))

# Extra colorspace conversions used for testing

def rgb2ycocgcs(image):
    return cs.RGB_to_YCoCg(image)

def ycocg2rgbcs(image):
    return cs.YCoCg_to_RGB(image)

def rgb2ycbcr(image):
    xform = np.array([[.299, .587, .114], [-.1687, -.3313, .5], [.5, -.4187, -.0813]])
    ycbcr = image.dot(xform.T)
    ycbcr[:,:,[1,2]] += 128
    return np.float64(ycbcr)

def ycbcr2rgb(image):
    xform = np.array([[1, 0, 1.402], [1, -0.34414, -.71414], [1, 1.772, 0]])
    rgb = image.astype(np.float64)
    rgb[:,:,[1,2]] -= 128
    rgb = rgb.dot(xform.T)
    np.putmask(rgb, rgb > 255, 255)
    np.putmask(rgb, rgb < 0, 0)
    return np.float64(rgb)

#cv2.cvtColor(stego_image, cv2.COLOR_YCR_CB2BGR)