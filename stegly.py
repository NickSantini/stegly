import argparse
import cv2
import bitstring
import sys
from pathlib import Path
import time
import sewar.full_ref


# Compression
import lzma

# ChaCha20 encryption
from base64 import b64encode
from base64 import b64decode
from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes

import metrics
import csv_writer as csv
import standard_dct as std_dct
import picky_dct
import multi_bit_dct

start_time = time.time()
ALGORITHM_CHOCIES = ['dct', 'cdct', 'edct', 'picky', 'mbdct']
ACTION_CHOCIES    = ['embed', 'extract']

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input_image", required=True)
parser.add_argument("-s", "--secret_message")
parser.add_argument("-t", "--type", required=True, choices=ALGORITHM_CHOCIES, type=str.lower)
parser.add_argument("-a", "--action", required=True, choices=ACTION_CHOCIES, type=str.lower)
parser.add_argument("-k", "--key", required=False)
parser.add_argument("-n", "--nonce", required=False)
args = parser.parse_args()

key   = None if args.key is None else b64decode(args.key)
nonce = None if args.nonce is None else b64decode(args.nonce)
encrypt_message = None
image_path = Path(args.input_image)

if args.action == 'embed':
  SECRET_MESSAGE_STRING = args.secret_message
  COVER_IMAGE_FILEPATH = str(image_path)
  STEGO_IMAGE_FILEPATH = str(image_path.with_name(image_path.stem + '_' + args.type + image_path.suffix))
  CSV_PATH       = str(image_path.with_name(args.type + '_metrics' + '.csv'))
  IMAGE_NAME     = str(image_path.name)
  print('Embedding: ' + IMAGE_NAME)
else:
  STEGO_IMAGE_FILEPATH = str(image_path)
  COVER_IMAGE_FILEPATH = str(image_path)

def to_utf8(message):
  try:
    utf_message = message.decode('utf-8')
  except:
      return('error')
  else:
    return(utf_message)

def compressed_message_as_bits():
  message_as_bytes = SECRET_MESSAGE_STRING.encode('utf-8')
  compressed_message = lzma.compress(message_as_bytes)
  return(message_as_bits(compressed_message))

def message_as_bits(message):
  encoded_bits = ''
  if not isinstance(message, bytes):
    message = message.encode('utf-8')

  for char in message: encoded_bits += bitstring.pack('uint:8', char)
  encoded_data_len = bitstring.pack('uint:16', len(encoded_bits)) 
  encoded_bits = encoded_data_len + encoded_bits
  metrics.final_message_length = len(encoded_bits)
  return encoded_bits

def compressed_std_dct_embed(image_path=COVER_IMAGE_FILEPATH):
  raw_cover_image = cv2.imread(image_path, flags=cv2.IMREAD_COLOR)
  compressed_message = compressed_message_as_bits()
  embedded_image = std_dct.embed(raw_cover_image, compressed_message)
  cv2.imwrite(STEGO_IMAGE_FILEPATH, embedded_image)

def compressed_std_dct_extract():
  embedded_image = cv2.imread(STEGO_IMAGE_FILEPATH, flags=cv2.IMREAD_COLOR)
  compressed_message = std_dct.extract(embedded_image)
  try:
    message = lzma.decompress(compressed_message)
  except:
    return ('decompress error')
  return(to_utf8(message))

def encrypted_message_as_bits():
  global key, nonce
  message_as_bytes = SECRET_MESSAGE_STRING.encode('utf-8')
  key = get_random_bytes(32)
  cipher = ChaCha20.new(key=key)
  ciphertext = cipher.encrypt(message_as_bytes)
  nonce = cipher.nonce
  encrypted_message = b64encode(ciphertext).decode('utf-8')
  print('Securely save nonce and key to de-code hidden message')
  print('nonce: ', b64encode(nonce).decode('utf-8'))
  print('key: ', b64encode(key).decode('utf-8'))
  return(message_as_bits(encrypted_message))

def encrypt_std_dct_embed(image_path=COVER_IMAGE_FILEPATH):
  global encrypt_message
  raw_cover_image = cv2.imread(image_path, flags=cv2.IMREAD_COLOR)
  encrypt_message = encrypted_message_as_bits() if encrypt_message is None else encrypt_message
  embedded_image = std_dct.embed(raw_cover_image, encrypt_message)
  cv2.imwrite(STEGO_IMAGE_FILEPATH, embedded_image)

def encrypt_std_dct_extract():
  global key, nonce
  if key == None or nonce == None: sys.exit('Missing key or nonce')
  decrypted_message = ''
  embedded_image = cv2.imread(STEGO_IMAGE_FILEPATH, flags=cv2.IMREAD_COLOR)
  message = std_dct.extract(embedded_image)
  try:
    cipher = ChaCha20.new(key=key, nonce=nonce)
    decrypted_message = cipher.decrypt(message)
  except: 
    (ValueError, KeyError)
  return(to_utf8(decrypted_message))

def picky_dct_embed(image_path=COVER_IMAGE_FILEPATH):
  message = message_as_bits(SECRET_MESSAGE_STRING)
  raw_cover_image = cv2.imread(image_path, flags=cv2.IMREAD_COLOR)
  embedded_image = picky_dct.embed(raw_cover_image, message)
  cv2.imwrite(STEGO_IMAGE_FILEPATH, embedded_image)

def picky_dct_extract():
  embedded_image = cv2.imread(STEGO_IMAGE_FILEPATH, flags=cv2.IMREAD_COLOR)
  message = picky_dct.extract(embedded_image)
  return(to_utf8(message))

def multi_bit_dct_embed(image_path=COVER_IMAGE_FILEPATH):
  message = message_as_bits(SECRET_MESSAGE_STRING)
  raw_cover_image = cv2.imread(image_path, flags=cv2.IMREAD_COLOR)
  embedded_image = multi_bit_dct.embed(raw_cover_image, message)
  cv2.imwrite(STEGO_IMAGE_FILEPATH, embedded_image)

def multi_bit_dct_extract():
  embedded_image = cv2.imread(STEGO_IMAGE_FILEPATH, flags=cv2.IMREAD_COLOR)
  message = multi_bit_dct.extract(embedded_image)
  return(to_utf8(message))

def standard_dct_embed(image_path=COVER_IMAGE_FILEPATH):
  message=message_as_bits(SECRET_MESSAGE_STRING)
  raw_cover_image = cv2.imread(str(image_path), flags=cv2.IMREAD_COLOR)
  embedded_image = std_dct.embed(raw_cover_image, message)
  cv2.imwrite(STEGO_IMAGE_FILEPATH, embedded_image)

def standard_dct_extract():
  embedded_image = cv2.imread(STEGO_IMAGE_FILEPATH, flags=cv2.IMREAD_COLOR)
  message = std_dct.extract(embedded_image)
  return(to_utf8(message)) 

def error_detected():
  if method_dictionary[f'{args.type}_extract']() == SECRET_MESSAGE_STRING:
    return False
  else:
    return True

method_dictionary = {
    'dct_embed':     standard_dct_embed,
    'dct_extract':   standard_dct_extract,
    'cdct_embed':    compressed_std_dct_embed,
    'cdct_extract':  compressed_std_dct_extract,
    'edct_embed':    encrypt_std_dct_embed,
    'edct_extract':  encrypt_std_dct_extract,
    'picky_embed':   picky_dct_embed,
    'picky_extract': picky_dct_extract,
    'mbdct_embed':   multi_bit_dct_embed,
    'mbdct_extract': multi_bit_dct_extract,
}

results = method_dictionary[f'{args.type}_{args.action}']()

if args.action == 'embed':
  for i in range (10):
    if error_detected():
      method_dictionary[f'{args.type}_embed'](STEGO_IMAGE_FILEPATH)
    else:
      print('Message succesfully embedded')
      break

  img1 = cv2.imread(COVER_IMAGE_FILEPATH, flags=cv2.IMREAD_COLOR)
  img2 = cv2.imread(STEGO_IMAGE_FILEPATH, flags=cv2.IMREAD_COLOR)
  
  metrics.height = img2.shape[0] 
  metrics.width = img2.shape[1]
  psnr = sewar.psnr(img1, img2)
  ssim = sewar.ssim(img1, img2)[0]
  qui = sewar.uqi(img1, img2)
  mse = sewar.mse(img1, img2)

  maximum_embeddable_bits    = round(metrics.maximum_embeddable_bits, 8)
  bits_per_pixel             = round(metrics.bits_per_pixel(), 8)
  total_percent_embedded     = round(metrics.total_percent_embedded(), 8) * 100
  potential_percent_embedded = round(metrics.potential_percent_embedded(), 8) * 100
  execution_time             = round(time.time() - start_time, 2)
  message_length             = len(SECRET_MESSAGE_STRING.encode('utf-8')* 8)
  final_message_length       = metrics.final_message_length
  image_resolution           = str(metrics.width) + 'x' + str(metrics.height)
 
  print('Image: ', IMAGE_NAME)
  print('Resolution: ', image_resolution)
  print('Message_length: ', message_length )
  print('Final Message Length: ', final_message_length)
  print('PSNR: ', psnr)
  print('SSIM: ', ssim)
  print('Maximum embeddable bits: ',   maximum_embeddable_bits)
  print('Percent of image embedded: ', total_percent_embedded)
  print('Potential percent embbed: ',  potential_percent_embedded)
  print('Bits per pixel: ', bits_per_pixel)
  print("Execution time: ", execution_time)

  csv.write(CSV_PATH,
  { 'image': IMAGE_NAME,
    'psnr':  psnr,
    'ssim':  ssim,
    'mse': mse,
    'bits_per_pixel':   bits_per_pixel,
    'execution_time':   execution_time,
    'image_resolution': image_resolution,
    'message_length':   message_length ,
    'final_message_length': final_message_length,
    'maximum_embeddable_bits':    maximum_embeddable_bits,
    'total_percent_embedded':     total_percent_embedded,
    'potential_percent_embedded': potential_percent_embedded })
else:
  print('Secret Message: ', results )