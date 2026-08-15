import base64
import io
import random
import string
from django.core.signing import TimestampSigner
from PIL import Image, ImageDraw, ImageFont

# Use Django's signer for stateless signed tokens
signer = TimestampSigner()


def generate_captcha(length=5, width=150, height=50, font_size=25):
    # Generate random text
    text = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    # Create blank image with white background
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Load default font or a truetype font if available    
    font = ImageFont.load_default(size=font_size)

    # Compute text size and position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (width - text_width) / 2
    y = (height - text_height) / 2

    # Draw text with random colors per character
    for i, char in enumerate(text):
        char_x = x + i * (text_width / length)
        char_y = y + random.randint(-5, 5)  # slight vertical jitter
        color = tuple(random.randint(0, 150) for _ in range(3))  # darker colors
        draw.text((char_x, char_y), char, font=font, fill=color)

    # Add random lines for noise
    for _ in range(8):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        line_color = tuple(random.randint(0, 255) for _ in range(3))
        draw.line(((x1, y1), (x2, y2)), fill=line_color, width=1)

    # Add random dots for noise
    for _ in range(100):
        dot_x, dot_y = random.randint(0, width), random.randint(0, height)
        dot_color = tuple(random.randint(0, 255) for _ in range(3))
        draw.point((dot_x, dot_y), fill=dot_color)

    # Save image to base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    img_data_uri = f"data:image/png;base64,{img_str}"

    # Hash the solution for validation
    # token = hashlib.sha256(text.encode()).hexdigest()
    token = signer.sign(text.lower())

    return {"image_base64": img_data_uri, "token": token}



