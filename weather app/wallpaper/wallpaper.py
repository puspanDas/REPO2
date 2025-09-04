from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
from sklearn.tree import DecisionTreeClassifier
import io
import random

app = Flask(__name__)

# Simple prediction model: mood → theme
X = [[0], [1], [2]]  # 0 = calm, 1 = energetic, 2 = focused
y = ['blue', 'orange', 'green']
model = DecisionTreeClassifier()
model.fit(X, y)

# Theme color mapping
color_map = {
    'blue': (30, 60, 200),
    'orange': (255, 140, 0),
    'green': (0, 180, 100)
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        mood = int(request.form.get('mood', 0))
        theme = model.predict([[mood]])[0]
        bg_color = color_map.get(theme, (50, 50, 50))

        # Create wallpaper
        WIDTH, HEIGHT = 1920, 1080
        img = Image.new('RGB', (WIDTH, HEIGHT), bg_color)
        draw = ImageDraw.Draw(img)

        # Load font
        try:
            font = ImageFont.truetype("arial.ttf", 100)
        except:
            font = ImageFont.load_default()

        # Text content
        text = f"Theme: {theme.capitalize()}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (WIDTH - text_width) // 2
        y = (HEIGHT - text_height) // 2
        draw.text((x, y), text, fill=(255, 255, 255), font=font)

        # Add random circles
        for _ in range(50):
            radius = random.randint(20, 100)
            cx = random.randint(0, WIDTH)
            cy = random.randint(0, HEIGHT)
            color = tuple(random.randint(100, 255) for _ in range(3))
            draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=color)

        # Return image
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')

    return render_template('index.html')
