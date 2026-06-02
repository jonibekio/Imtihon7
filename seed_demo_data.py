import os
from decimal import Decimal
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.conf import settings
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

from categories.models import Category
from products.models import Product, ProductImage, Status


COLORS = [
    ("#0f766e", "#e6fffb"),
    ("#172033", "#eef2ff"),
    ("#9f1239", "#fff1f2"),
    ("#166534", "#f0fdf4"),
    ("#854d0e", "#fffbeb"),
    ("#1d4ed8", "#eff6ff"),
    ("#6d28d9", "#f5f3ff"),
    ("#be123c", "#fff1f2"),
]

CATEGORIES = [
    ("Smartfonlar", "smartfonlar"),
    ("Laptoplar", "laptoplar"),
    ("Audio", "audio"),
    ("Aksessuarlar", "aksessuarlar"),
    ("Uy texnikasi", "uy-texnikasi"),
    ("Sport", "sport"),
    ("Kiyim", "kiyim"),
    ("Kitoblar", "kitoblar"),
]

PRODUCTS = [
    ("iPhone 15 Pro 256GB", "smartfonlar", "Titanium korpusli, kuchli kamera va tezkor chipga ega premium smartfon.", "15190000", "14490000", 14),
    ("Samsung Galaxy S24", "smartfonlar", "Yorqin AMOLED ekran, tezkor ishlash va kundalik foydalanish uchun ishonchli telefon.", "10990000", "9990000", 21),
    ("Xiaomi Redmi Note 13", "smartfonlar", "Katta ekran, yaxshi batareya va qulay narxdagi zamonaviy smartfon.", "3290000", "2990000", 35),
    ("Google Pixel 8", "smartfonlar", "Toza Android tajribasi va kuchli kamera algoritmlari bilan smartfon.", "8490000", None, 10),
    ("MacBook Air M2 13", "laptoplar", "Yengil, sokin va kuchli Apple M2 chipli noutbuk.", "13990000", "13290000", 8),
    ("Lenovo ThinkPad E16", "laptoplar", "Ish va o'qish uchun mustahkam klaviatura va barqaror noutbuk.", "8990000", None, 12),
    ("ASUS Vivobook 15", "laptoplar", "Kundalik ishlar, browsing va office uchun yaxshi balansdagi laptop.", "6490000", "6190000", 18),
    ("HP Pavilion x360", "laptoplar", "Sensor ekranli, 2-in-1 formatdagi ixcham va qulay noutbuk.", "7790000", None, 7),
    ("Sony WH-1000XM5", "audio", "Shovqinni pasaytiruvchi premium simsiz quloqchin.", "4490000", "4190000", 11),
    ("AirPods Pro 2", "audio", "ANC, Spatial Audio va Apple ekotizimi uchun qulay quloqchin.", "3290000", None, 20),
    ("JBL Charge 5", "audio", "Kuchli ovoz, suvga chidamlilik va uzoq batareyali portativ kolonka.", "1890000", "1690000", 17),
    ("Anker Soundcore Life Q30", "audio", "Yaxshi bass, ANC va uzoq ishlaydigan batareyali quloqchin.", "990000", None, 26),
    ("Apple Watch Series 9", "aksessuarlar", "Sog'liq monitoringi, sport tracking va qulay bildirishnomalar.", "4990000", "4690000", 9),
    ("Logitech MX Master 3S", "aksessuarlar", "Professional ish uchun jim, aniq va ergonomik sichqoncha.", "1290000", None, 24),
    ("Keychron K2 Keyboard", "aksessuarlar", "Mexanik klaviatura, simsiz rejim va chiroyli minimal dizayn.", "1190000", "1090000", 16),
    ("Baseus 65W Charger", "aksessuarlar", "Telefon va laptop uchun tezkor GaN zaryadlovchi adapter.", "490000", None, 40),
    ("Dyson V8 Vacuum", "uy-texnikasi", "Simsiz changyutgich, uy tozalash uchun yengil va kuchli yechim.", "4590000", "4290000", 6),
    ("Philips Air Fryer XL", "uy-texnikasi", "Kam yog' bilan tez pishirish uchun katta hajmli air fryer.", "2290000", None, 13),
    ("Bosch Blender 1000W", "uy-texnikasi", "Smuzilar, souslar va oshxona tayyorgarligi uchun kuchli blender.", "890000", "790000", 19),
    ("Samsung Microwave 32L", "uy-texnikasi", "Katta hajmli, qulay boshqaruvga ega mikroto'lqinli pech.", "1790000", None, 15),
    ("Nike Pegasus 40", "sport", "Yugurish va kundalik yurish uchun yengil sport oyoq kiyimi.", "1390000", "1240000", 22),
    ("Adidas Training Mat", "sport", "Uy mashqlari va yoga uchun sirpanmaydigan qulay mat.", "390000", None, 31),
    ("Garmin Forerunner 255", "sport", "Yuguruvchilar uchun GPS, puls va mashg'ulot tahliliga ega soat.", "3790000", "3490000", 5),
    ("Dumbbell Set 20kg", "sport", "Uy sharoitida kuch mashqlari uchun sozlanadigan gantel to'plami.", "890000", None, 14),
    ("Oxford Cotton Shirt", "kiyim", "Minimal dizaynli, ish va casual uslubga mos paxta ko'ylak.", "349000", None, 45),
    ("Classic Denim Jacket", "kiyim", "Mavsumiy kiyimlar bilan oson moslashadigan klassik denim kurtka.", "649000", "599000", 18),
    ("Merino Wool Sweater", "kiyim", "Yumshoq, iliq va oddiy ko'rinishdagi merino sviter.", "529000", None, 20),
    ("Clean Code Book", "kitoblar", "Dasturchilar uchun toza kod yozish bo'yicha amaliy qo'llanma.", "290000", "249000", 30),
    ("Atomic Habits", "kitoblar", "Kichik odatlar orqali katta natijalar yaratish haqida bestseller.", "180000", None, 34),
    ("Design of Everyday Things", "kitoblar", "Mahsulot dizayni va foydalanuvchi tajribasini tushunish uchun kitob.", "220000", "199000", 25),
]


def main():
    media_root = Path(settings.MEDIA_ROOT)
    (media_root / "categories").mkdir(parents=True, exist_ok=True)
    (media_root / "products").mkdir(parents=True, exist_ok=True)

    categories = {}
    for index, (name, slug) in enumerate(CATEGORIES):
        image_path = create_image(
            media_root / "categories" / f"demo-{slug}.png",
            name,
            COLORS[index % len(COLORS)],
        )
        category, _ = Category.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "image": f"categories/{image_path.name}",
            },
        )
        categories[slug] = category

    for index, product_data in enumerate(PRODUCTS, start=1):
        title, category_slug, description, price, discount_price, stock = product_data
        slug = slugify(title)
        image_path = create_image(
            media_root / "products" / f"demo-{slug}.png",
            title,
            COLORS[index % len(COLORS)],
        )

        product, _ = Product.objects.update_or_create(
            slug=slug,
            defaults={
                "category": categories[category_slug],
                "title": title,
                "description": description,
                "price": Decimal(price),
                "discount_price": Decimal(discount_price) if discount_price else None,
                "stock": stock,
                "status": Status.PUBLISHED,
            },
        )

        main_image = ProductImage.objects.filter(product=product, is_main=True).first()
        if main_image:
            main_image.image = f"products/{image_path.name}"
            main_image.save(update_fields=["image", "updated_at"])
        else:
            ProductImage.objects.create(
                product=product,
                image=f"products/{image_path.name}",
                is_main=True,
            )

    print(f"Created or updated {len(CATEGORIES)} categories and {len(PRODUCTS)} products.")


def create_image(path, title, color_pair):
    if path.exists():
        return path

    accent, background = color_pair
    image = Image.new("RGB", (1200, 900), background)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((80, 80, 1120, 820), radius=36, fill="white", outline=accent, width=6)
    draw.rounded_rectangle((120, 120, 360, 190), radius=18, fill=accent)
    draw.text((152, 140), "IMTIHON", fill="white", font=get_font(30))

    wrapped = wrap_text(title, 21)
    y = 330
    for line in wrapped:
        draw.text((140, y), line, fill="#172033", font=get_font(62))
        y += 76

    draw.text((140, 700), "Demo product image", fill="#667085", font=get_font(34))
    image.save(path, "PNG")
    return path


def get_font(size):
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def wrap_text(text, limit):
    words = text.split()
    lines = []
    current = []
    for word in words:
        candidate = " ".join([*current, word])
        if len(candidate) > limit and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines[:3]


if __name__ == "__main__":
    main()
