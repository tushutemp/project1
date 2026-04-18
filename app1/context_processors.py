# context_processors.py
from .models import CartItem

def cart_count(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        cart_item_count = sum(item.quantity for item in cart_items)
        return {'cart_item_count': cart_item_count}
    return {'cart_item_count': 0}