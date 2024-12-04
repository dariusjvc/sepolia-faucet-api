from django.http import JsonResponse
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.cache import cache
import os

from django.utils import timezone
from datetime import timedelta
from .models import Transaction 

from .tasks import send_funds 



@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'wallet_address',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description='Wallet address to which funds will be sent.'
        ),
    ],
    responses={
        200: openapi.Response(
            description='Funds sent successfully. Returns the transaction ID.',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message.'),
                    'transaction_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID of the transaction sent.')
                }
            )
        ),
        400: openapi.Response(
            description='Invalid method. Wallet address may be missing or incorrect.'
        ),
        429: openapi.Response(
            description='Rate limit exceeded. Users can only request funds once per minute.'
        )
    }
)
@api_view(['POST'])
def fund_view(request):
    wallet_address = request.query_params.get('wallet_address')  # Getting the address
    private_key = os.environ.get('PRIVATE_KEY')

    if not wallet_address:
        return JsonResponse({'error': 'No wallet address provided'}, status=400)

    user_ip = request.META.get('REMOTE_ADDR')
    cache_key_ip = f"faucet_request_{user_ip}"
    cache_key_wallet = f"faucet_request_{wallet_address}"

    # Timeout of 60 seconds for the rate limit
    rate_limit_timeout = 60  

    # Check if there is a cached entry for the IP or wallet address
    if cache.get(cache_key_ip) or cache.get(cache_key_wallet):
        return JsonResponse({'error': 'Rate limit exceeded. Please try again later.'}, status=429)

    # Set cache for both the IP and wallet address for the timeout period
    cache.set(cache_key_ip, True, timeout=rate_limit_timeout)
    cache.set(cache_key_wallet, True, timeout=rate_limit_timeout)

    # Call the Celery task
    result = send_funds.delay(wallet_address, private_key)
    
    try: 
        txn_hash = result.get(timeout=10)  # Get the result
        print(f"Transaction Hash: {txn_hash}") 
        return JsonResponse({'message': 'Funds sent!', 'transaction_id': txn_hash}, status=200)

    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error
        return JsonResponse({'error': 'Failed to send funds', 'details': str(e)}, status=500)


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(
            description='Returns the count of successful and failed transactions in the last 24 hours.',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'successful_transactions': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of successful transactions in the last 24 hours.'),
                    'failed_transactions': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of failed transactions in the last 24 hours.')
                }
            )
        ),
        400: openapi.Response(
            description='Invalid method. The request could not be processed.'
        )
    }
)
@api_view(['GET'])
def stats_view(request):
    twenty_four_hours_ago = timezone.now() - timedelta(days=1)
    
    successful_transactions = Transaction.objects.filter(
        status=Transaction.SUCCESS, 
        timestamp__gte=twenty_four_hours_ago
    ).count()
    
    failed_transactions = Transaction.objects.filter(
        status=Transaction.FAILED, 
        timestamp__gte=twenty_four_hours_ago
    ).count()

    return JsonResponse({
        'successful_transactions': successful_transactions,
        'failed_transactions': failed_transactions
    })
