from django.shortcuts import render,get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from product.serializers import ProductSerializer, ProductImageSerializer
from product.models import Product, ProductImages
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


@api_view(['POST'])
def new_product(request):
    data  = request.data

    serializer = ProductSerializer(data=data)

    if serializer.is_valid():

        product = Product.objects.create(**data)

        res = ProductSerializer(product,many=False)

        return Response({'product': res.data})
    else:
        return Response({'error': serializer.errors})

@api_view(["POST"])
def upload_product_images(request):
    data = request.data

    files = request.FILES.getlist('images')
    images = []
    for file in files:
        image = ProductImages.objects.create(product=Product(data['product']), image=file)
        images.append(image)

    serializer = ProductImageSerializer(images, many=True)

    return Response({'data' : serializer.data})

@api_view(["PUT"])
def update_product(request,pk):
    data = request.data

    product = get_object_or_404(Product, id=pk)

    product.name =  data['name']
    product.description= data['description']
    product.price= data['price']
    product.brand = data['brand']
    product.category = data['category']
    product.rating= data['rating']
    product.stock= data['stock']

    product.save()

    res = ProductSerializer(product, many=False)

    return Response({'product': res.data})

@api_view(["DELETE"])
def delete_product(request,pk):

    product = get_object_or_404(Product, id=pk)

    product.delete()

    return Response({'message': 'product deleted', },status=status.HTTP_200_OK)
