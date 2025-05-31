from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models.aggregates import Count
# from django.db.models.query_utils import Q
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST

from accounts.models import Customer, SearchHistory
from products.models import Category, Product
from lib.recommendations import RecommendationEngine


User = get_user_model()




def home_view(request):
    engine = RecommendationEngine()

    # Fetch categories and trending products
    categories = Category.objects.annotate(product_count=Count('product'))
    trending_products = Product.objects.filter(is_trending=True)[:6]
    all_products = Product.objects.all()

    # Track search if query exists
    if search_query := request.GET.get('q', ''):
        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, query=search_query)

    # Get recommendations
    recommendations = []
    if request.user.is_authenticated:
        print(f"Getting recommendations for user {request.user.id}")
        recommendations = engine.get_recommendations(request.user.id)
        print(f"Found {len(recommendations)} recommendations")
        for rec in recommendations:
            print(f"Recommendation: {rec.title}")

    # Get wishlist IDs for the current user
    wishlist_ids = []
    if request.user.is_authenticated and hasattr(request.user, 'customer'):
        wishlist_ids = list(request.user.customer.wishlist.values_list('id', flat=True))

    context = {
        "categories": categories,
        "trending_products": trending_products,
        "all_products": all_products,
        "search_query": search_query,
        "recommendations": recommendations,
        "wishlist_ids": wishlist_ids,
        "recent_searches": SearchHistory.objects.filter(user=request.user)[:5] if request.user.is_authenticated else []
    }
    return render(request, "accounts/home.html", context)


@require_POST
def record_view(request, product_id):
    if request.user.is_authenticated:
        RecommendationEngine().record_view(request.user.id, product_id)
    return JsonResponse({'status': 'success'})
# @login_required
# def home_view(request):
#     try:
#         # Fetch categories and trending products
#         categories = Category.objects.all()
#         trending_products = Product.objects.filter(is_trending=True)[:6]
#         all_products = Product.objects.all()
#
#         # Handle search
#         search_query = request.GET.get('q', '')
#         if search_query:
#             all_products = all_products.filter(
#                 Q(name__icontains=search_query) |
#                 Q(description__icontains=search_query)
#             )
#
#         # Get saved products for the current user
#         saved_product_ids = []
#         if request.user.is_authenticated and hasattr(request.user, 'customer'):
#             saved_product_ids = request.user.customer.saved_items.values_list('id', flat=True)
#
#         context = {
#             "categories": categories,
#             "trending_products": trending_products,
#             "all_products": all_products,
#             "saved_product_ids": list(saved_product_ids),
#             "search_query": search_query,
#         }
#
#         return render(request, "accounts/home.html", context)
#
#     except Exception as e:
#         # Handle errors gracefully (e.g., log the error and show an error page)
#         context = {"error": "An error occurred while loading the page."}
#         return render(request, "accounts/home.html", context)
#
#     except Exception as e:
#         # Handle any unexpected errors
#         from django.contrib import messages
#         messages.error(request, f"An error occurred: {str(e)}")
#         return render(request, "accounts/home.html", {})

def login_view(request):
    error = None

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('product_list')
        else:
            error = 'Invalid email or password.'

    return render(request, 'accounts/login.html', {'error': error})



def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'accounts/signup.html', {'error': 'Passwords do not match'})

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return render(request, 'accounts/signup.html', {'error': 'Email is already registered'})

        # Create user
        user = User.objects.create_user(
            email=email,
            full_name=full_name,
            password=password,
        )

        # Create associated Customer object
        Customer.objects.create(user=user)

        return redirect('login')

    return render(request, 'accounts/signup.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def favourite_products_view(request):
    favourite_products = request.user.customer.wishlist.all()
    context = {
        "favourite_products": favourite_products,
    }
    return render(request, "accounts/favourite_products.html", context)


@login_required
def profile_view(request):
    user = request.user
    context = {
        "profile_user": user,
    }
    return render(request, "accounts/profile.html", context)


@login_required
def update_profile_view(request):
    if request.method == 'POST':
        try:
            user = request.user
            user.full_name = request.POST.get('full_name', user.full_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            messages.success(request, 'Profile updated successfully!', extra_tags='edit_profile')
            return redirect('profile')

        except ValidationError as e:
            messages.error(request, str(e), extra_tags='edit_profile')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}', extra_tags='edit_profile')

    return render(request, "accounts/edit_profile.html", {
        "profile_user": request.user
    })


# accounts/views.py
@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    customer = request.user.customer

    if product in customer.wishlist.all():
        customer.wishlist.remove(product)
        action = 'removed'
    else:
        customer.wishlist.add(product)
        action = 'added'

    return JsonResponse({
        'status': 'success',
        'action': action,
        'wishlist_count': customer.wishlist.count()
    })


@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    request.user.customer.wishlist.remove(product)
    return redirect('favourites')
