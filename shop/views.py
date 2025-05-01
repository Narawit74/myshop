from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Product, Category, Cart, Order, OrderItem, ProductImage
from django.http import JsonResponse
from .models import UserProfile
from .forms import UserProfileForm
import uuid
import qrcode
from io import BytesIO
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from .forms import ProductForm, ProductImageForm, CategoryForm
from django.forms import modelformset_factory
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import UserForm

def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "ชื่อผู้ใช้นี้มีผู้ใช้งานแล้ว โปรดเลือกชื่อผู้ใช้อื่น")
            return render(request, 'shop/add_user.html')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "อีเมลนี้มีผู้ใช้งานแล้ว โปรดเลือกอีเมลอื่น")
            return render(request, 'shop/add_user.html')

        # Create the user with password hashing
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password  # Django will hash the password automatically
        )
        messages.success(request, "เพิ่มผู้ใช้สำเร็จ")
        return redirect('shop:admin_user_list')  # Redirect to the user list page after saving

    return render(request, 'shop/admin_user_list')

def admin_order_list(request):
    orders = Order.objects.all()  # Or filter based on specific criteria

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get(f'status_{order_id}')
        
        if order_id and new_status:
            order = Order.objects.get(id=order_id)
            order.status = new_status
            order.save()

    return render(request, 'shop/admin_order_list.html', {'orders': orders})

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)

# เช็คว่าเป็นแค่ admin เท่านั้นที่เข้าถึงฟังก์ชันนี้ได้
def is_admin(user):
    return user.is_staff

# แสดงรายชื่อผู้ใช้ทั้งหมด
@user_passes_test(is_admin)
def admin_user_list(request):
    users = User.objects.all()
    return render(request, 'shop/admin_user_list.html', {'users': users})

# แก้ไขข้อมูลผู้ใช้
@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        messages.success(request, 'ข้อมูลผู้ใช้ถูกอัปเดตเรียบร้อยแล้ว')
        return redirect('shop:admin_user_list')
    
    return render(request, 'shop/admin_edit_user.html', {'user': user})

# ลบผู้ใช้
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if user != request.user:  # ห้ามลบผู้ใช้ที่ล็อกอินอยู่
        user.delete()
        messages.success(request, 'ผู้ใช้ถูกลบเรียบร้อยแล้ว')
    else:
        messages.error(request, 'ไม่สามารถลบผู้ใช้ที่ล็อกอินอยู่ได้')
    
    return redirect('shop:admin_user_list')

def admin_edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    categories = Category.objects.all()
    product_images = ProductImage.objects.filter(product=product)

    if request.method == "POST":
        # Save the product information
        product.name = request.POST['name']
        product.description = request.POST['description']
        product.price = request.POST['price']
        product.stock = request.POST['stock']
        product.category = Category.objects.get(id=request.POST['category'])
        product.save()

        # Save uploaded images if any
        if request.FILES.getlist('image'):
            for img in request.FILES.getlist('image'):
                product_image = ProductImage(product=product, image=img)
                product_image.save()
                messages.success(request, "บันทึกการแก้ใขเรียบร้อยแล้ว")

        # Redirect to the same page after saving (go back to the product edit page)
        return redirect(reverse('shop:admin_edit_product', kwargs={'product_id': product.id}))

    return render(request, 'shop/admin_edit_product.html', {
        'product': product,
        'categories': categories,
        'product_images': product_images
    })

def remove_uploaded_image(request, image_id):
    # Remove an uploaded image from the session
    image = request.session.get('product_images', [])
    image = [img for img in image if img['id'] != image_id]
    request.session['product_images'] = image
    return redirect('shop:admin_edit_product', product_id=request.product.id)

@admin_required
def delete_image(request, image_id):
    # ค้นหารูปภาพตาม ID
    image = get_object_or_404(ProductImage, id=image_id)
    
    # ลบรูปภาพ
    image.delete()

    # หลังจากลบเสร็จแล้ว ให้กลับไปที่หน้าการแก้ไขสินค้า
    return redirect('shop:admin_edit_product', product_id=image.product.id)

@admin_required
def admin_product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/admin_product_list.html', {'products': products})

@admin_required
def admin_delete_product(request, product_id):
    # ค้นหาสินค้าตาม ID
    product = get_object_or_404(Product, id=product_id)
    
    # ลบสินค้าออกจากฐานข้อมูล
    product.delete()
    
    # หลังจากลบสินค้าแล้ว, redirect ไปยังหน้าจัดการสินค้าหรือหน้าอื่น ๆ
    return redirect('shop:admin_product_list')

@admin_required
def admin_add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        image_form = ProductImageForm(request.POST, request.FILES)

        if product_form.is_valid() and image_form.is_valid():
            # บันทึกข้อมูลสินค้า
            product = product_form.save()

            # บันทึกรูปภาพหลายไฟล์
            images = request.FILES.getlist('image')  # รับหลายไฟล์จากฟอร์ม
            for image in images:
                new_image = ProductImage(product=product, image=image, is_primary=False)
                new_image.save()

            messages.success(request, 'เพิ่มสินค้าและรูปภาพสำเร็จ!')
            return redirect('shop:admin_product_list')  # ไปที่หน้ารายการสินค้าหลังจากบันทึก
        else:
            # แสดงข้อผิดพลาดของฟอร์ม
            messages.error(request, 'กรุณาตรวจสอบข้อมูลให้ถูกต้อง')
            print("Product form errors:", product_form.errors)
            print("Image form errors:", image_form.errors)

    else:
        product_form = ProductForm()
        image_form = ProductImageForm()

    return render(request, 'shop/admin_add_product.html', {
        'product_form': product_form,
        'image_form': image_form,
    })

@admin_required
def admin_add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shop:admin_category_list')  # ไปที่หน้าแสดงรายการหมวดหมู่
    else:
        form = CategoryForm()

    return render(request, 'shop/admin_add_category.html', {'form': form})

@admin_required
def admin_category_list(request):
    categories = Category.objects.all()  # ดึงข้อมูลหมวดหมู่ทั้งหมด
    return render(request, 'shop/admin_category_list.html', {'categories': categories})

@admin_required
def admin_edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('shop:admin_category_list')  # ไปที่หน้าแสดงรายการหมวดหมู่
    else:
        form = CategoryForm(instance=category)

    return render(request, 'shop/admin_edit_category.html', {'form': form, 'category': category})

@admin_required
def admin_delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        return redirect('shop:admin_category_list')  # ไปที่หน้าแสดงรายการหมวดหมู่
    return render(request, 'shop/admin_delete_category.html', {'category': category})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "ล็อกอินเข้าสู่ระบบสำเร็จ!")
            return redirect('shop:product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "ลงทะเบียนสำเร็จ! กรุณาล็อกอินเข้าสู่ระบบ.")
            return redirect('shop:login')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "คุณได้ออกจากระบบแล้ว")
    return redirect('shop:login')

def product_list(request, category_id=None):
    categories = Category.objects.all()
    products = Product.objects.all()
    current_category = None

    q = request.GET.get('q', '')
    if q:
        products = products.filter(name__icontains=q)

    if category_id:
        current_category = get_object_or_404(Category, id=category_id)
        products = products.filter(category=current_category)

    products = products.order_by('-id')[:20]  # <<< ตรงนี้แหละ! เอาเฉพาะ 20 ตัวล่าสุด

    return render(request, 'shop/product_list.html', {
        'products': products,
        'categories': categories,
        'current_category': current_category,
    })

# ฟังก์ชันแสดงสินค้าทั้งหมดในหน้าแรก
def home_view(request):
    categories = Category.objects.all()  # ดึงข้อมูลหมวดหมู่ทั้งหมด
    products = Product.objects.all()  # ดึงสินค้าทั้งหมด
    return render(request, 'shop/product_list.html', {'categories': categories, 'products': products})

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'shop/product_detail.html', {'product': product})

def search_view(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query)  # ค้นหาสินค้าจากชื่อ
    else:
        products = Product.objects.all()
    
    return render(request, 'shop/product_list.html', {'products': products, 'query': query})

# ฟังก์ชันแสดงสินค้าตามหมวดหมู่
def category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)  # ดึงหมวดหมู่ที่มี id ตรงกับ category_id
    products = Product.objects.filter(category=category)  # ดึงสินค้าที่อยู่ในหมวดหมู่เดียวกัน
    return render(request, 'shop/category_detail.html', {'category': category, 'products': products})

def cart_detail(request):
    cart_items = []
    total_price = 0

    if request.user.is_authenticated:
        # ผู้ใช้ล็อกอิน ใช้ Cart จากฐานข้อมูล
        user_cart = Cart.objects.filter(user=request.user)
        for item in user_cart:
            subtotal = item.product.price * item.quantity
            cart_items.append({
                'product': item.product,
                'quantity': item.quantity,
                'subtotal': subtotal,
            })
            total_price += subtotal
    else:
        # ผู้ใช้ทั่วไป ใช้ session
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            subtotal = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
            total_price += subtotal

    return render(request, 'shop/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))  # รับค่าจำนวนจากฟอร์ม
    except (ValueError, TypeError):
        quantity = 1  # ค่าเริ่มต้นถ้าไม่มีการส่งค่า quantity

    if quantity <= 0:
        quantity = 1  # กันคนส่งค่าติดลบ

    if request.user.is_authenticated:
        # สำหรับผู้ใช้ที่ล็อกอิน
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            cart_item.quantity = product.stock  # ปรับจำนวนสินค้าให้ไม่เกินสต๊อก
            cart_item.save()
            messages.warning(request, f"เพิ่มได้สูงสุด {product.stock} ชิ้น (ตามสต๊อก)")
        else:
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f"เพิ่ม {quantity} ชิ้นลงในตะกร้าแล้ว")
    else:
        # สำหรับผู้ใช้ที่ไม่ได้ล็อกอิน (ใช้ session)
        cart = request.session.get('cart', {})
        current_qty = cart.get(str(product_id), 0)
        new_qty = current_qty + quantity
        if new_qty > product.stock:
            cart[str(product_id)] = product.stock
            messages.warning(request, f"เพิ่มได้สูงสุด {product.stock} ชิ้น (ตามสต๊อก)")
        else:
            cart[str(product_id)] = new_qty
            messages.success(request, f"เพิ่ม {quantity} ชิ้นลงในตะกร้าแล้ว")
        request.session['cart'] = cart

    return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))

def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        Cart.objects.filter(user=request.user, product=product).delete()
    else:
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart

    return redirect('shop:cart_detail')

def increase_quantity(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.warning(request, "เพิ่มสินค้าไม่ได้เกินจำนวนสต๊อก")
    else:
        cart = request.session.get('cart', {})
        current_qty = cart.get(str(product_id), 0)
        if current_qty < product.stock:
            cart[str(product_id)] = current_qty + 1
            request.session['cart'] = cart
        else:
            messages.warning(request, "เพิ่มสินค้าไม่ได้เกินจำนวนสต๊อก")

    return redirect('shop:cart_detail')

def decrease_quantity(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(user=request.user, product=product).first()
        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
    else:
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)] -= 1
            if cart[str(product_id)] <= 0:
                del cart[str(product_id)]
            request.session['cart'] = cart

    return redirect('shop:cart_detail')

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    total_price = float(total_price)  # Convert Decimal to float for JSON serialization

    user_profile = UserProfile.objects.filter(user=request.user).first()

    if not user_profile or not user_profile.address:
        return render(request, 'shop/checkout.html', {
            'cart_items': cart_items,
            'total_price': total_price,
            'error_message': 'กรุณาเพิ่มข้อมูลที่อยู่จัดส่งในโปรไฟล์'
        })

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        order_number = str(uuid.uuid4())[:8].upper()

        # Start the transaction
        with transaction.atomic():
            # Create a new order
            order = Order.objects.create(
                user=request.user,
                order_number=order_number,
                total_price=total_price,
                payment_method=payment_method,
                address=user_profile.address,
                city=user_profile.city,
                province=user_profile.province,
                postcode=user_profile.postcode,
                phone=user_profile.phone
            )

            # Add items to the order
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            # Clear cart after order creation
            cart_items.delete()

        # Save order details to session
        request.session['checkout_data'] = {
            'order_number': order_number,
            'total_price': total_price,
            'payment_method': payment_method,
            'user_profile': {
                'address': user_profile.address,
                'city': user_profile.city,
                'province': user_profile.province,
                'postcode': user_profile.postcode,
                'phone': user_profile.phone
            }
        }

        return redirect('shop:payment')

    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'user_profile': user_profile,
    })

@login_required
def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # อัปเดตชื่อและนามสกุล
        user = request.user
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        if not first_name:
            first_name = user.first_name  # ใช้ชื่อเดิมถ้าไม่ได้กรอก
        if not last_name:
            last_name = user.last_name  # ใช้นามสกุลเดิมถ้าไม่ได้กรอก

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # อัปเดตข้อมูลที่อยู่หากมีการเปลี่ยนแปลง
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        province = request.POST.get('province', '')
        postcode = request.POST.get('postcode', '')
        phone = request.POST.get('phone', '')

        # ตรวจสอบว่ามีการกรอกข้อมูลที่อยู่หรือไม่ และอัปเดตเฉพาะข้อมูลที่ถูกกรอก
        if address:
            user_profile.address = address
        if city:
            user_profile.city = city
        if province:
            user_profile.province = province
        if postcode:
            user_profile.postcode = postcode
        if phone:
            user_profile.phone = phone

        user_profile.save()
        
        messages.success(request, "โปรไฟล์ของคุณถูกอัปเดตเรียบร้อยแล้ว")
        return redirect('shop:profile')

    else:
        # แสดงฟอร์มและข้อมูลของผู้ใช้
        form = UserProfileForm(instance=user_profile)

    return render(request, 'shop/profile.html', {'form': form, 'user_profile': user_profile})

@login_required
def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    return render(request, 'shop/order_success.html', {
        'order': order,
        'order_items': order_items
    })

def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'shop/order_history.html', {'orders': orders})

@login_required
def payment_view(request):
    checkout_data = request.session.get('checkout_data')

    if not checkout_data:
        return redirect('shop:checkout')

    if request.method == 'POST':
        # เมื่อการชำระเงินสำเร็จ
        order_number = checkout_data['order_number']
        total_price = checkout_data['total_price']
        payment_method = checkout_data['payment_method']
        address = checkout_data['address']
        city = checkout_data['city']
        province = checkout_data['province']
        postcode = checkout_data['postcode']
        phone = checkout_data['phone']
        cart_items = checkout_data['cart_items']

        # สร้างคำสั่งซื้อในฐานข้อมูล
        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            total_price=total_price,
            payment_method=payment_method,
            address=address,
            city=city,
            province=province,
            postcode=postcode,
            phone=phone
        )

        # เพิ่มรายการสินค้าในคำสั่งซื้อ
        for item in cart_items:
            product = get_object_or_404(Product, id=item['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=item['price']
            )

        # เคลียร์ตะกร้าสินค้าหลังจากการสั่งซื้อ
        Cart.objects.filter(user=request.user).delete()

        # เคลียร์ session
        del request.session['checkout_data']

        # รีไดเร็กไปที่หน้าสำเร็จ
        return redirect('shop:order_success', order_number=order.order_number)

    return render(request, 'shop/payment.html')




