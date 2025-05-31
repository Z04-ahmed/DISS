from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate
from .forms import BrandRepresentativeSignUpForm
from products.models import Product, Category
from django.db.models import Count
from django.db.models.functions import Coalesce

@login_required
def manage_products(request):
    if not hasattr(request.user, 'brandrepresentative'):
        messages.error(request, 'You do not have permission to access this page.', extra_tags='manage_products')
        return redirect('home')
    
    products = Product.objects.filter(
        brand=request.user.brandrepresentative.brand
    ).annotate(
        saves_count=Coalesce(Count('saves'), 0),
        views_count=Coalesce(Count('views'), 0)
    ).order_by('-created_at')
    
    context = {
        'products': products,
    }
    return render(request, 'brandrep/manage_products.html', context)

@login_required
def view_product(request, product_id):
    if not hasattr(request.user, 'brandrepresentative'):
        messages.error(request, 'You do not have permission to access this page.', extra_tags='manage_products')
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id, brand=request.user.brandrepresentative.brand)
    context = {
        'product': product,
    }
    return render(request, 'brandrep/view_product.html', context)

@login_required
def edit_product(request, product_id):
    if not hasattr(request.user, 'brandrepresentative'):
        messages.error(request, 'You do not have permission to access this page.', extra_tags='manage_products')
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id, brand=request.user.brandrepresentative.brand)
    
    if request.method == 'POST':
        # Handle product update
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')
        
        if title and description and price and category_id:
            product.title = title
            product.description = description
            product.price = price
            product.category_id = category_id
            if image:
                product.image = image
            product.save()
            
            messages.success(request, 'Product updated successfully.', extra_tags='manage_products')
            return redirect('manage_products')
        else:
            messages.error(request, 'Please fill in all required fields.', extra_tags='manage_products')
    
    context = {
        'product': product,
        'categories': Category.objects.all(),
    }
    return render(request, 'brandrep/edit_product.html', context)

@login_required
def delete_product(request, product_id):
    if not hasattr(request.user, 'brandrepresentative'):
        messages.error(request, 'You do not have permission to access this page.', extra_tags='manage_products')
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id, brand=request.user.brandrepresentative.brand)
    product_title = product.title
    product.delete()
    
    messages.success(request, f'Product "{product_title}" has been deleted.', extra_tags='manage_products')
    return redirect('manage_products')
