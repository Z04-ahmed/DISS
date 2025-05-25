from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Board, BoardItem
from products.models import Product
from accounts.models import Customer


@login_required
def create_board(request):
	if request.method == 'POST':
		try:
			# Get the customer profile for the current user
			customer = request.user.customer

			board = Board.objects.create(
				customer=customer,  # Use customer instead of user
				name=request.POST.get('name'),
				description=request.POST.get('description', ''),
				visibility=request.POST.get('visibility', 'public')
			)

			if 'cover_image' in request.FILES:
				board.cover_image = request.FILES['cover_image']
				board.save()

			messages.success(request, "Board created successfully!")
			return redirect('boards')

		except Exception as e:
			messages.error(request, f"Error creating board: {str(e)}")
			return render(request, 'boards/create_board.html')

	return render(request, 'boards/create_board.html')


@login_required
def boards_list(request):
	customer = request.user.customer
	boards = Board.objects.filter(customer=customer)
	return render(request, 'boards/board_list.html', {'boards': boards})


@login_required
def delete_board(request, board_id):
	if request.method == 'POST':
		board = get_object_or_404(Board, id=board_id, customer=request.user.customer)
		board.delete()
		messages.success(request, "Board deleted successfully!")
	return redirect('boards_list')


@login_required
def board_detail(request, pk):
	board = get_object_or_404(Board, pk=pk, customer=request.user.customer)

	board_items = BoardItem.objects.filter(board=board)

	return render(request, 'boards/board_detail.html', {
		'board': board,
		'board_items': board_items
	})


@login_required
def add_product_to_board(request):
	if request.method == 'POST':
		try:
			product_id = request.POST.get('product_id')
			board_id = request.POST.get('board_id')

			if not board_id:
				messages.error(request, "Please select a board")
				return redirect('board_detail', pk=board_id)

			product = get_object_or_404(Product, id=product_id)
			board = get_object_or_404(Board, id=board_id, customer=request.user.customer)

			if BoardItem.objects.filter(board=board, product=product).exists():
				messages.warning(request, "This product is already in your board!")
			else:
				BoardItem.objects.create(board=board, product=product)
				messages.success(request, f"Product added to {board.name}!")

			return redirect('board_detail', pk=board_id)

		except Exception as e:
			messages.error(request, f"Error adding product to board: {str(e)}")
			return redirect('board_detail', pk=board_id)

	return redirect('home')
