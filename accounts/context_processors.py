def role_flags(request):
    user = request.user
    is_manager = False
    if user.is_authenticated:
        is_manager = user.groups.filter(name="Менеджеры").exists()
    return {"is_manager": is_manager}