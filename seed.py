from app import create_app, db
from app.models import Category, Product, User, ShippingZone

app = create_app()

with app.app_context():
    db.create_all()

    if Category.query.first():
        print("Database already seeded.")
        exit()

    categories = [
        {"name": "Electronics", "slug": "electronics", "description": "Latest gadgets and electronic devices"},
        {"name": "Clothing", "slug": "clothing", "description": "Fashionable clothing and accessories"},
        {"name": "Home & Kitchen", "slug": "home-kitchen", "description": "Home appliances and kitchen essentials"},
        {"name": "Books", "slug": "books", "description": "Educational and entertainment books"},
        {"name": "Sports", "slug": "sports", "description": "Sports equipment and fitness gear"},
        {"name": "Beauty", "slug": "beauty", "description": "Beauty products and personal care"},
    ]

    for cat_data in categories:
        cat = Category(**cat_data)
        db.session.add(cat)

    db.session.flush()

    electronics = Category.query.filter_by(slug="electronics").first()
    clothing = Category.query.filter_by(slug="clothing").first()
    home = Category.query.filter_by(slug="home-kitchen").first()
    books = Category.query.filter_by(slug="books").first()
    sports = Category.query.filter_by(slug="sports").first()
    beauty = Category.query.filter_by(slug="beauty").first()

    products = [
        {"name": "SmartPhone X Pro", "slug": "smartphone-x-pro", "description": "Latest flagship smartphone with 5G, 256GB storage, 8GB RAM, and professional-grade camera system. Features biometric fingerprint sensor and face unlock.", "price": 899.99, "original_price": 1099.99, "stock": 50, "category_id": electronics.id, "is_featured": True, "rating": 4.5, "review_count": 128, "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400&h=400&fit=crop"},
        {"name": "Wireless Noise-Canceling Headphones", "slug": "wireless-headphones", "description": "Premium over-ear headphones with active noise cancellation, 30-hour battery life, and hi-res audio support.", "price": 249.99, "original_price": 349.99, "stock": 75, "category_id": electronics.id, "is_featured": True, "rating": 4.3, "review_count": 95, "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop"},
        {"name": "Laptop UltraBook 15", "slug": "laptop-ultrabook-15", "description": "Thin and light laptop with 15.6\" 4K display, Intel i7 processor, 16GB RAM, 512GB SSD. Includes fingerprint reader for secure login.", "price": 1299.99, "stock": 30, "category_id": electronics.id, "is_featured": True, "rating": 4.7, "review_count": 67, "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=400&fit=crop"},
        {"name": "Smart Watch Fitness Pro", "slug": "smart-watch-fitness", "description": "Advanced fitness smartwatch with heart rate monitoring, GPS tracking, sleep analysis, and secure payment support.", "price": 199.99, "original_price": 279.99, "stock": 100, "category_id": electronics.id, "is_featured": True, "rating": 4.2, "review_count": 203, "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop"},
        {"name": "Men's Classic Fit Suit", "slug": "mens-classic-suit", "description": "Premium wool blend suit with modern slim fit design. Perfect for business and formal occasions.", "price": 299.99, "original_price": 399.99, "stock": 40, "category_id": clothing.id, "is_featured": True, "rating": 4.4, "review_count": 45, "image_url": "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=400&h=400&fit=crop"},
        {"name": "Women's Summer Dress", "slug": "womens-summer-dress", "description": "Elegant floral print summer dress made from breathable cotton. Available in multiple sizes.", "price": 59.99, "stock": 80, "category_id": clothing.id, "rating": 4.1, "review_count": 156, "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400&h=400&fit=crop"},
        {"name": "Designer Handbag", "slug": "designer-handbag", "description": "Luxury leather handbag with gold-tone hardware, multiple compartments, and adjustable shoulder strap.", "price": 449.99, "original_price": 599.99, "stock": 25, "category_id": clothing.id, "is_featured": True, "rating": 4.6, "review_count": 89, "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400&h=400&fit=crop"},
        {"name": "Premium Blender Set", "slug": "premium-blender", "description": "High-performance blender with 1500W motor, BPA-free container, and 10 speed settings. Ideal for smoothies and soups.", "price": 79.99, "original_price": 99.99, "stock": 60, "category_id": home.id, "rating": 4.0, "review_count": 234, "image_url": "https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=400&h=400&fit=crop"},
        {"name": "Stainless Steel Cookware Set", "slug": "cookware-set", "description": "10-piece professional stainless steel cookware set with tempered glass lids and stay-cool handles.", "price": 189.99, "stock": 35, "category_id": home.id, "is_featured": True, "rating": 4.5, "review_count": 112, "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop"},
        {"name": "Robot Vacuum Cleaner", "slug": "robot-vacuum", "description": "Smart robot vacuum with lidar navigation, 2500Pa suction, app control, and works with voice assistants.", "price": 349.99, "original_price": 449.99, "stock": 45, "category_id": home.id, "rating": 4.3, "review_count": 178, "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400&h=400&fit=crop"},
        {"name": "Security Camera System", "slug": "security-camera", "description": "4K wireless security camera system with night vision, motion detection, and cloud storage. Ideal for home security.", "price": 199.99, "stock": 40, "category_id": electronics.id, "rating": 4.2, "review_count": 67, "image_url": "https://images.unsplash.com/photo-1558002038-1055907df827?w=400&h=400&fit=crop"},
        {"name": "Programming in Python", "slug": "python-programming", "description": "Comprehensive guide to Python programming from basics to advanced topics including security and encryption.", "price": 39.99, "stock": 200, "category_id": books.id, "rating": 4.8, "review_count": 312, "image_url": "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=400&h=400&fit=crop"},
        {"name": "Cybersecurity Fundamentals", "slug": "cybersecurity-book", "description": "Essential guide to cybersecurity, encryption, authentication, and trusted computing platforms.", "price": 49.99, "stock": 150, "category_id": books.id, "is_featured": True, "rating": 4.6, "review_count": 89, "image_url": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400&h=400&fit=crop"},
        {"name": "Yoga Mat Premium", "slug": "yoga-mat", "description": "Extra thick 6mm yoga mat with non-slip surface, carrying strap, and alignment lines.", "price": 34.99, "stock": 120, "category_id": sports.id, "rating": 4.3, "review_count": 201, "image_url": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400&h=400&fit=crop"},
        {"name": "Fitness Tracker Band", "slug": "fitness-tracker", "description": "Lightweight fitness band with step counter, heart rate monitor, sleep tracking, and 7-day battery life.", "price": 49.99, "stock": 200, "category_id": sports.id, "rating": 4.0, "review_count": 445, "image_url": "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=400&h=400&fit=crop"},
        {"name": "Organic Skincare Set", "slug": "skincare-set", "description": "Natural organic skincare set including cleanser, toner, moisturizer, and serum. Cruelty-free.", "price": 69.99, "stock": 90, "category_id": beauty.id, "is_featured": True, "rating": 4.4, "review_count": 167, "image_url": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400&h=400&fit=crop"},
        {"name": "Wireless Earbuds Pro", "slug": "wireless-earbuds", "description": "True wireless earbuds with active noise cancellation, IPX5 water resistance, and wireless charging case.", "price": 149.99, "original_price": 199.99, "stock": 85, "category_id": electronics.id, "rating": 4.1, "review_count": 256, "image_url": "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=400&h=400&fit=crop"},
        {"name": "Tablet 10 Inch", "slug": "tablet-10-inch", "description": "10-inch tablet with 2K display, octa-core processor, 128GB storage, and 8-hour battery. Perfect for entertainment.", "price": 299.99, "stock": 55, "category_id": electronics.id, "rating": 4.0, "review_count": 78, "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=400&fit=crop"},
        {"name": "Coffee Maker Deluxe", "slug": "coffee-maker", "description": "Programmable 12-cup coffee maker with thermal carafe, brew strength selector, and auto-shutoff.", "price": 89.99, "original_price": 109.99, "stock": 70, "category_id": home.id, "rating": 4.2, "review_count": 189, "image_url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&h=400&fit=crop"},
        {"name": "Men's Running Shoes", "slug": "mens-running-shoes", "description": "Lightweight running shoes with responsive cushioning, breathable mesh upper, and durable outsole.", "price": 119.99, "stock": 65, "category_id": sports.id, "is_featured": True, "rating": 4.5, "review_count": 134, "image_url": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400&h=400&fit=crop"},
    ]

    for prod_data in products:
        product = Product(**prod_data)
        db.session.add(product)

    import json
    zones = [
        {"name": "Tanzania Mainland", "countries": json.dumps(["Tanzania", "Tanzania, United Republic of"]), "base_rate": 3.99, "free_threshold": 50.0, "estimated_days": "1-3 business days"},
        {"name": "East Africa", "countries": json.dumps(["Kenya", "Uganda", "Rwanda", "Burundi", "South Sudan"]), "base_rate": 8.99, "free_threshold": 100.0, "estimated_days": "3-7 business days"},
        {"name": "Other Africa", "countries": json.dumps(["Nigeria", "Ghana", "South Africa", "Ethiopia", "Egypt", "Morocco"]), "base_rate": 14.99, "free_threshold": 150.0, "estimated_days": "5-10 business days"},
        {"name": "International", "countries": json.dumps(["United States", "United Kingdom", "Canada", "Germany", "France", "Australia", "China", "India", "Brazil", "Japan"]), "base_rate": 24.99, "free_threshold": 200.0, "estimated_days": "7-14 business days"},
    ]
    if not ShippingZone.query.first():
        for z in zones:
            db.session.add(ShippingZone(**z))
        db.session.commit()
        print(f"Seeded {len(zones)} shipping zones.")
    else:
        print("Shipping zones already exist.")

    db.session.commit()
    print(f"Database seeded with {len(categories)} categories and {len(products)} products!")
    print("Default admin: username='admin', password='Admin@123456'")
