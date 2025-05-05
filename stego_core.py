from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import wave
import cv2
import numpy as np
import base64

# AES Encryption/Decryption 
def aes_encrypt(message, key):
    cipher = AES.new(pad(key, AES.block_size), AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
    return base64.b64encode(cipher.iv + ct_bytes).decode()

def aes_decrypt(ciphertext, key):
    raw = base64.b64decode(ciphertext)
    iv = raw[:16]
    ct = raw[16:]
    cipher = AES.new(pad(key, AES.block_size), AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size).decode()

# Image Steganography 
def embed_in_image(image_path, message, output_path, key):
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    encoded = image.copy()
    width, height = image.size
    encrypted_message = aes_encrypt(message, key)
    binary_message = ''.join([format(ord(char), '08b') for char in encrypted_message]) + '1111111111111110'

    data_index = 0
    for y in range(height):
        for x in range(width):
            if data_index < len(binary_message):
                r, g, b = image.getpixel((x, y))
                r = (r & ~1) | int(binary_message[data_index])
                data_index += 1
                if data_index < len(binary_message):
                    g = (g & ~1) | int(binary_message[data_index])
                    data_index += 1
                if data_index < len(binary_message):
                    b = (b & ~1) | int(binary_message[data_index])
                    data_index += 1
                encoded.putpixel((x, y), (r, g, b))
            else:
                break
    encoded.save(output_path)

def extract_from_image(image_path, key):
    image = Image.open(image_path)
    binary_data = ''
    for y in range(image.height):
        for x in range(image.width):
            r, g, b = image.getpixel((x, y))
            binary_data += str(r & 1) + str(g & 1) + str(b & 1)

    all_bytes = [binary_data[i:i + 8] for i in range(0, len(binary_data), 8)]
    decoded_data = ""
    for byte in all_bytes:
        if byte == '11111110':
            break
        decoded_data += chr(int(byte, 2))
    return aes_decrypt(decoded_data, key)

#  Audio Steganography
def embed_in_audio(audio_path, message, output_path, key):
    audio = wave.open(audio_path, mode='rb')
    frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
    encrypted_message = aes_encrypt(message, key)
    encrypted_message += '###END'
    bits = ''.join([format(ord(i), '08b') for i in encrypted_message])
    
    if len(bits) > len(frame_bytes):
        raise ValueError("Message too long to hide in audio file.")

    for i in range(len(bits)):
        frame_bytes[i] = (frame_bytes[i] & 254) | int(bits[i])
    
    modified_audio = wave.open(output_path, 'wb')
    modified_audio.setparams(audio.getparams())
    modified_audio.writeframes(bytes(frame_bytes))
    modified_audio.close()
    audio.close()

def extract_from_audio(audio_path, key):
    audio = wave.open(audio_path, mode='rb')
    frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
    extracted = [str(frame_bytes[i] & 1) for i in range(len(frame_bytes))]
    decoded_message = ""
    for i in range(0, len(extracted), 8):
        byte = extracted[i:i+8]
        char = chr(int(''.join(byte), 2))
        decoded_message += char
        if decoded_message.endswith('###END'):
            break
    return aes_decrypt(decoded_message[:-6], key)

#  Text Steganography
def encode_text_stego(text_path, message, output_path, key):
    with open(text_path, 'r') as file:
        content = file.read()
    encrypted = aes_encrypt(message, key)
    binary = ''.join(format(ord(i), '08b') for i in encrypted) + '11111110'
    
    if len(binary) > len(content):
        raise ValueError("Message too large to encode in text.")

    encoded = ''
    for i in range(len(content)):
        encoded += content[i]
        if i < len(binary):
            if binary[i] == '1':
                encoded += ' '
    
    with open(output_path, 'w') as out:
        out.write(encoded)

def decode_text_stego(text_path, key):
    with open(text_path, 'r') as file:
        content = file.read()
    binary = ''
    i = 0
    while i < len(content):
        if content[i] == ' ':
            binary += '1'
            i += 2
        else:
            binary += '0'
            i += 1

    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    message = ''
    for ch in chars:
        if ch == '11111110':
            break
        message += chr(int(ch, 2))
    return aes_decrypt(message, key)

#  Video Steganography 
def embed_in_video(video_path, message, frame_number, output_path, key):
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS),
                          (int(cap.get(3)), int(cap.get(4))))
    count = 0
    encrypted = aes_encrypt(message, key)
    binary_message = ''.join([format(ord(i), '08b') for i in encrypted]) + '11111110'
    data_index = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if count == frame_number:
            for i in range(frame.shape[0]):
                for j in range(frame.shape[1]):
                    for k in range(3):
                        if data_index < len(binary_message):
                            frame[i, j, k] = (frame[i, j, k] & ~1) | int(binary_message[data_index])
                            data_index += 1
            out.write(frame)
        else:
            out.write(frame)
        count += 1

    cap.release()
    out.release()

def extract_from_video(video_path, frame_number, key):
    cap = cv2.VideoCapture(video_path)
    count = 0
    binary_data = ''
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if count == frame_number:
            for i in range(frame.shape[0]):
                for j in range(frame.shape[1]):
                    for k in range(3):
                        binary_data += str(frame[i, j, k] & 1)
            break
        count += 1

    cap.release()
    all_bytes = [binary_data[i:i + 8] for i in range(0, len(binary_data), 8)]
    decoded_data = ""
    for byte in all_bytes:
        if byte == '11111110':
            break
        decoded_data += chr(int(byte, 2))
    return aes_decrypt(decoded_data, key)

