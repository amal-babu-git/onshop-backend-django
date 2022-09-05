from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from store.admin import ProductAdmin, ProductImageInline
from store.models import Product
from tags.models import TaggedItem
from .models import User
# Register your models here.


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # adding additional information  fields too| this add_fieldsets from BaseUserAdmin
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "email", "first_name", "last_name",),
            },
        ),
    )


# This core is also app act as an intermediary between
# store and tags app
# Here we define the TagInline class for show tags inside the product panel.
# and create a CustomProductAdmin class which inherits from Productadmin in store app.and
# inside that we declared inline atribute then unregister the Product model and reregister
# with new CustomProductAdmin.
# This is why ? --> because we need to decoupled tags app from store app.
# so tags app is independent app from store. this custom store is intermediary betwwen them.

# Create an inline class for display TagItem inside product panel
class TagInline(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem
    extra: int = 1


class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline,ProductImageInline]


admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)
