from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Drug, Stock, Category, Cart, CartItem, UserOrder

User = get_user_model()


class InventoryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up initial data for tests that is shared among all test methods
        cls.client = Client()
        cls.category = Category.objects.create(category_name="Painkillers")

        # Create Drug
        cls.drug = Drug(
            drug_name="Aspirin",
            category=cls.category,
            price=10.00,
            discount=20.00
        )
        cls.drug.save()  # Explicitly save the drug to assign the ID

        # Debugging info to check if drug was created successfully
        print(f"Drug created in setUpTestData: pk={cls.drug.pk}, name={cls.drug.drug_name}")

        cls.stock = Stock.objects.create(drug=cls.drug, available_stock=100, stock_status=True)

        # Create a user and a staff user
        cls.user = User.objects.create_user(username='testuser', password='password')
        cls.staff_user = User.objects.create_superuser(username='staffuser', password='password')

    def test_drug_list_view(self):
        # Test the drug list view
        response = self.client.get(reverse('drug_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/drug_list.html')
        self.assertContains(response, 'Aspirin')

    def test_add_to_cart_view_authenticated(self):
        # Ensure the Drug object has an ID before proceeding
        self.assertIsNotNone(self.drug.pk, "Drug object is not saved correctly and has no ID.")

        # Login with user credentials
        self.client.login(username='testuser', password='password')

        # Attempt to add the drug to the cart
        response = self.client.post(reverse('add_to_cart', args=[self.drug.pk]), {'quantity': 2})

        # Check the response and the CartItem
        self.assertEqual(response.status_code, 302)  # Should redirect after adding to cart
        cart = Cart.objects.get(user=self.user)
        cart_item = CartItem.objects.get(cart=cart, drug=self.drug)
        self.assertEqual(cart_item.quantity, 2)

    def test_add_to_cart_view_unauthenticated(self):
        # Ensure the Drug object has an ID before proceeding
        self.assertIsNotNone(self.drug.pk, "Drug object is not saved correctly and has no ID.")

        # Attempt to add to cart without login
        response = self.client.post(reverse('add_to_cart', args=[self.drug.pk]), {'quantity': 2})
        self.assertEqual(response.status_code, 302)  # Should redirect to login page

    def test_view_cart_view(self):
        # Test viewing the cart page
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('cart'))  # Updated to match the correct URL name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/view_cart.html')

    def test_checkout_view_empty_cart(self):
        # Test trying to checkout with an empty cart
        self.client.login(username='testuser', password='password')

        # Ensure the user has an empty cart by creating it
        Cart.objects.get_or_create(user=self.user)

        # Now proceed to checkout with an empty cart
        response = self.client.post(reverse('checkout'))

        # Check if the response is a redirect to the cart page due to the empty cart
        self.assertEqual(response.status_code, 302)  # Should redirect since the cart is empty
        self.assertRedirects(response, reverse('cart'))  # Check that the redirect is to the cart page

        # Check for error messages in the response
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any(message.message == "Your cart is empty." for message in messages))

    def test_checkout_view_with_items(self):
        # Test checking out with items in the cart
        self.client.login(username='testuser', password='password')
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, drug=self.drug, quantity=5)

        response = self.client.post(reverse('checkout'))
        self.assertEqual(response.status_code, 302)  # Should redirect to order confirmation
        user_order = UserOrder.objects.filter(user=self.user).first()
        self.assertIsNotNone(user_order)
        self.assertEqual(user_order.total_amount, 5 * self.drug.price_after_discount)

    def test_admin_dashboard_access_as_non_staff(self):
        # Login as non-staff user and try to access the admin dashboard
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login or another page
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('admin_dashboard')}")

    def test_admin_dashboard_access_as_non_staff(self):
        # Login as non-staff user and try to access the admin dashboard
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Should redirect since non-staff cannot access it
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('admin_dashboard')}")

    def test_order_drug_insufficient_stock(self):
        # Test ordering more than available stock
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('order_drug', args=[self.drug.pk]), {'quantity': 150})
        self.assertEqual(response.status_code, 302)  # Should redirect due to insufficient stock
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any(message.message == "Insufficient stock available." for message in messages))

    def test_signup_view_user(self):
        # Test signing up a new user with all required fields
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',  # Include email if it's a required field
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'role': 'user'
        })

        # If the form fails, print out the errors for debugging
        if response.status_code == 200:
            form = response.context.get('form')
            if form:
                print("Form is invalid. Errors:", form.errors)

        # Assert the user was redirected after a successful signup
        self.assertEqual(response.status_code, 302)  # Should redirect after signup

        # Verify that the new user exists in the database
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signup_view_admin(self):
        # Test signing up a new user with all required fields
        response = self.client.post(reverse('signup'), {
            'username': 'newuseradmin',
            'email': 'newuseradmin@example.com',  # Include email if it's a required field
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'role': 'admin'
        })

        # If the form fails, print out the errors for debugging
        if response.status_code == 200:
            form = response.context.get('form')
            if form:
                print("Form is invalid. Errors:", form.errors)

        # Assert the user was redirected after a successful signup
        self.assertEqual(response.status_code, 302)  # Should redirect after signup

        # Verify that the new user exists in the database
        self.assertTrue(User.objects.filter(username='newuseradmin').exists())


