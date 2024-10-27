from django.db import models

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
    available_stock = models.PositiveIntegerField()
    stock_updated_on = models.DateTimeField(auto_now=True)
    stock_status = models.BooleanField(default=True)

    def update_stock(self, quantity):
        self.available_stock -= quantity
        self.stock_status = self.available_stock > 0
        self.save()

    def __str__(self):
        return f"{self.drug.drug_name} - Stock: {self.available_stock}"

class UserOrder(models.Model):
    order_id = models.AutoField(primary_key=True)
    order_date = models.DateTimeField(auto_now_add=True)
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Update stock based on order quantity
        stock = Stock.objects.get(drug=self.drug)
        if stock.available_stock >= self.quantity:
            stock.update_stock(self.quantity)
            self.total_amount = self.price * self.quantity
            super().save(*args, **kwargs)
        else:
            raise ValueError("Insufficient stock")

    def __str__(self):
        return f"Order {self.order_id} - {self.drug.drug_name}"
