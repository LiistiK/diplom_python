from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order, OrderItem
from shop.models import Product
from orders.serializers import OrderSerializer


class OrdersView(APIView):
    def get(self, request, *args, **kwargs):
        order_id = request.query_params.get('order_id')

        if order_id:
            queryset = Order.objects.get(pk=order_id)
            serializer = OrderSerializer(queryset)

        else:
            queryset = Order.objects.all().prefetch_related('items')
            serializer = OrderSerializer(queryset, many=True)

        return Response(serializer.data)

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(user=request.user)
    order.products.add(product)
    order.total_price += product.price
    order.save()
    return redirect('cart')

@login_required
def remove_from_cart(request, external_id):
    product = Product.objects.get(id=external_id)
    order = Order.objects.get(user=request.user)
    order.products.remove(product)
    order.total_price -= product.price
    order.save()
    return redirect('cart')

@login_required
def cart(request):
    order = Order.objects.get(user=request.user)
    context = {'order': order}
    return render(request, 'cart.html', context)

@login_required
def checkout(request):
    order = Order.objects.get(user=request.user)
    if request.method == 'POST':
        order.delete()
        return redirect('home')
    context = {'order': order}
    return render(request, 'checkout.html', context)


