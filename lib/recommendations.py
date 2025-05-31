from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from products.models import Product
from accounts.models import ProductView, SearchHistory


class RecommendationEngine:
	def __init__(self):
		self.max_recommendations = 6

	def record_view(self, user_id, product_id):
		try:
			# Update existing view timestamp or create new view
			view, created = ProductView.objects.get_or_create(
				user_id=user_id,
				product_id=product_id,
				defaults={'viewed_at': timezone.now()}
			)
			if not created:
				view.viewed_at = timezone.now()
				view.save()
		except Exception as e:
			print(f"Error recording view: {str(e)}")

	def get_recommendations(self, user_id):
		try:
			print(f"Starting recommendation process for user {user_id}")
			
			# Get user's recent views (last 30 days)
			recent_views = ProductView.objects.filter(
				user_id=user_id,
				viewed_at__gte=timezone.now() - timedelta(days=30)
			).values_list('product_id', flat=True)

			# Get user's recent searches (last 30 days)
			recent_searches = SearchHistory.objects.filter(
				user_id=user_id,
				created_at__gte=timezone.now() - timedelta(days=30)
			).order_by('-created_at')[:5]  # Get 5 most recent searches

			if not recent_views and not recent_searches:
				print("No recent activity, returning trending products")
				return Product.objects.filter(is_trending=True)[:self.max_recommendations]

			# Collect all potential recommendations
			all_recommendations = []

			# First priority: Products matching recent searches
			if recent_searches:
				search_query = Q()
				for search in recent_searches:
					search_query |= Q(title__icontains=search.query) | Q(description__icontains=search.query)
				search_products = list(Product.objects.filter(search_query))
				print(f"Found {len(search_products)} products matching searches")
				all_recommendations.extend(search_products)

			# Second priority: Products in same categories as viewed products
			if recent_views:
				viewed_products = Product.objects.filter(id__in=recent_views)
				category_ids = viewed_products.values_list('category_id', flat=True)
				category_products = list(Product.objects.filter(category_id__in=category_ids).exclude(id__in=recent_views))
				all_recommendations.extend(category_products)

			# Third priority: Products often viewed with user's viewed products
			if recent_views:
				co_viewed = list(Product.objects.filter(
					productview__product_id__in=recent_views
				).exclude(
					id__in=recent_views
				).annotate(
					view_count=Count('productview')
				).order_by('-view_count'))
				print(f"Found {len(co_viewed)} co-viewed products")
				all_recommendations.extend(co_viewed)

			# Remove duplicates while preserving order
			seen_ids = set()
			unique_recommendations = []
			for product in all_recommendations:
				if product.id not in seen_ids:
					seen_ids.add(product.id)
					unique_recommendations.append(product)

			# If we don't have enough recommendations, add trending products
			if len(unique_recommendations) < self.max_recommendations:
				print("Adding trending products to fill recommendations")
				trending = list(Product.objects.filter(is_trending=True).exclude(
					id__in=seen_ids
				)[:self.max_recommendations - len(unique_recommendations)])
				unique_recommendations.extend(trending)

			final_recommendations = unique_recommendations[:self.max_recommendations]
			print(f"Returning {len(final_recommendations)} final recommendations")
			return final_recommendations

		except Exception as e:
			print(f"Error getting recommendations: {str(e)}")
			# Fallback to trending products
			return Product.objects.filter(is_trending=True)[:self.max_recommendations]
