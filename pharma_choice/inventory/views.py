from django.shortcuts import render
from django.shortcuts import render, get_object_or_404,redirect

from .forms import DrugForm, CategoryForm
from .models import Drug, Stock, Category, UserOrder,Cart, CartItem, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import user_passes_test

@login_required
def dashboard_redirect(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')  # Redirect to admin dashboard for admins
    else:
        return redirect('drug_list')

class DrugListView(ListView):
    model = Drug
    template_name = 'inventory/drug_list.html'
    context_object_name = 'drugs'

    def get_queryset(self):
        # Get the base queryset
        queryset = Drug.objects.filter(stock__stock_status=True).select_related('stock')

        # Get the search query and category from GET parameters
        search_query = self.request.GET.get('search', '')
        category_id = self.request.GET.get('category', '')

        # Filter the queryset based on the search query
        if search_query:
            queryset = queryset.filter(drug_name__icontains=search_query)

        # Filter the queryset based on the selected category
        if category_id:
            queryset = queryset.filter(category__category_id=category_id)

        return queryset

    def get_context_data(self, **kwargs):
        # Add additional context for search and category dropdown
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        return context

@login_required
def order_drug(request, drug_id):
    drug = get_object_or_404(Drug, pk=drug_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        # Check if there is enough stock available
        stock = Stock.objects.get(drug=drug)
        if stock.available_stock >= quantity:
            # Create an order and reduce the stock
            order = UserOrder.objects.create(
                drug=drug,
                quantity=quantity,
                price=drug.price_after_discount,
                total_amount=quantity * drug.price_after_discount,
                order_date=timezone.now()
            )
            stock.update_stock(quantity)  # Update stock
            messages.success(request, "Order placed successfully!")
            return redirect('order_success')  # Redirect to an order success page
        else:
            messages.error(request, "Insufficient stock available.")
            return redirect('drug_list')  # Redirect back to drug list if stock is insufficient

    return render(request, 'inventory/order_form.html', {'drug': drug})

@login_required
def add_to_cart(request, drug_id):
    drug = get_object_or_404(Drug, pk=drug_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    if request.method == "POST":
        try:
            # Get the quantity from the POST request
            quantity = int(request.POST.get("quantity", 1))

            # Retrieve or create the cart item
            cart_item, created = CartItem.objects.get_or_create(cart=cart, drug=drug)

            if created:
                # If the item is new, set the quantity
                cart_item.quantity = quantity
            else:
                # If the item already exists, increment the quantity
                cart_item.quantity += quantity

            # Save the updated cart item
            cart_item.save()
            messages.add_message(request, messages.SUCCESS, f'{drug.drug_name} added to cart.')

        except ValueError:
            messages.add_message(request, messages.ERROR, 'Invalid quantity specified.')
    else:
        messages.add_message(request, messages.ERROR, 'Invalid request method.')

    return redirect('drug_list')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'inventory/view_cart.html', {'cart': cart})

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)  # Retrieve the user's cart
    if not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    # Calculate the total amount before rendering
    total_amount = sum(item.quantity * item.drug.price_after_discount for item in cart.items.all())

    if request.method == 'POST':
        # Create a new order
        order = UserOrder.objects.create(user=request.user)
        total_amount = 0

        # Move each item from the cart to the order
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                drug=cart_item.drug,
                quantity=cart_item.quantity,
                price=cart_item.drug.price_after_discount,
            )
            total_amount += cart_item.quantity * cart_item.drug.price_after_discount

            # Update stock
            stock = cart_item.drug.stock
            if stock.available_stock >= cart_item.quantity:
                stock.update_stock(cart_item.quantity)
            else:
                messages.error(request, f"Insufficient stock for {cart_item.drug.drug_name}.")
                return redirect('cart')

        # Update the order's total amount
        order.total_amount = total_amount
        order.save()

        # Clear the cart
        cart.items.all().delete()

        # Redirect to a confirmation page
        messages.success(request, "Your order has been placed successfully.")
        return redirect('order_confirmation', order_id=order.pk)

    # Pass total_amount to the template for display
    return render(request, 'inventory/checkout.html', {'cart': cart, 'total_amount': total_amount})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(UserOrder, id=order_id, user=request.user)
    return render(request, 'inventory/order_confirmation.html', {'order': order})

@login_required
def order_history(request):
    # Retrieve all orders for the logged-in user
    orders = UserOrder.objects.filter(user=request.user).prefetch_related('items__drug')
    return render(request, 'inventory/order_history.html', {'orders': orders})

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    drugs = Drug.objects.all().select_related('stock')
    return render(request, 'inventory/admin_dashboard.html', {'drugs': drugs})

def order_success(request):
    return render(request, 'inventory/order_success.html')

def edit_drug(request, drug_id):
    drug = get_object_or_404(Drug, pk=drug_id)
    if request.method == 'POST':
        form = DrugForm(request.POST, instance=drug)
        if form.is_valid():
            form.save()
            messages.success(request, "Drug updated successfully!")
            return redirect('admin_dashboard')
    else:
        form = DrugForm(instance=drug, initial={'available_stock': drug.stock.available_stock})
    return render(request, 'inventory/edit_drug.html', {'form': form})

def delete_drug(request, drug_id):
    drug = get_object_or_404(Drug, pk=drug_id)
    if request.method == 'POST':
        drug.delete()
        messages.success(request, "Drug deleted successfully!")
        return redirect('admin_dashboard')
    return render(request, 'inventory/delete_drug.html', {'drug': drug})


def add_drug(request):
    if request.method == 'POST':
        form = DrugForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New drug added successfully!")
            return redirect('admin_dashboard')
    else:
        form = DrugForm()
    return render(request, 'inventory/add_drug.html', {'form': form})

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New category added successfully!")
            return redirect('add_drug')  # Redirect back to the add drug page
    else:
        form = CategoryForm()
    return render(request, 'inventory/add_category.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after signup
            messages.success(request, "Signup successful!")
            return redirect('dashboard_redirect')  # Redirect to the dashboard_redirect view
    else:
        form = CustomUserCreationForm()
    return render(request, 'inventory/signup.html', {'form': form})
