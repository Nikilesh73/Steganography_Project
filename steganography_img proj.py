import cv2
import numpy as np
import sys
import textwrap
import maskpass 

def text_to_binary(text):
    """Convert text to a binary string."""
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary_string):
    """Convert binary string back to readable text."""
    chars = [binary_string[i:i+8] for i in range(0, len(binary_string), 8)]
    return ''.join(chr(int(char, 2)) for char in chars)

def ensure_png_extension(filename):
    """Ensure the filename has a .png extension."""
    return filename if filename.lower().endswith(".png") else filename + ".png"

def encode_message():
    image_path = input("Enter the image file path (Use PNG for best results): ")
    img = cv2.imread(image_path)

    if img is None:
        print("Error: Image not found.")
        sys.exit()

    msg = maskpass.advpass("Enter secret message: ", mask="*")
    password = maskpass.advpass("Enter a passcode: ", mask="*")

    output_filename = input("Enter a filename to save the encrypted image: ")
    output_filename = ensure_png_extension(output_filename)

    full_msg = password + "<PASS>" + msg + "<END>"
    binary_msg = text_to_binary(full_msg)
    
    msg_index = 0
    height, width, _ = img.shape

    if len(binary_msg) > height * width * 3:
        print("Error: Message is too large to fit in the image.")
        sys.exit()

    for row in range(height):
        for col in range(width):
            for channel in range(3):
                if msg_index < len(binary_msg):
                    img[row, col, channel] = (img[row, col, channel] & ~1) | int(binary_msg[msg_index])
                    msg_index += 1
                else:
                    break
            if msg_index >= len(binary_msg):
                break
        if msg_index >= len(binary_msg):
            break

    cv2.imwrite(output_filename, img)
    print(f" Message encoded successfully! Saved as {output_filename}")

def decode_message():
    image_path = input("Enter the encrypted image file path: ")
    img = cv2.imread(image_path)

    if img is None:
        print("Error: Image not found.")
        sys.exit()

    entered_password = maskpass.advpass("Enter the passcode for decryption: ", mask="*")

    output_filename = input("Enter a filename to save the decrypted image: ")
    output_filename = ensure_png_extension(output_filename)

    binary_data = ""
    height, width, _ = img.shape

    for row in range(height):
        for col in range(width):
            for channel in range(3):
                binary_data += str(img[row, col, channel] & 1)
                if len(binary_data) % 8 == 0 and "<END>" in binary_to_text(binary_data):
                    break
            if "<END>" in binary_to_text(binary_data):
                break
        if "<END>" in binary_to_text(binary_data):
            break

    extracted_text = binary_to_text(binary_data)

    if "<PASS>" in extracted_text and "<END>" in extracted_text:
        stored_password, message = extracted_text.split("<PASS>", 1)
        message = message.replace("<END>", "")

        if stored_password == entered_password:
            print("\n Decryption successful! Message is now written on the decrypted image.")

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = min(width, height) / 700  
            text_color = (0, 255, 0)  
            thickness = 2
            x, y = 50, 100  

            max_chars_per_line = int(width / (font_scale * 20))  
            wrapped_text = textwrap.wrap(message, width=max_chars_per_line)

            for line in wrapped_text:
                cv2.putText(img, line, (x, y), font, font_scale, text_color, thickness, cv2.LINE_AA)
                y += int(40 * font_scale)  

            cv2.imwrite(output_filename, img)  # Saving the decrypted image with message
            print(f" Decrypted image saved as {output_filename}")
        else:
            print("\n Authentication failed! Incorrect passcode.")
    else:
        print("\n  Failed to extract a valid message. Please ensure the correct image is used.")

print("\nChoose an option:")
print("1️ Encode a message")
print("2️ Decode a message")
choice = input("Enter 1 or 2: ")

if choice == "1":
    encode_message()
elif choice == "2":
    decode_message()
else:
    print(" Invalid option selected!")
