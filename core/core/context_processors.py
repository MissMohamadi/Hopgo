def context(request):
    # stuff needed before defining context
    context = {
        'canonical_path': request.build_absolute_uri(request.path),
        # any other context variables needed
    }
    return context