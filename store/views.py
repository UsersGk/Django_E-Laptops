from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models.product import Product
from .models.category import Category
from .models.customer import Customer
from .models.cart import Cart
from django.contrib import messages
import re
from django.db.models import Q
from django.contrib.auth import logout
from .models.order import Orderdetail
import requests
import json
from django.shortcuts import redirect
from django.http import JsonResponse
import logging
import uuid


# Create your views here.


# def home(request):
#     product = None
#     if request.session.has_key('email'):
#         email = request.session.get('email')
#         category = Category.get_all_category()
#         categoryId = request.GET.get('category')
#         customer = Customer.objects.filter(email=email)
#         print(categoryId)
#         name = None
#         for c in customer:
#             name = c.name
#         if categoryId:
#             product = Product.get_all_product_by_category_id(categoryId)
#         else:
#             product = Product.get_all_products()
#
#         data = {}
#         data['name'] = name
#         data['product'] = product
#         data['category'] = category
#         return render(request, 'home.html', data)
#     else:
#         return redirect('login')
def home(request):
    product = None
    email = None
    if request.session.has_key('email'):
        email = request.session.get('email')  # Get session email if exists
    category = Category.get_all_category()
    categoryId = request.GET.get('category')
    customer = None
    name = None

    # Fetch user name if logged in
    if email:
        customer = Customer.objects.filter(email=email).first()
        if customer:
            name = customer.name

    # Filter products based on category
    if categoryId:
        product = Product.get_all_product_by_category_id(categoryId)
    else:
        product = Product.get_all_products()

    # Prepare data for the template
    data = {
        'name': name,
        'product': product,
        'category': category
    }
    return render(request, 'home.html', data)


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html')
    else:
        postdata = request.POST
        name = postdata.get('name')
        email = postdata.get('email')
        password = postdata.get('password')
        confirm = postdata.get('confirm')
        customer = Customer(name=name, email=email, password=password)
        # validation
        error_message = None
        value = {
            name: 'name',
            email: 'email',
            password: 'password',
            confirm: 'confirm'
        }
        if not name:
            error_message = "Name is required"
        elif not email:
            error_message = "Email is required"
        elif customer.isExist():
            error_message = "Email is already exists"
        elif not password:
            error_message = "Password is required"
        elif not confirm:
            error_message = "Confirm is required"
        # Check if password and confirmation match
        elif password != confirm:
            error_message = "Passwords do not match"
        elif len(password) < 8:
            error_message = "Password must be at least 8 characters long"
        elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            error_message = "Password must include at least one special character"
        # Create a new customer instance (assuming the model takes these fields)

        if not error_message:
            messages.success(request, "Congratulation !! Resister successfully")
            customer.register()
            return redirect('signup')
        else:
            data = {
                'error': error_message,
                'value': value
            }
            return render(request, 'signup.html', data)


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        postdata = request.POST
        email = postdata.get('email')
        password = postdata.get('password')
        # customer = Customer(email=email, password=password)
        # validation
        request.session['email'] = email
        error_message = None
        value = {
            email: 'email',
            password: 'password'
        }
        if not email:
            error_message = "Email is required"
        elif not password:
            error_message = "Password is required"
        # Check if password and confirmation match
        elif len(password) < 8:
            error_message = "Password must be at least 8 characters long"
        elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            error_message = "Password must include at least one special character"
        # Create a new customer instance (assuming the model takes these fields)
        if error_message:
            data = {
                'error': error_message,
                'value': value

            }
            return render(request, 'login.html', data)
        else:
            if email and password:
                user = Customer.objects.filter(Q(email=email) & Q(password=password))
                data = user.count()
                if data == 1:
                    return redirect('home')
                else:
                    return render(request, 'signup.html')


def productdetails(request, pk):
    product = Product.objects.get(pk=pk)
    totalitem = 0
    item_already_in_cart = False
    if request.session.has_key('email'):
        email = request.session["email"]
        totalitem = len(Cart.objects.filter(email=email))
        item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(email=email)).exists()
        customer = Customer.objects.filter(email=email)
        name = None
        for c in customer:
            name = c.name
        data = {
            'name': name,
            'product': product,
            'item_already_in_cart': item_already_in_cart,
        }
        return render(request, 'productdetails.html', data)
    else:
        return redirect("login")


def logout(request):
    print("hello")
    print(request.session.get('email'))
    if request.session.has_key('email'):
        request.session.flush()
        return redirect('login')
    else:
        return redirect('login')


def add_to_cart(request):
    email = request.session['email']
    product_id = request.GET.get('prod_id')
    print("hello")
    print(product_id)
    if product_id:
        product_name = Product.objects.get(id=product_id)
        print(product_id)
        print("hello")
        product = Product.objects.filter(id=product_id)

        for p in product:
            image = p.image
            price = p.price
            Cart(email=email, product=product_name, image=image, price=price).save()
            return redirect(f"/product_details/{product_id}")


def show_cart(request):
    if 'email' not in request.session:
        # Handle the case where the user is not logged in
        return render(request, 'show_cart.html', {'name': None, 'totalitem': 0, 'cart': []})

    email = request.session.get('email')
    print(email)

    # Retrieve the cart items and customer information
    cart_items = Cart.objects.filter(email=email)
    totalitem = cart_items.count()
    id = uuid.uuid4()
    customer = Customer.objects.filter(email=email).first()
    name = customer.name if customer else None
    print(name)
    print(cart_items)
    # Prepare the context data
    data = {
        'name': name,
        'totalitem': totalitem,
        'cart': cart_items,
        'uuid': id,
    }
    if cart_items:
        # Retrieve customer name
        # Render the template with data
        return render(request, 'show_cart.html', data)
    else:
        return render(request, 'empty.html', data)


def plus_cart(request):
    if request.session.has_key('email'):
        email = request.session["email"]
        product_id = request.GET.get('prod_id')
        print(product_id)
        try:
            cart = Cart.objects.get(Q(id=product_id) & Q(email=email))
            cart.quantity += 1
            cart.save()
            data = {
                'quantity': cart.quantity,
            }
            return JsonResponse(data)
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found'}, status=404)
    else:
        return JsonResponse({'error': 'Please login first'}, status=401)


def minus_cart(request):
    if request.session.has_key('email'):
        email = request.session["email"]
        product_id = request.GET.get('prod_id')
        print(product_id)
        try:
            cart = Cart.objects.get(Q(id=product_id) & Q(email=email))
            cart.quantity -= 1
            cart.save()
            data = {
                'quantity': cart.quantity,
            }
            return JsonResponse(data)
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found'}, status=404)
    else:
        return JsonResponse({'error': 'Please login first'}, status=401)


def remove_cart(request):
    if request.session.has_key('email'):
        email = request.session["email"]
        product_id = request.GET.get('prod_id')
        print(product_id)
        try:
            cart = Cart.objects.get(Q(id=product_id) & Q(email=email))
            cart.delete()
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found'}, status=404)
    else:
        return JsonResponse({'error': 'Please login first'}, status=401)


def checkout(email, mobile, name):
    # if 'email' in request.session:
    # email = request.session['email']
    # name = request.POST.get('Name')
    # address = request.POST.get('address')
    # mobile = request.POST.get('mobile')

    # Print to check if data is being passed correctly
    #  print(f"Name: {name},Mobile: {mobile}, Email: {email}")
    print(f"Name: {name},Mobile: {mobile}, Email: {email}")

    # Get the cart items for the current user
    cart_product = Cart.objects.filter(email=email)

    # Check if there are cart items
    if not cart_product.exists():
        return HttpResponse("Your cart is empty.", status=400)

    # Iterate over cart items and create orders
    for c in cart_product:
        qty = c.quantity
        price = c.price
        product_name = c.product
        image = c.image

        # Debug: Check what data is being passed
        print(f"Saving Order: {product_name}, Quantity: {qty}, Price: {price}")
        print("hey")
        data = {
            email: 'email'
        }
        try:
            # Save order details
            print("hello")
            Orderdetail(user=email, product_name=product_name, image=image, qty=qty, price=price).save()
        except Exception as e:
            print(f"Error saving order: {e}")

        # Delete the cart item after saving order
        cart_product.delete()

    # Redirect or render after checkout (maybe show a success page)
    return redirect('show_cart.html')  # You may want to show a success page instead


def order(request):
    if 'email' in request.session:
        email = request.session['email']

        # Get the User object using the email
        user = Customer.objects.filter(email=email).first()
        print(user)
        # If no user is found with this email, handle the case
        if not user:
            return HttpResponse("User not found.", status=404)

        total_item = Cart.objects.filter(email=email).count()  # Count items in the cart
        order = Orderdetail.objects.filter(user=email)  # Filter by User object, not email
        print(total_item)
        print(order)

        data = {
            'order': order,
            'name': email,  # Assuming the user has a 'username' or 'name' attribute
            'total_item': total_item
        }
        print(data)
        # Return the appropriate template based on whether the user has orders
        if order:
            return render(request, 'order.html', data)
        else:
            return render(request, 'empty_order.html', data)
    else:
        return HttpResponse("User not logged in.", status=401)


def search(request):
    total_item = 0
    if 'email' in request.session:
        email = request.session['email']
        query = request.GET.get('query', '')  # Default to an empty string if no query parameter
        search_results = Product.objects.filter(name__icontains=query)  # Case-insensitive search
        category = Category.objects.all()  # Assuming Category model has a default `objects` manager
        total_item = Cart.objects.filter(email=email).count()  # Count items in the cart
        user = Customer.objects.filter(email=email).first()

        data = {
            'email': email,
            'total_item': total_item,
            'search_results': search_results,  # Lowercase for Python naming convention
            'category': category,
            'query': query
        }
        return render(request, 'search.html', data)
    else:
        return redirect('login')

    # khalti payment intergration


def initkhalti(request):
    if request.method == 'POST':
        # Get the data from the POST request
        url = "https://a.khalti.com/api/v2/epayment/initiate/"
        return_url = request.POST.get('return_url')
        website_url = request.POST.get('return_url')

        amt = float(request.POST.get('amount'))
        purchase_order_id = request.POST.get('purchase_order_id')
        name = request.POST.get('Name')
        email = request.POST.get('email')
        mobile = request.POST.get('Mobile')
        amount = 0  # Initialize the amount variable

        if amt > 100000:
            amount = amt / 100  # Convert to integer after division
        elif amt > 5000:
            amount = amt / 10  # Convert to integer after division
        else:
            amount = 1000

        print(email)

        print(amount)

        checkout(
            email=email,
            mobile=mobile,
            name=name
        )

        # Validate inputs
        if not all([return_url, website_url, amount, purchase_order_id]):
            return JsonResponse({"error": "Missing required fields."}, status=400)

        # Prepare payload
        payload = json.dumps({
            "return_url": return_url,
            "website_url": website_url,
            "amount": amount,
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": "Test Order",
            "customer_info": {
                "name": name,
                "email": email,
                "phone": mobile
            }
        })

        # Headers for the API request
        headers = {
            'Authorization': 'key b5995fb8c9344eafa9d619ef0babd096',
            'Content-Type': 'application/json',
        }

        # Make the POST request to Khalti
        response = requests.post(url, headers=headers, data=payload)
        new_res = json.loads(response.text)

        # Debug logs
        print("API Response:", new_res)

        # Check if the payment URL is provided
        if response.status_code == 200 and 'payment_url' in new_res:
            return redirect(new_res['payment_url'])

        else:
            return JsonResponse({"error": "Payment initiation failed.", "details": new_res, "amount": amount},
                                status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)


# from django.http import JsonResponse
# import json
# import requests


def verifyKhalti(request):
    if request.method == 'GET':
        url = "https://a.khalti.com/api/v2/epayment/lookup/"
        headers = {
            'Authorization': 'key b5995fb8c9344eafa9d619ef0babd096',
            'Content-Type': 'application/json',
        }
        pidx = request.GET.get('pidx')

        if not pidx:
            return JsonResponse({
                "error": "Missing required parameter 'pidx'."
            }, status=400)

        data = json.dumps({
            'pidx': pidx
        })

        # Send request to Khalti API
        res = requests.post(url, headers=headers, data=data)
        try:
            new_res = res.json()  # Convert API response to JSON
        except json.JSONDecodeError:
            return JsonResponse({
                "error": "Invalid response from Khalti API."
            }, status=500)

        print(new_res)  # For debugging

        # Check the transaction status
        if new_res['status'] == 'Completed':
            # user = request.user

            # user.has_verified_dairy = True
            # user.save()
            # perform your db interaction logic
            message = "Thank you for purchasing via Khalti Payment Gateway! Your payment has been confirmed successfully."
            return render(request, 'message_page.html', {'message': message, 'duration': 30})
            pass

            # else:
            #     # give user a proper error message
            #     raise BadRequest("sorry ")

        return redirect('home')
