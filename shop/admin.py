from django.contrib import admin
from .models import UserProfile
from .models import Product, ProductImage, Category, Cart, Order, OrderItem  # นำเข้าโมเดลจาก models.py
from django.utils.html import format_html
from .models import Order

# ลงทะเบียน Order เพียงครั้งเดียว
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_price', 'status', 'created_at')  # เพิ่ม 'status'
    list_filter = ('status', 'created_at')  # กรองตามสถานะและวันที่
    search_fields = ('order_number', 'user__username')  # ค้นหาจากหมายเลขคำสั่งซื้อและชื่อผู้ใช้
    readonly_fields = ('order_number', 'created_at')  # ไม่ให้แก้ไขหมายเลขคำสั่งซื้อและวันที่

    def status_display(self, obj):
        return obj.get_status_display()  # แสดงค่าที่อ่านง่ายจาก choices

    status_display.short_description = 'Order Status'

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'created_at', 'updated_at')  # แสดงหมวดหมู่ในรายการสินค้า
    search_fields = ('name', 'description')
    list_filter = ('category', 'created_at', 'updated_at')  # เพิ่มการกรองตามหมวดหมู่
    inlines = [ProductImageInline]

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    list_filter = ('user',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'city', 'postcode', 'phone')
    search_fields = ('user__username', 'address', 'city')
    list_filter = ('city',)
    fields = ('user', 'address', 'city', 'postcode', 'phone')  # ฟิลด์ที่แสดงในหน้าแก้ไข

# ลงทะเบียนโมเดลที่เหลือ
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cart, CartAdmin)
