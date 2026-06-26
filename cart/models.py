from django.db import models
from products.models import Product
from django.contrib.auth.models import User
import uuid


# -------------------------
# Base Model (Reusable)
# -------------------------
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


# -------------------------
# Cart Model
# -------------------------
class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Cart"

    # Cart total price (IMPORTANT FIX)
    @property
    def total_price(self):
        return sum(item.total_price for item in self.cart_items.all())

# Cart Item Model
class CartItem(BaseModel):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.product.product_name

    # Total price for single item
    @property
    def total_price(self):
        return self.product.price * self.quantity

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product'],
                name='unique_cart_product'
            )
        ]