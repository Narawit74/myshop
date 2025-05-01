from django.db import models
from django.contrib.auth.models import User
import uuid

# โมเดลสำหรับหมวดหมู่สินค้า
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# โมเดลสินค้าที่เชื่อมโยงกับหมวดหมู่
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)  # เชื่อมโยงกับ Category
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# โมเดลสำหรับรูปภาพสินค้า
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)  # Add this line to track when the item was added
    
    def __str__(self):
        return f"{self.product.name} in {self.user.username}'s cart"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, null=True, blank=True)  # แก้ไขที่นี่
    city = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(max_length=100, null=True, blank=True)
    postcode = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class Order(models.Model):
    PENDING = 'Pending'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELLED = 'Cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    payment_method = models.CharField(max_length=50, choices=[('promptpay', 'PromptPay')])

    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(max_length=100, null=True, blank=True)
    postcode = models.CharField(max_length=10, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = str(uuid.uuid4()).split('-')[0].upper()
        if self.user:
            self.first_name = self.user.first_name
            self.last_name = self.user.last_name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} ({self.status})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_subtotal(self):
        return self.quantity * self.price