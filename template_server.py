from PIL import Image, ImageDraw, ImageFont
import qrcode


def make_image_square(image, size):
    # Get the dimensions of the original image
    original_width, original_height = image.size
    
    # Calculate the necessary padding to make the image square
    if original_width > original_height:
        new_size = (original_width, original_width)
    else:
        new_size = (original_height, original_height)

    # Create a new square image with a white background
    square_image = Image.new("RGBA", new_size, (255, 255, 255, 0))

    # Calculate the position to paste the original image in the center of the square
    paste_position = ((new_size[0] - original_width) // 2, (new_size[1] - original_height) // 2)

    # Paste the original image onto the square background
    square_image.paste(image, paste_position)

    # Resize the square image to the desired size
    square_image = square_image.resize((size, size))

    return square_image

# Function to add a logo and QR code to the base image
def insert_logo_qrcode(base_image_path, logo_path, output_image_path, qr_image_path, qr_position, logo_position):
    # Open the base image (the one with placeholders)
    base_image = Image.open(base_image_path)

    # Open the logo image
    logo = Image.open(logo_path)

    # Ensure the logo has an alpha channel (transparency)
    if logo.mode != 'RGBA':
        logo = logo.convert("RGBA")

    # Generate the QR code
    qr_code_img = Image.open(qr_image_path)

    # Resize the logo and make it square
    logo_size = 350  # Adjust the size according to the placeholder
    logo = make_image_square(logo, logo_size)

    # Resize the QR code if necessary
    qr_code_size = (400, 400)  # Adjust the size according to the placeholder
    qr_code_img = qr_code_img.resize(qr_code_size)

    # Paste the logo at the desired position (coordinates need adjustment based on your image)
    base_image.paste(logo, logo_position, logo)

    # Paste the QR code at the desired position (coordinates need adjustment based on your image)
    base_image.paste(qr_code_img, qr_position)

    # Save the resulting image
    base_image.save(output_image_path)

# Example usage
base_image_path = 'images/Template of MOM AI Restaurant QR-Code.png'  # Replace with your image path
logo_path = 'images/BiryaniLogo.jpeg'  # Replace with the logo image path
output_image_path = 'result.png'  # Output path to save the image
qr_image_path = "images/QR-Code.png"  # Replace with your QR code data

# Define the positions for the logo and QR code
qr_position = (600, 600)  # Adjust based on where you want to place the QR code
logo_position = (320, 59)  # Adjust based on where you want to place the logo

# Call the function to insert the logo and QR code
insert_logo_qrcode(base_image_path, logo_path, output_image_path, qr_image_path, qr_position, logo_position)

print("Image created successfully!")
