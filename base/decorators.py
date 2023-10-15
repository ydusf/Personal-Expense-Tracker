from django.shortcuts import redirect


def guest_only(view_func):
    """
    Custom Django decorator to restrict access to a view function to unauthenticated (guest) users.

    Args:
        view_func (function): The view function to be decorated.

    Returns:
        function: The decorated view function that either redirects authenticated users to their profile or allows guest users to access the original view.
    """
    def _wrapped_view(request, *args, **kwargs):
        """
        The inner function that performs the access control.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable-length positional arguments.
            **kwargs: Variable-length keyword arguments.

        Returns:
            HttpResponse: Either a redirection to the user's profile if they are authenticated, or the result of the original view function if they are a guest.
        """
        if request.user.is_authenticated:
            # If the user is authenticated, redirect them to their profile page.
            return redirect("profile")
        else:
            # If the user is a guest, allow them to access the original view function.
            return view_func(request, *args, **kwargs)

    return _wrapped_view
