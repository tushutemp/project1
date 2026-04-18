from django.shortcuts import render,HttpResponse,redirect
from.models import*
from django.http import JsonResponse
from .models import Wishlist, Product
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, get_object_or_404, redirect
from.models import*
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Coupon
from decimal import Decimal
from django.utils import timezone
from .models import Coupon, CartItem
# Create your views here.
import requests
import json
import secrets
import string
from datetime import datetime, timedelta
from django.utils import timezone
from geopy.geocoders import Nominatim
from decimal import Decimal

def home(request):
    return render(request,'index.html')

def contact(request):
    return render(request,'contact.html')

def about(request):
    return render(request,'about.html')
def shop(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    # 🔍 Search
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)

    # 📂 Category
    category = request.GET.get('category')
    if category:
        products = products.filter(category_id=category)

    # 🎨 Color
    color = request.GET.get('color')
    if color:
        products = products.filter(color__icontains=color)

    # 📏 Size
    size = request.GET.get('size')
    if size:
        products = products.filter(sizes__value=size).distinct()

    # 💰 Price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # ⭐ Rating filter (NEW)
    rating = request.GET.get('rating')
    if rating:
        # Filter products where average rating >= selected rating
        products = [
            p for p in products 
            if p.average_rating() >= int(rating)
        ]
        # Convert back to queryset if needed (for template compatibility)
        from django.db.models import Case, When, Value, IntegerField
        product_ids = [p.id for p in products]
        products = Product.objects.filter(id__in=product_ids)

    # ↕ Sorting
    sort = request.GET.get('sort')
    if sort == 'low':
        products = products.order_by('price')
    elif sort == 'high':
        products = products.order_by('-price')
    elif sort == 'rating':
        # Sort by average rating (annotate)
        products = products.annotate(
            avg_rating=models.Avg('reviews__rating')
        ).order_by('-avg_rating')
    elif sort == 'new':
        products = products.order_by('-created_at')

    # Get available colors for filter UI
    available_colors = Product.objects.exclude(color__isnull=True).exclude(color='').values_list('color', flat=True).distinct()
    
    # Get available sizes for filter UI
    available_sizes = Size.objects.values_list('value', flat=True).distinct()

    # Get wishlist items for logged-in user
    wishlist_items = []
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'shop.html', {
        'products': products,
        'categories': categories,
        'available_colors': available_colors,
        'available_sizes': available_sizes,
        'rating_options': [
            {'value': 4, 'label': '★★★★ & above'},
            {'value': 3, 'label': '★★★ & above'},
            {'value': 2, 'label': '★★ & above'},
            {'value': 1, 'label': '★ & above'},
        ],
        'wishlist_items': wishlist_items,
    })


def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)

    # ✅ SAFE totals
    total_price = sum(
        (item.product.price * item.quantity for item in cart_items),
        Decimal('0.00')
    )

    cart_item_count = sum(item.quantity for item in cart_items)

    # ✅ Get all active coupons
    coupons = Coupon.objects.filter(active=True)

    coupon = None
    discount = Decimal('0.00')
    savings_message = None

    # ✅ Get coupon from session
    coupon_id = request.session.get('coupon_id')

    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)

            if coupon.is_valid() and total_price >= coupon.min_amount:

                if coupon.is_percentage:
                    discount = total_price * (
                        Decimal(str(coupon.discount)) / Decimal('100')
                    )
                else:
                    discount = Decimal(str(coupon.discount))

                # ✅ Amazon-style message
                savings_message = f"You saved ₹{discount:.2f} with {coupon.code}"

            else:
                coupon = None

        except Coupon.DoesNotExist:
            coupon = None

    # ✅ FINAL TOTAL (never negative)
    final_total = max(total_price - discount, Decimal('0.00'))

    # ✅ ALWAYS SHOW OFFERS (NEW 🔥)
    offers = []

    for c in coupons:
        if c.is_percentage:
            offers.append(f"{c.discount}% OFF using code {c.code}")
        else:
            offers.append(f"Flat ₹{c.discount} OFF using code {c.code}")

    # ✅ If no coupons exist (fallback message)
    if not offers:
        offers.append("Use coupons to get exciting discounts!")

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_item_count': cart_item_count,

        'coupons': coupons,
        'coupon': coupon,
        'discount': discount,
        'final_total': final_total,
        'savings_message': savings_message,

        'offers': offers,  # ✅ IMPORTANT
    })
@login_required(login_url='login')


def apply_coupon_by_id(request, id):
    coupon = get_object_or_404(Coupon, id=id)

    if not coupon.is_valid():
        from django.contrib import messages
        messages.error(request, "Coupon expired")
        return redirect('cart')

    request.session['coupon_id'] = coupon.id

    from django.contrib import messages
    messages.success(request, f"{coupon.code} applied!")

    return redirect('cart')
def services(request):
    return render(request,'services.html')

def blog(request):
    return render(request,'blog.html')

def signup(request):
    if request.method=='POST':
        name=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        cpassword=request.POST['cpassword']
        if password==cpassword:
            User.objects.create_user(username=name,email=email,password=password).save()
            return redirect('logins')
        else:
            return HttpResponse("Password Didn't match!")
    return render(request,'signup.html')


def logins(request):
     if request.method=='POST':
        name=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=name,password=password)
        if user:
            login(request,user)
            return redirect(home)
        else:
            return HttpResponse("Invalid credentials!")
     return render(request,'login.html')

def contact(request):
    if request.method=='POST':
        name=request.POST['name']
        email=request.POST['email']
        password=request.POST['password']
        phone=request.POST['phone']
        dob=request.POST['dob']
        gender=request.POST['gender']
        address=request.POST['address']
        hashed_password = make_password(password)
        obj=student(Name=name,Email=email,Password=hashed_password,Phone=phone,DOB=dob,Gender=gender,Address=address)
        obj.save()
        return HttpResponse("Data Inserted")
        
    return render(request,'contact.html')


def fetch(request):
    dd=student.objects.all()
    return render(request,'fetch.html',{'d':dd})


def update(request,id):
    dd=student.objects.get(id=id)
    if request.method=='POST':
        name=request.POST['name']
        email=request.POST['email']
        password=request.POST['password']
        phone=request.POST['phone']
        dob=request.POST['dob']
        gender=request.POST['gender']
        address=request.POST['address']
        dd.Name=name
        dd.Email=email
        dd.Password=password
        dd.Phone=phone
        dd.DOB=dob
        dd.Gender=gender
        dd.Address=address
        dd.save()
        return redirect(fetch)
    return render(request,'update.html',{'dd':dd})


def signup(request):
    if request.method=='POST':
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        cpassword=request.POST['cpassword']
        if password==cpassword:
            User.objects.create_user(username=username,email=email,password=password).save()
            return redirect(logins)
        else:
            return HttpResponse("password not match!")
    return render(request,'signup.html')


# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     cart = request.session.get('cart', {})
#     cart[str(product_id)] = cart.get(str(product_id), 0) + 1
#     request.session['cart'] = cart
#     return redirect('cart')  # Redirect to cart page

def product_detail(request, id):
    dd = Product.objects.get(id=id)
    
    # Get all reviews for this product
    reviews = Review.objects.filter(product=dd).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = dd.average_rating()
    
    # Generate star display (e.g., 4.5 = ★★★★½)
    full_stars = int(avg_rating)
    half_star = avg_rating - full_stars >= 0.5
    star_display = '★' * full_stars
    if half_star:
        star_display += '½'
    star_display += '☆' * (5 - full_stars - (1 if half_star else 0))
    
    # Check if current user has already reviewed
    has_reviewed = False
    if request.user.is_authenticated:
        has_reviewed = Review.objects.filter(product=dd, user=request.user).exists()
    
    if request.method == 'POST':
        qty = int(request.POST['quantity'])
        size = request.POST.get('size')
        
        if dd.size_type == 'none':
            size = None
        
        CartItem.objects.create(
            product=dd,
            quantity=qty,
            size=size,
            user=request.user
        )
        return redirect('cart')
    
    return render(request, 'product_details.html', {
        'dd': dd,
        'reviews': reviews,
        'review_count': reviews.count(),
        'average_rating': avg_rating,
        'star_display': star_display,
        'has_reviewed': has_reviewed,
    })

def remove_from_cart(request, id):
    cart_item = CartItem.objects.get(id=id)
    cart_item.delete()
    return redirect(cart)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, F
from .models import Order, CartItem, OrderItem
from django.contrib.auth.models import User

def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    coupon = None
    if 'coupon_id' in request.session:
        try:
            coupon = Coupon.objects.get(
                id=request.session['coupon_id'],
                expiry_date__gte=timezone.now()
            )
        except Coupon.DoesNotExist:
            request.session.pop('coupon_id', None)
    
    if not coupon:
        coupon = Coupon.objects.filter(expiry_date__gte=timezone.now(), active=True).first()
    
    totals = get_cart_total(request.user, coupon)
    total = totals['total']
    discount = totals['discount']
    final_total = totals['final_total']
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        
        payment_method = request.POST.get('payment_method')
        card_number = request.POST.get('card_number') if payment_method == 'online' else None
        expiry_date = request.POST.get('expiry_date') if payment_method == 'online' else None
        cvv = request.POST.get('cvv') if payment_method == 'online' else None
        upi_id = request.POST.get('upi_id') if payment_method == 'upi' else None
        
        if not cart_items.exists():
            messages.error(request, "Your cart is empty!")
            return redirect('cart')
        
        # Geocode the delivery address
        lat, lng = geocode_address(address, city, state, zipcode)
        
        # Generate tracking number
        tracking_number = generate_tracking_number()
        
        # Create Order
        order = Order.objects.create(
            user=request.user,
            coupon=coupon,
            full_name=full_name,
            email=email,
            address=address,
            city=city,
            state=state,
            zipcode=zipcode,
            payment_method=payment_method,
            card_number=card_number,
            expiry_date=expiry_date,
            cvv=cvv,
            upi_id=upi_id,
            total_amount=final_total,
            discount_amount=discount,
            tracking_number=tracking_number,
            delivery_latitude=lat,
            delivery_longitude=lng,
            estimated_delivery=get_estimated_delivery_date(),
            status='pending'
        )
        
        # Create tracking history
        create_tracking_history(order, 'pending', 'Order placed successfully', 
                                f"{address}, {city}")
        
        # Create Order Items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                size=cart_item.size,
                price=cart_item.product.price
            )
        
        cart_items.delete()
        
        messages.success(request, f"Order placed successfully! Your tracking number is: {tracking_number}")
        return redirect('track_order', tracking_number=tracking_number)
    
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'discount': discount,
        'final_total': final_total,
        'coupon': coupon,
    })


from django.db.models import Avg

def update_product_rating(product):
    avg = product.reviews.aggregate(Avg('rating'))['rating__avg']
    product.rating = avg if avg else 0
    product.save()


def add_review(request, id):
    product = get_object_or_404(Product, id=id)
    
    # Check if user already reviewed this product
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.warning(request, "You have already reviewed this product!")
        return redirect('product_detail', id=product.id)
    
    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and int(rating) >= 1 and int(rating) <= 5:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment
            )
            messages.success(request, "Thank you for your review!")
        else:
            messages.error(request, "Please provide a valid rating (1-5)")
    
    return redirect('product_detail', id=product.id)
def thankyou(request):
    return render(request, 'thankyou.html')

def order_success_view(request, order_id):
    # Fetch the order
    order = get_object_or_404(Order, id=order_id)
    
    # Fetch all items related to this order
    order_items = OrderItem.objects.filter(order=order)
    
    # Calculate total price
    total_price = sum(item.price * item.quantity for item in order_items)
    
    context = {
        'order': order,
        'order_items': order_items,
        'total_price': total_price
    }
    
    return render(request, 'order_success.html', context)

def logout_view(request):
    """Log out the current user and redirect to login page"""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login') 


@login_required
def orders_view(request):
    # Get all orders for the current user
    user_orders = Order.objects.filter(user=request.user).order_by('-id')
    
    context = {
        'orders': user_orders,
    }
    return render(request, 'orders.html', context)



def get_cart_total(user, coupon=None):
    cart_items = CartItem.objects.filter(user=user)

    total = sum(item.product.price * item.quantity for item in cart_items)

    discount = Decimal('0.00')

    if coupon:
        if coupon.is_valid() and total >= coupon.min_amount:

            if coupon.is_percentage:
                discount = total * (Decimal(coupon.discount) / Decimal('100'))
            else:
                discount = Decimal(coupon.discount)

    final_total = total - discount

    return {
        'total': total,
        'discount': discount,
        'final_total': final_total
    }   


from django.contrib import messages
from .models import Coupon

def apply_coupon(request):
    code = request.POST.get('coupon')

    try:
        coupon = Coupon.objects.get(code__iexact=code)
    except Coupon.DoesNotExist:
        messages.error(request, "Invalid Coupon")
        return redirect('cart')

    if not coupon.is_valid():
        messages.error(request, "Coupon expired or inactive")
        return redirect('cart')

    request.session['coupon_id'] = coupon.id

    messages.success(request, "Coupon Applied Successfully")
    return redirect('cart')


def remove_coupon(request):
    request.session.pop('coupon_id', None)
    return redirect('cart')


@login_required


def add_to_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'login_required'})

    product = Product.objects.get(id=product_id)

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        wishlist_item.delete()
        return JsonResponse({'status': 'removed'})

    return JsonResponse({'status': 'added'})


@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user)

    return render(request, 'wishlist.html', {'items': items})

def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        Wishlist.objects.filter(
            user=request.user,
            product_id=product_id
        ).delete()

    return redirect('wishlist')


def generate_tracking_number():
    """Generate unique tracking number"""
    prefix = "CEL"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"{prefix}{timestamp}{random_str}"

def geocode_address(address, city, state, zipcode):
    """Convert address to coordinates using Nominatim (OpenStreetMap)"""
    geolocator = Nominatim(user_agent="celine_ecommerce")
    full_address = f"{address}, {city}, {state}, {zipcode}, India"
    
    try:
        location = geolocator.geocode(full_address)
        if location:
            return Decimal(str(location.latitude)), Decimal(str(location.longitude))
    except Exception as e:
        print(f"Geocoding error: {e}")
    
    # Default coordinates (if geocoding fails - center of India)
    return Decimal('20.5937'), Decimal('78.9629')

def get_estimated_delivery_date():
    """Calculate estimated delivery date (3-7 days from now)"""
    from django.utils import timezone
    import random
    days = random.randint(3, 7)
    return timezone.now() + timedelta(days=days)

def create_tracking_history(order, status, note=None, location=None, lat=None, lng=None):
    """Create tracking history entry"""
    OrderTrackingHistory.objects.create(
        order=order,
        status=status,
        note=note,
        location=location,
        latitude=lat,
        longitude=lng
    )

def track_order(request, tracking_number):
    try:
        order = get_object_or_404(Order, tracking_number=tracking_number)
        
        # Check if user owns this order or is admin
        if request.user.is_authenticated:
            if order.user != request.user and not request.user.is_staff:
                messages.error(request, "You don't have permission to track this order")
                return redirect('orders')
        else:
            # For non-logged in users, allow tracking with just tracking number
            pass
        
        tracking_history = OrderTrackingHistory.objects.filter(order=order).order_by('-created_at')
        
        # Calculate progress percentage
        status_order = ['pending', 'confirmed', 'processing', 'shipped', 'out_for_delivery', 'delivered']
        current_index = 0
        if order.status in status_order:
            current_index = status_order.index(order.status)
        
        progress_percentage = (current_index / (len(status_order) - 1)) * 100 if len(status_order) > 1 else 0
        
        # Handle missing coordinates
        if not order.delivery_latitude or not order.delivery_longitude:
            # Set default coordinates (India Gate, Delhi as fallback)
            order.delivery_latitude = 28.6129
            order.delivery_longitude = 77.2295
        
        context = {
            'order': order,
            'tracking_history': tracking_history,
            'progress_percentage': int(progress_percentage),
            'status_order': status_order,
            'current_index': current_index,
        }
        
        return render(request, 'track_order.html', context)
        
    except Exception as e:
        messages.error(request, f"Error tracking order: {str(e)}")
        return redirect('orders')

# Admin view to update order status (for delivery personnel/admin)
@login_required
def update_order_status(request, tracking_number):
    if not request.user.is_staff:  # Only staff/admin can update
        messages.error(request, "Unauthorized access")
        return redirect('home')
    
    order = get_object_or_404(Order, tracking_number=tracking_number)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        note = request.POST.get('note', '')
        location = request.POST.get('location', '')
        
        # Update status and timestamps
        order.status = new_status
        
        if new_status == 'confirmed' and not order.confirmed_at:
            order.confirmed_at = timezone.now()
            create_tracking_history(order, new_status, note or 'Order confirmed', location)
        elif new_status == 'processing' and not order.processed_at:
            order.processed_at = timezone.now()
            create_tracking_history(order, new_status, note or 'Order is being processed', location)
        elif new_status == 'shipped' and not order.shipped_at:
            order.shipped_at = timezone.now()
            create_tracking_history(order, new_status, note or 'Order has been shipped', location)
        elif new_status == 'out_for_delivery' and not order.out_for_delivery_at:
            order.out_for_delivery_at = timezone.now()
            create_tracking_history(order, new_status, note or 'Out for delivery', location)
        elif new_status == 'delivered' and not order.delivered_at:
            order.delivered_at = timezone.now()
            create_tracking_history(order, new_status, note or 'Order delivered successfully', location)
        elif new_status == 'cancelled':
            create_tracking_history(order, new_status, note or 'Order cancelled', location)
        
        # Update live location if provided
        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')
        if lat and lng:
            order.current_latitude = Decimal(lat)
            order.current_longitude = Decimal(lng)
            order.last_location_update = timezone.now()
        
        order.save()
        
        messages.success(request, f"Order status updated to {new_status}")
        return redirect('track_order', tracking_number=tracking_number)
    
    return render(request, 'admin_update_status.html', {'order': order})


from django.http import JsonResponse

def get_tracking_location(request, tracking_number):
    """API endpoint for live location updates"""
    order = get_object_or_404(Order, tracking_number=tracking_number)
    
    return JsonResponse({
        'latitude': str(order.current_latitude) if order.current_latitude else None,
        'longitude': str(order.current_longitude) if order.current_longitude else None,
        'status': order.status,
        'last_update': order.last_location_update.isoformat() if order.last_location_update else None,
    })

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_update_status(request, tracking_number):
    """Admin view to update order status"""
    order = get_object_or_404(Order, tracking_number=tracking_number)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        location = request.POST.get('location')
        note = request.POST.get('note')
        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')
        
        if new_status:
            # Convert empty strings to None
            lat = Decimal(lat) if lat else None
            lng = Decimal(lng) if lng else None
            
            order.update_status(new_status, location, note, lat, lng)
            
            messages.success(request, f"Order status updated to {new_status}")
            
            # Send notification to user (optional)
            # send_status_update_email(order, new_status)
            
            return redirect('track_order', tracking_number=tracking_number)
    
    return render(request, 'admin_update_status.html', {'order': order})