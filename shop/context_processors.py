from .models import Cart, Product

def cart_info(request):
    """
    คืนค่าจำนวนสินค้าทั้งหมด และราคารวมทั้งหมด ในตะกร้า
    """
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        total_items = sum(item.quantity for item in cart_items)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
    else:
        cart = request.session.get('cart', {})
        products = Product.objects.filter(id__in=cart.keys())
        total_items = sum(cart.values())
        total_price = sum(product.price * cart[str(product.id)] for product in products)

    return {
        'cart_total_items': total_items,
        'cart_total_price': total_price
    }
