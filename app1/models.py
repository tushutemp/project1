from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User
# ------------------ STUDENT ------------------
class student(models.Model):
    Name = models.CharField(max_length=50)
    Email = models.EmailField(max_length=50)
    Password = models.CharField(max_length=50)
    Phone = models.CharField(max_length=50)
    DOB = models.CharField(max_length=50)
    Gender = models.CharField(max_length=50)
    Address = models.CharField(max_length=50)


# ------------------ COUPON ------------------
# class Coupon(models.Model):
#     code = models.CharField(max_length=20, unique=True)
#     discount = models.FloatField()
#     is_percentage = models.BooleanField(default=True)
#     min_amount = models.FloatField(default=0)
#     valid_from = models.DateTimeField()
#     valid_to = models.DateTimeField()
#     active = models.BooleanField(default=True)

#     def is_valid(self):
#         now = timezone.now()
#         return self.active and self.valid_from <= now <= self.valid_to

#     def __str__(self):
#         return self.code


# ------------------ PRODUCT ------------------
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    SIZE_CHOICES = (
        ('clothing', 'clothing'),
        ('footwear', 'Footwear'),
        ('none', 'No Size'),
    )

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    description = models.TextField(blank=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    # ❌ REMOVE THIS
    # rating = models.FloatField(default=0)

    # ✅ ADD THIS
    color = models.CharField(max_length=50, blank=True, null=True)

    size_type = models.CharField(max_length=20, choices=SIZE_CHOICES, default='none')

    # ✅ ADD THIS
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    # ⭐ ADD THIS METHOD
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0


class Size(models.Model):
    SIZE_TYPE = (
        ('clothing', 'Clothing'),   # S, M, L
        ('footwear', 'Footwear'),   # 6, 7, 8
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size_type = models.CharField(max_length=20, choices=SIZE_TYPE)
    value = models.CharField(max_length=10)  # S, M, L or 6, 7, 8

    def __str__(self):
        return f"{self.product.name} - {self.value}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.IntegerField()
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
# ------------------ CART ------------------
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.size} x {self.quantity}"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.FloatField()

    is_percentage = models.BooleanField(default=True)
    min_amount = models.FloatField(default=0)

    active = models.BooleanField(default=True)

    expiry_date = models.DateTimeField(null=True, blank=True)  # ✅ ADD THIS

    def is_valid(self):
        if not self.active:
            return False
        if self.expiry_date and self.expiry_date < timezone.now():
            return False
        return True

# ------------------ ORDER ------------------
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=10)

    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Credit/Debit Card'),
        ('upi', 'UPI'),
    ]

    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cod')
    card_number = models.CharField(max_length=20, blank=True, null=True)
    expiry_date = models.CharField(max_length=10, blank=True, null=True)
    cvv = models.CharField(max_length=5, blank=True, null=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True)

    # ✅ ADD THESE FIELDS
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tracking_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    
    # Delivery Location (from user's address)
    delivery_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    delivery_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Estimated delivery time
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    
    # Status update timestamps
    confirmed_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    out_for_delivery_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Current location (for live tracking - updated by delivery person)
    current_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    last_location_update = models.DateTimeField(null=True, blank=True)
    def update_status(self, new_status, location=None, note=None, lat=None, lng=None):
        """Update order status and create tracking history"""
        from django.utils import timezone
        
        old_status = self.status
        self.status = new_status
        
        # Update timestamp based on status
        if new_status == 'confirmed' and not self.confirmed_at:
            self.confirmed_at = timezone.now()
        elif new_status == 'processing' and not self.processed_at:
            self.processed_at = timezone.now()
        elif new_status == 'shipped' and not self.shipped_at:
            self.shipped_at = timezone.now()
        elif new_status == 'out_for_delivery' and not self.out_for_delivery_at:
            self.out_for_delivery_at = timezone.now()
        elif new_status == 'delivered' and not self.delivered_at:
            self.delivered_at = timezone.now()
        
        self.save()
        
        # Create tracking history entry
        OrderTrackingHistory.objects.create(
            order=self,
            status=new_status,
            location=location or self.get_status_location(new_status),
            note=note,
            latitude=lat,
            longitude=lng
        )
        
        return True
    
    def get_status_location(self, status):
        """Get default location message for status"""
        locations = {
            'pending': 'Order received at warehouse',
            'confirmed': 'Order confirmed, preparing for processing',
            'processing': 'Order is being packed',
            'shipped': 'Order left warehouse',
            'out_for_delivery': 'Out for delivery to your address',
            'delivered': 'Delivered to your address',
            'cancelled': 'Order cancelled'
        }
        return locations.get(status, 'Status updated')


# ------------------ ORDER ITEM ------------------
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    


class OrderTrackingHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_history')
    status = models.CharField(max_length=20)
    location = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.order.tracking_number} - {self.status} at {self.created_at}"
    


