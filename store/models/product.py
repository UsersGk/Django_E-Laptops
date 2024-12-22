from django.db import models
from .category import Category


class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=200, default='')  # Changed 'Description' to 'description' for consistency
    image = models.ImageField(upload_to='upload/product/')

    @staticmethod
    def get_all_products():
        return Product.objects.all()  # Corrected to return all products
    @staticmethod
    def get_all_product_by_category_id(category_id):
        if category_id:
            return Product.objects.filter(category=category_id)
        else:
            return Product.objects.all()

    def __str__(self):
        return self.name  # Corrected to return the product name


# Example usage
# print(Product.objects.all())  # This will print the queryset of all products
