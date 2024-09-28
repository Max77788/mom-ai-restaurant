from PIL import Image, ImageDraw, ImageFont
import qrcode


# Function to add a logo and QR code to the base image
def serve_qrcode_template(base_image_path, output_image_path, qr_image_path, qr_position):
    # Open the base image (the one with placeholders)
    base_image = Image.open(base_image_path)

    qr_code_img = Image.open(qr_image_path)

    # Resize the QR code if necessary
    qr_code_size = (500, 500)  # Adjust the size according to the placeholder
    qr_code_img = qr_code_img.resize(qr_code_size)

    # Paste the QR code at the desired position (coordinates need adjustment based on your image)
    base_image.paste(qr_code_img, (450, 310))

    # Save the resulting image
    base_image.save(output_image_path)

# Example usage
base_image_path = 'static/images/QR-Code-Template.jpg'  # Replace with your image path
output_image_path = 'result.png'  # Output path to save the image
qr_image_path = "static/images/random-qr-code.jpeg"  # Replace with your QR code data

# Call the function to insert the logo and QR code
serve_qrcode_template(base_image_path, output_image_path, qr_image_path)

print("Image created successfully!")
