from django.db.models import Count
from products.models import Product
from accounts.models import ProductView


class RecommendationEngine:
	def __init__(self):
		self.max_recommendations = 6

	def record_view(self, user_id, product_id):
		ProductView.objects.get_or_create(
			user_id=user_id,
			product_id=product_id
		)

	def get_recommendations(self, user_id):
		# Get frequently viewed-with products (co-viewing)
		user_viewed = ProductView.objects.filter(
			user_id=user_id
		).values_list('product_id', flat=True)

		if not user_viewed:
			return Product.objects.filter(is_trending=True)[:self.max_recommendations]

		# Find products often viewed with the user's viewed products
		recommendations = Product.objects.filter(
			productview__product_id__in=user_viewed
		).exclude(
			id__in=user_viewed
		).annotate(
			view_count=Count('productview')
		).order_by('-view_count')[:self.max_recommendations]

		return recommendations
