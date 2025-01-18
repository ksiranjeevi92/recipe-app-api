from django.shortcuts import render,get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from product.serializers import ProductSerializer
from product.models import Product
from product.filters import ProductFilter
# Create your views here.
@api_view(['GET'])
def get_products(request):

    #products = Product.objects.all()

    filterset = ProductFilter(request.GET,queryset=Product.objects.all().order_by('id'))

    reqPerPage = 1

    paginator = PageNumberPagination()

    paginator.page_size = reqPerPage

    queryset = paginator.paginate_queryset(filterset.qs, request)

    count = filterset.qs.count()

    serailzier = ProductSerializer(queryset, many=True)

    return Response({'reqPerPage': reqPerPage,'count': count, 'products': serailzier.data})

@api_view(['GET'])
def get_product(request, pk):
    product = get_object_or_404(Product,id=pk)

    serializer = ProductSerializer(product,many=False)

    return Response({'product': serializer.data})