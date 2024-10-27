from django.shortcuts import render
from django.shortcuts import render, get_object_or_404,redirect

from .forms import DrugForm, CategoryForm
from .models import Drug, Stock, Category, UserOrder
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
from django.contrib import messages
from django.utils import timezone

class DrugListView(ListView):
    model = Drug
    template_name = 'inventory/drug_list.html'
    context_object_name = 'drugs'

    def get_queryset(self):
        return Drug.objects.filter(stock__stock_status=True).select_related('stock')

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
