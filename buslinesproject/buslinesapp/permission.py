# chứng thực admin
from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_role = request.user.role

        return user_role == 'admin'


# chứng thực busowner
class IsBusOwnerRole(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_role = request.user.role

        return user_role == 'busowner'


# chứng thực khách hàng
class IsCustomerRole(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_role = request.user.role

        return user_role == 'customer'


# chứng thực nhân viên
class IsEmployeeRole(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_role = request.user.role

        return user_role == 'employee'