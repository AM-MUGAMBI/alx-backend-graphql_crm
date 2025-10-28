import graphene
from .models import Product

class ProductType(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    stock = graphene.Int()

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass  # no input args needed

    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []

        for product in low_stock_products:
            product.stock += 10  # simulate restock
            product.save()
            updated_products.append(product)

        message = f"{len(updated_products)} products updated successfully"
        return UpdateLowStockProducts(updated_products=updated_products, message=message)


class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

