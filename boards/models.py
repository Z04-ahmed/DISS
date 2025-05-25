from django.db import models
from django.contrib.auth.models import User

from accounts.models import Customer  # Import your Customer model


class Board(models.Model):
	VISIBILITY_CHOICES = [
		('public', 'Public'),
		('private', 'Private'),
	]

	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Changed from user to customer
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	cover_image = models.ImageField(upload_to='board_covers/', blank=True, null=True)
	visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name


class BoardItem(models.Model):
	board = models.ForeignKey(Board, on_delete=models.CASCADE)
	product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
	added_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ['board', 'product']  # Prevent duplicate products in board
