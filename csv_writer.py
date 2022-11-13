import os.path
import csv

def write(file, row):
  fieldnames = ['image', 'image_resolution', 'message_length', 'final_message_length', 'psnr', 'ssim', 'mse', 'maximum_embeddable_bits', 'bits_per_pixel', 'total_percent_embedded', 'potential_percent_embedded', 'execution_time']
  file_exists = os.path.isfile(file)

  with open(file, 'a', encoding='UTF8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)

    if not file_exists:
            writer.writeheader()

    writer.writerow(row)