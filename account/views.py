from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token


def account(request):
	"""
	Render account page with login/logout functionality.
	Initial state depends on user authentication.
	"""
	# Get CSRF token for AJAX requests
	csrf_token = get_token(request)
	context = {
		'csrf_token': csrf_token,
	}
	return render(request, 'account/account.html', context)


@require_http_methods(["POST"])
def login_view(request):
	"""
	Handle AJAX login requests.
	Returns JSON with authentication result.
	"""
	form = AuthenticationForm(request, data=request.POST)
	
	if form.is_valid():
		user = form.get_user()
		login(request, user)
		return JsonResponse({
			'success': True,
			'username': user.username,
			'message': 'Login successful'
		})
	else:
		# Collect form errors
		errors = {}
		for field, field_errors in form.errors.items():
			errors[field] = list(field_errors)
		
		return JsonResponse({
			'success': False,
			'errors': errors,
			'message': 'Login failed'
		}, status=400)


@require_http_methods(["POST"])
def logout_view(request):
	"""
	Handle AJAX logout requests.
	Returns JSON confirmation.
	"""
	logout(request)
	return JsonResponse({
		'success': True,
		'message': 'Logout successful'
	})


@require_http_methods(["GET"])
def auth_status(request):
	"""
	Check current authentication status.
	Returns JSON with user info if authenticated.
	"""
	if request.user.is_authenticated:
		return JsonResponse({
			'authenticated': True,
			'username': request.user.username
		})
	else:
		return JsonResponse({
			'authenticated': False
		})
