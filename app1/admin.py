from django.contrib import admin

from.models import*
# Register your models here.
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Category)
admin.site.register(Coupon)
admin.site.register(Size)
admin.site.register(OrderTrackingHistory)
# admin.site.register(OrderTrackingHistoryInline)
# admin.site.register(OrderTrackingHistoryAdmin)
class OrderTrackingHistoryInline(admin.TabularInline):
    model = OrderTrackingHistory
    extra = 1
    readonly_fields = ('created_at',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'tracking_number', 'user', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['tracking_number', 'user__username', 'full_name']
    readonly_fields = ['tracking_number', 'created_at', 'confirmed_at', 'processed_at', 
                       'shipped_at', 'out_for_delivery_at', 'delivered_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('tracking_number', 'user', 'status', 'total_amount', 'discount_amount')
        }),
        ('Customer Details', {
            'fields': ('full_name', 'email', 'address', 'city', 'state', 'zipcode')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'card_number', 'expiry_date', 'upi_id')
        }),
        ('Timestamps', {
            'fields': ('confirmed_at', 'processed_at', 'shipped_at', 'out_for_delivery_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_processing', 'mark_as_shipped', 
               'mark_as_out_for_delivery', 'mark_as_delivered']
    
    def mark_as_confirmed(self, request, queryset):
        for order in queryset:
            order.update_status('confirmed')
        self.message_user(request, f"{queryset.count()} order(s) marked as confirmed.")
    mark_as_confirmed.short_description = "Mark selected orders as Confirmed"
    
    def mark_as_processing(self, request, queryset):
        for order in queryset:
            order.update_status('processing')
        self.message_user(request, f"{queryset.count()} order(s) marked as processing.")
    mark_as_processing.short_description = "Mark selected orders as Processing"
    
    def mark_as_shipped(self, request, queryset):
        for order in queryset:
            order.update_status('shipped')
        self.message_user(request, f"{queryset.count()} order(s) marked as shipped.")
    mark_as_shipped.short_description = "Mark selected orders as Shipped"
    
    def mark_as_out_for_delivery(self, request, queryset):
        for order in queryset:
            order.update_status('out_for_delivery')
        self.message_user(request, f"{queryset.count()} order(s) marked as out for delivery.")
    mark_as_out_for_delivery.short_description = "Mark selected orders as Out for Delivery"
    
    def mark_as_delivered(self, request, queryset):
        for order in queryset:
            order.update_status('delivered')
        self.message_user(request, f"{queryset.count()} order(s) marked as delivered.")
    mark_as_delivered.short_description = "Mark selected orders as Delivered"


# @admin.register(OrderTrackingHistory)
class OrderTrackingHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'location', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__tracking_number', 'order__user__username']