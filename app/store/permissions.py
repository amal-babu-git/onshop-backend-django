from rest_framework import permissions

# Create custom psermission class
# GET method is available for all users, but POST,PUT available only for staff or admin user


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

# Custom pemission for view custmer history; flow for edit thr code--> Customer model,permissions.py, customer viewset
class ViewCustomerHistoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        #                             app_name.permission_name
        return request.user.has_perm('store.view_history')


class FullDjangoModelPermissions(permissions.DjangoModelPermissions):

    def __init__(self) -> None:
        # View permission necessary for get request, we only use this for customer viewset
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']

