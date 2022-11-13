# Stegly
Stegly was created to study DCT steganography embedding and extraction techniques. It currently supports 5 DCT embedding methods; standard, encrypted, compressed, picky and more bits.

#### Standard DCT
&nbsp;&nbsp;&nbsp;&nbsp; Utilizes embedding in the LSB of the DCT coefficients

#### Encrypted DCT
&nbsp;&nbsp;&nbsp;&nbsp; Uses standard DCT but with data encrypted in ChaCha20

#### Compressed DCT
&nbsp;&nbsp;&nbsp;&nbsp; Uses standard DCT but with data compressed with LZMA

#### Picky DCT
&nbsp;&nbsp;&nbsp;&nbsp; Embeds in higher frequency data by only utilizing DCT coefficients after the 24th coefficient in a DCT block

#### More Bits DCT
&nbsp;&nbsp;&nbsp;&nbsp; Instead of using the LSB, it uses the two least significant bits. Only when the coefficient is greater or equal to 4, or else it uses the LSB.

## Setup

* Python3
* Install requirments.txt

## Usage

#### Required Arguments
##### Action
&nbsp;&nbsp;&nbsp;&nbsp;The type of operation to be completed

&nbsp;&nbsp;&nbsp;&nbsp; requires one of the following params [ embed, extract]

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; --action, -a
 

##### Type 
&nbsp;&nbsp;&nbsp;&nbsp; The algorithm to be used while either embedding or extracting.

&nbsp;&nbsp;&nbsp;&nbsp; Note: extraction completed with edct requires two additional parameters; key and nonce. 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; -—type, -t  

&nbsp;&nbsp;&nbsp;&nbsp; requires one of the following params [ dct, cdct, edct, mbdct, picky ]
##### Image
&nbsp;&nbsp;&nbsp;&nbsp; The image path

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; —input_image, -i

##### Secret Message
&nbsp;&nbsp;&nbsp;&nbsp; Note: messages with spaces must be encapsulated with quotes

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; —secret_message, -s

#### Optional Arguments
  ##### Key:
  &nbsp;&nbsp;&nbsp;&nbsp; Used during extraction of encrypted messages
  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; —key, k
##### Nonce:
  &nbsp;&nbsp;&nbsp;&nbsp; Used during extraction of encrypted messages
  
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; —nonce, n
#### Example Usage
	stegly.py -a embed -t dct -i ./test_image.png -s “this is a message”

batch_stegly is included to run the script on a folder of images to aid in testing algorithms on a larger amount of images. Its usage is similar to Stegly but it is for embedding only and instead of an image it takes -d for a directory. 
#### Batch Example Usage
 	batch_stegly.py -t dct -s -d ./this_is_a_directory
  
  
Stegly currently only supports PNG image types. BMP images are untested but should also work. 

