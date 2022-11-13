import cv2
import struct
import bitstring
import numpy  as np
import metrics
import image_tools as img

NUM_CHANNELS = 3

def embed(image, message):
  stego_image = np.empty_like(img.to_f32(image))
  ycocgr_image = img.YCOCGR_Image(image)

  for chan_index in range(NUM_CHANNELS):
      # FORWARD DCT STAGE
      dct_blocks = [cv2.dct(block) for block in ycocgr_image.channels[chan_index]]
      dct_quants = [np.around(np.divide(item, img.JPEG_STD_LUM_QUANT_TABLE)).flatten() for item in dct_blocks]
      
      # DATA INSERTION STAGE
      # Embed data in Luminance layer
      if (chan_index == 0):
          embedded_dct_blocks   = embed_encoded_data_into_DCT(dct_quants, message)
          desorted_coefficients = [block.reshape(8,8) for block in embedded_dct_blocks]
      else:
          desorted_coefficients = [block.reshape(8,8) for block in dct_quants]

      # DEQUANTIZATION STAGE
      dct_quants = [np.multiply(data, img.JPEG_STD_LUM_QUANT_TABLE) for data in desorted_coefficients]

      # Inverse DCT Stage
      idct_blocks = [cv2.idct(block) for block in dct_quants]

      # Rebuild full image channel
      stego_image[:,:,chan_index] = np.asarray(img.stitch_8x8_blocks_back_together(ycocgr_image.width, idct_blocks))

  stego_image_rgb = img.ycocgr2rgb(stego_image)
  return np.uint8(np.clip(stego_image_rgb, 0, 255))

def embed_encoded_data_into_DCT(dct_blocks, message):
    data_complete = False; message.pos = 0
    metrics.maximum_embeddable_bits = 0
    converted_blocks = []

    for index, current_dct_block in enumerate(dct_blocks):
        for i in range(1, len(current_dct_block)):
            curr_coeff = np.int32(current_dct_block[i])
            if (curr_coeff >= 4):
                metrics.maximum_embeddable_bits +=2
                if (message.pos == (len(message))): data_complete = True; continue
                curr_coeff = np.uint8(current_dct_block[i])
                pack_coeff = bitstring.pack('uint:8', curr_coeff)
                pack_coeff[-2] = message.read(1)
                if not message.pos == (len(message)):
                    pack_coeff[-1] = message.read(1)
                current_dct_block[i] = np.float32(pack_coeff.read('uint:8'))
            elif(curr_coeff > 1 & curr_coeff < 4):
                metrics.maximum_embeddable_bits +=1
                if (message.pos == (len(message))): data_complete = True; continue
                curr_coeff = np.uint8(current_dct_block[i])
                pack_coeff = bitstring.pack('uint:8', curr_coeff)
                pack_coeff[-1] = message.read(1)
                current_dct_block[i] = np.float32(pack_coeff.read('uint:8'))
        converted_blocks.append(current_dct_block)

    if not(data_complete): raise ValueError("Data didn't fully embed into cover image!")
    return converted_blocks


def extract(image):
    stego_image_ycocgr = img.YCOCGR_Image(image)

    # FORWARD DCT STAGE
    dct_blocks = [cv2.dct(block) for block in stego_image_ycocgr .channels[0]]  # Only care about Luminance layer

    # QUANTIZATION STAGE
    dct_quants = [np.around(np.divide(item, img.JPEG_STD_LUM_QUANT_TABLE)).flatten() for item in dct_blocks]

    # Sort DCT coefficients by frequency
    sorted_coefficients = dct_quants

    # DATA EXTRACTION STAGE
    recovered_data = extract_encoded_data_from_DCT(sorted_coefficients)

    data_len = int(recovered_data.read('uint:16')/8)

    # Extract secret message from DCT coefficients
    extracted_data = bytes()

    try:
        for _ in range(data_len): extracted_data += struct.pack('>B', recovered_data.read('uint:8'))
    except:
        return('error')
    else:
        return(extracted_data)

def extract_encoded_data_from_DCT(dct_blocks):
    extracted_data = ""
    for index, current_dct_block in enumerate(dct_blocks):
        for i in range(1, len(current_dct_block)):
            curr_coeff = np.int32(current_dct_block[i])
            if (curr_coeff >= 4):
                extracted_data += bitstring.pack('uint:2', np.uint8(current_dct_block[i]) & 0x03)
            elif(curr_coeff > 1 & curr_coeff < 4):
                extracted_data += bitstring.pack('uint:1', np.uint8(current_dct_block[i]) & 0x01)
    return extracted_data
