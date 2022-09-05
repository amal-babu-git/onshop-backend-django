from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes, action
from rest_framework.viewsets import ModelViewSet, ViewSet
from .serializers import CustomerSerializer
from store.models import Customer
from .models import Payment
import braintree
import razorpay

# Create your views here.

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id="w8t358bgkcbnqn6j",
        public_key="hntg7mkst68zkgc8",
        private_key="385d361019992664347be58a94bde933"
    )
)


# @csrf_exempt
@permission_classes([IsAuthenticated])
def generate_token(request):

    # pass client_token to your front-end
    user_id = request.user.id
    queryset = Customer.objects.get(user_id=user_id)
    customer_id = CustomerSerializer(queryset)
    client_token = gateway.client_token.generate()
    return JsonResponse({'client_token': client_token, 'success': True, 'customer_id': customer_id.data})


@csrf_exempt
@permission_classes([IsAuthenticated])
def process_payment(request):

    nonce_from_the_client = request.POST['paymentNonce']
    amount = request.POST['amount']

    result = gateway.transaction.sale({
        "amount": amount,
        "payment_method_nonce": nonce_from_the_client,
        "options": {
            "submit_for_settlement": True
        }
    })

    if (result.is_success):
        return JsonResponse({'success': result.is_success,
                             'transaction': {
                                 'id': result.transaction.id,
                                 'amount': result.transaction.amount
                             }
                             })
    else:
        JsonResponse({'error': True, 'success': False})


class PaymentBApiViewSet(ViewSet):

    permission_classes = [IsAuthenticated]

    # Braintree

    @csrf_exempt
    @action(detail=False, methods=['GET'])
    def gettoken(self, request):
        # pass client_token to your front-end
        user_id = request.user.id
        queryset = Customer.objects.get(user_id=user_id)
        customer = CustomerSerializer(queryset)
        client_token = gateway.client_token.generate()
        return Response({'client_token': client_token, 'success': True, 'customer': customer.data})

    @csrf_exempt
    @action(detail=False, methods=['POST'])
    def process_payment(self, request):

        print('dattta', request.data)

        data = request.data['paymentData']
        nonce_from_the_client = data['paymentMethodNonce']
        amount = data['amount']

        # print('dattta',nonce_from_the_client)

        # return Response(request.data)

        result = gateway.transaction.sale({
            "amount": amount,
            "payment_method_nonce": nonce_from_the_client,
            "options": {
                "submit_for_settlement": True
            }
        })

        if (result.is_success):
            return Response({'success': result.is_success,
                             'transaction': {
                                 'id': result.transaction.id,
                                 'amount': result.transaction.amount
                             }
                             })
        else:
            return Response({'error': True, 'success': False})


# FIXME : TODO :working but testing face
class PaymentRApiViewSet(ViewSet):

    permission_classes = [IsAuthenticated]

    @csrf_exempt
    @action(detail=False, methods=['POST'])
    def start_payment(self, request):
        # pass client_token to your front-end
        user_id = request.user.id
        username = request.user.username
        queryset = Customer.objects.get(user_id=user_id)
        customer = CustomerSerializer(queryset)

        amount = request.data['amount']
        print(amount)

        DATA = {"amount": int(amount) * 100,
                "currency": "INR",
                "payment_capture": "1"}

        client = razorpay.Client(
            auth=('rzp_test_jj05mMUix1fD9r', 'aOo31hAP4J62uMGBisX8IKkg'))

        payment = client.order.create(DATA)


        return Response({'success': True, 'customer': customer.data, 'username': username, 'payment': payment})

    #TODO not yet done 
    @csrf_exempt
    @action(detail=False, methods=['POST'])
    def payment_status(self, request):

        response = request.data['response']
        ord_id = ""
        raz_pay_id = ""
        raz_signature = ""

        # # res.keys() will give us list of keys in res
        # for key in response.keys():
        #     if key == 'razorpay_order_id':
        #         ord_id = response[key]
        #     elif key == 'razorpay_payment_id':
        #         raz_pay_id = response[key]
        #     elif key == 'razorpay_signature':
        #         raz_signature = response[key]

        # data = {
        #     'razorpay_order_id': ord_id,
        #     'razorpay_payment_id': raz_pay_id,
        #     'razorpay_signature': raz_signature
        # }

        # client = razorpay.Client(
        #     auth=('rzp_test_jj05mMUix1fD9r', 'aOo31hAP4J62uMGBisX8IKkg'))

        # check = client.utility.verify_payment_signature(data)

        # if check is not None:
        #     print("Redirect to error url or error page")
        #     return Response({'error': 'Something went wrong'})
        print(response)
        return Response(response)
