from django.db import models
import uuid


class BaseModel(models.Model):

    uid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Restaurant(BaseModel):

    name = models.CharField(max_length=200)

    image = models.ImageField(
        upload_to='restaurants/'
    )

    # ADD THIS
    banner_image = models.ImageField(
        upload_to='restaurant_banners/',
        null=True,
        blank=True
    )

    address = models.TextField()

    rating = models.FloatField(default=0)

    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Category(BaseModel):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(BaseModel):

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,   
        related_name='products'                                
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True
    )

    product_name = models.CharField(max_length=200)

    slug = models.SlugField(unique=True)

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.product_name


class ProductImage(BaseModel):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(
        upload_to='product_images/'
    )