from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from accounts.models import Customer, User, SearchHistory, Notification
from boards.models import Board
from .models import Brand, BrandRepresentative, Category, Product
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login, authenticate
from django.db.models.functions import Coalesce
from lib.recommendations import RecommendationEngine


def product_list(request):
    products = Product.objects.all()
    # Filters
    search_query = request.GET.get('q')
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    color = request.GET.get('color')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', 'title')  # e.g., 'price', '-price'

    # Save search query if user is authenticated
    if search_query and request.user.is_authenticated:
        SearchHistory.objects.create(user=request.user, query=search_query)

    if search_query:
        products = products.filter(title__icontains=search_query)

    if category:
        try:
            category_id = int(category)
            products = products.filter(category_id=category_id)
        except (ValueError, TypeError):
            pass

    if brand:
        if brand.isdigit():
            products = products.filter(brand__id=int(brand))
        else:
            products = products.filter(brand__name__iexact=brand)

    if color:
        products = products.filter(color__iexact=color)

    try:
        if min_price:
            products = products.filter(price__gte=float(min_price))
        if max_price:
            products = products.filter(price__lte=float(max_price))
    except ValueError:
        pass

    if sort_by in ['price', '-price', 'title', '-title', 'created_at', '-created_at']:
        products = products.order_by(sort_by)

    # Get colors from model choices
    colors = [choice[0] for choice in Product.COLOR_CHOICES]

    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Get wishlist IDs for the current user
    wishlist_ids = []
    if request.user.is_authenticated and hasattr(request.user, 'customer'):
        wishlist_ids = list(request.user.customer.wishlist.values_list('id', flat=True))

    context = {
        'products': page_obj,
        'wishlist_ids': wishlist_ids,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'colors': colors,
        'description': "Discover our curated collection of fashion items",
        'search_query': search_query,
        'selected_category': category,
        'selected_brand': brand,
        'selected_color': color,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }

    return render(request, 'products/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    customer = Customer.objects.get(user=request.user) if request.user.is_authenticated else None
    boards = Board.objects.filter(customer=customer) if request.user.is_authenticated else []
    
    # Record the view if user is authenticated
    if request.user.is_authenticated:
        engine = RecommendationEngine()
        engine.record_view(request.user.id, product.id)
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'boards': boards
    })

def create_product(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')
        color = request.POST.get('color')

        category = Category.objects.get(pk=category_id) if category_id else None

        Product.objects.create(
            title=title,
            description=description,
            price=price,
            category=category,
            image=image,
            color=color
        )

        return redirect('product_list')


def brand_rep_signup(request):
    if request.method == 'POST':
        # Get all form data
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        brand_name = request.POST.get('brand_name')
        website = request.POST.get('website', '')

        # Basic validation
        if not all([email, password, full_name, phone_number, brand_name]):
            messages.error(request, 'Please fill all required fields')
            return redirect('brand_rep_signup')

        try:
            # Create brand first
            brand = Brand.objects.create(
                name=brand_name,
                website=website,
                is_approved=False  # Brand needs admin approval
            )

            # Create user
            user = User.objects.create(
                email=email,
                password=make_password(password),
                full_name=full_name,
                user_type='BRAND_REPRESENTATIVE',
                is_active=False  # Requires admin approval
            )

            # Create brand representative
            BrandRepresentative.objects.create(
                user=user,
                brand=brand,
                phone_number=phone_number
            )

            messages.success(request, 'Registration successful! Waiting for admin approval.')
            return redirect('brand_rep_login')

        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')

    return render(request, 'brandrep/signup.html')


def brand_rep_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None and user.is_active:
            try:
                brand_rep = BrandRepresentative.objects.get(user=user)
                login(request, user)
                return redirect('brand_dashboard')
            except BrandRepresentative.DoesNotExist:
                messages.error(request, 'No brand representative account found')
        else:
            messages.error(request,
                           'Invalid credentials or account not approved yet.')

    return render(request, 'brandrep/login.html')


@login_required
def brand_dashboard(request):
    try:
        brand_rep = BrandRepresentative.objects.get(user=request.user)

        # Get all products for this brand
        products = Product.objects.filter(brand=brand_rep.brand)

        # If you need to count wishlist users for each product
        products = products.annotate(
            wishlist_count=Count('wishlist_users')
        ).order_by('-created_at')

        return render(request, 'brandrep/dashboard.html', {
            'brand': brand_rep.brand,
            'products': products,
            'phone_number': brand_rep.phone_number
        })

    except BrandRepresentative.DoesNotExist:
        messages.error(request, 'You are not a registered brand representative')
        return redirect('logout')


@login_required
def add_product(request):
    try:
        brand_rep = BrandRepresentative.objects.get(user=request.user)

        if request.method == 'POST':
            # Get form data
            title = request.POST.get('title')
            description = request.POST.get('description')
            price = request.POST.get('price')
            image = request.FILES.get('image')
            category_id = request.POST.get('category')
            color = request.POST.get('color')

            # Basic validation
            if not all([title, price, category_id]):
                messages.error(request, 'Please fill all required fields', extra_tags='add_product')
                return redirect('add_product')

            try:
                category = Category.objects.get(id=category_id)
                product = Product.objects.create(
                    title=title,
                    description=description,
                    price=price,
                    image=image,
                    category=category,
                    brand=brand_rep.brand,
                    color=color
                )

                # Create notifications for all customers
                customers = User.objects.filter(customer__isnull=False).exclude(id=request.user.id)
                for user in customers:
                    Notification.objects.create(
                        user=user,
                        type='new_product',
                        title='New Product Available',
                        message=f'{product.title} is now available!',
                        link=f'/products/{product.id}/'
                    )

                messages.success(request, 'Product added successfully!', extra_tags='add_product')
                return redirect('brand_dashboard')
            except Exception as e:
                messages.error(request, f'Error adding product: {str(e)}', extra_tags='add_product')

        categories = Category.objects.all()
        return render(request, 'brandrep/add_product.html', {'categories': categories})

    except BrandRepresentative.DoesNotExist:
        messages.error(request, 'You are not a registered brand representative')
        return redirect('logout')

@login_required
def view_product(request, product_id):
    try:
        brand_rep = BrandRepresentative.objects.get(user=request.user)
        product = get_object_or_404(Product, id=product_id, brand=brand_rep.brand)
        
        return render(request, 'brandrep/view_product.html', {
            'product': product,
            'brand': brand_rep.brand
        })
    except BrandRepresentative.DoesNotExist:
        messages.error(request, 'You are not a registered brand representative')
        return redirect('logout')

@login_required
def edit_product(request, product_id):
    try:
        brand_rep = BrandRepresentative.objects.get(user=request.user)
        product = get_object_or_404(Product, id=product_id, brand=brand_rep.brand)
        
        if request.method == 'POST':
            title = request.POST.get('title')
            description = request.POST.get('description')
            price = request.POST.get('price')
            category_id = request.POST.get('category')
            image = request.FILES.get('image')
            color = request.POST.get('color')
            
            if title and description and price and category_id:
                product.title = title
                product.description = description
                product.price = price
                product.category_id = category_id
                product.color = color
                if image:
                    product.image = image
                product.save()
                
                messages.success(request, 'Product updated successfully.', extra_tags='edit_product')
                return redirect('view_product', product_id=product.id)
            else:
                messages.error(request, 'Please fill in all required fields.', extra_tags='edit_product')
        
        return render(request, 'brandrep/edit_product.html', {
            'product': product,
            'categories': Category.objects.all(),
            'brand': brand_rep.brand
        })
    except BrandRepresentative.DoesNotExist:
        messages.error(request, 'You are not a registered brand representative')
        return redirect('logout')

@login_required
def delete_product(request, product_id):
    try:
        brand_rep = BrandRepresentative.objects.get(user=request.user)
        product = get_object_or_404(Product, id=product_id, brand=brand_rep.brand)
        product_title = product.title
        product.delete()
        
        messages.success(request, f'Product "{product_title}" has been deleted.', extra_tags='delete_product')
        return redirect('brand_dashboard')
    except BrandRepresentative.DoesNotExist:
        messages.error(request, 'You are not a registered brand representative')
        return redirect('logout')
