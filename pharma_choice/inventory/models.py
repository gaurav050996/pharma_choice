from django.db import models
from django.conf import settings
from django.db import models

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name

class Drug(models.Model):
    drug_id = models.AutoField(primary_key=True)
    drug_name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    stock_status = models.BooleanField(default=True)

    @property
    def price_after_discount(self):
        return self.price - (self.price * self.discount / 100)

    def __str__(self):
        return self.drug_name

class Stock(models.Model):
    stock_id = models.AutoField(primary_key=True)
    drug = models.OneToOneField(Drug, on_delete=models.CASCADE)
    available_stock = models.PositiveIntegerField(default=0)
    stock_updated_on = models.DateTimeField(auto_now=True)
    stock_status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Update stock status based on availability
        self.stock_status = self.available_stock > 0
        super().save(*args, **kwargs)

    def update_stock(self, quantity):
        # Update available stock and stock status
        self.available_stock -= quantity
        self.save()

    def __str__(self):
        return f"{self.drug.drug_name} - Stock: {self.available_stock} - Status: {'In Stock' if self.stock_status else 'Out of Stock'}"

class UserOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class OrderItem(models.Model):
    order = models.ForeignKey(UserOrder, related_name='items', on_delete=models.CASCADE)
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')

    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_item_price(self):
        return self.quantity * self.drug.price_after_discount

    def __str__(self):
        return f"{self.quantity} of {self.drug.drug_name}"
