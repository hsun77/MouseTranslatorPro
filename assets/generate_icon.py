from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main() -> None:
    out = Path(__file__).resolve().parent / "icon.ico"
    image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((16, 16, 240, 240), radius=48, fill=(0, 120, 135, 255))
    try:
        font = ImageFont.truetype("msyh.ttc", 112)
    except OSError:
        font = ImageFont.load_default()
    text = "译"
    bbox = draw.textbbox((0, 0), text, font=font)
    x = (256 - (bbox[2] - bbox[0])) / 2
    y = (256 - (bbox[3] - bbox[1])) / 2 - 8
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    image.save(out, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(out)


if __name__ == "__main__":
    main()
