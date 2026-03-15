import logging
from .models import *
from .serializers import *
from utils.views import APIResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


logger = logging.getLogger(__name__)

# ----review API view-----------------------------------------
class ReviewAPIView(APIView, APIResponse):
    """GET /api/reviews/
    Retrieves a list of reviews with pagination support.
    """
    pagination_class = PageNumberPagination

    def get(self, request):
        try:
            queryset = Review.objects.all().order_by('-created_at')
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request, view=self)
    
            if page is not None:
                serializer = ReviewSerializer(page, many=True, context={"request": request})
                meta = {
                    "count": paginator.page.paginator.count,
                    "next": paginator.get_next_link(),
                    "previous": paginator.get_previous_link(),
                }
    
                return self.success_response(
                    message="Reviews retrieved successfully",
                    data=serializer.data,
                    meta=meta,
                )
            else:
                # Return empty list if no pagination page
                serializer = ReviewSerializer(queryset, many=True, context={"request": request})
                return self.success_response(
                    message="Reviews retrieved successfully",
                    data=serializer.data,
                    meta={"count": queryset.count(), "next": None, "previous": None},
                )
    
        except ValidationError as e:
            logger.error(f"Validation error while retrieving reviews: {str(e)}")
            return self.error_response(
                message="Invalid data provided",
                errors=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Error while retrieving reviews: {str(e)}")
            return self.error_response(
                message="Internal server error",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

# ---- Our Results API view-----------------------------------------
class OurResultsAPIView(APIView, APIResponse):
    """GET /api/our-results/
    Retrieves a list of our results with pagination support.
    """
    pagination_class = PageNumberPagination

    def get(self, request):
        try:
            queryset = OurResults.objects.prefetch_related('images').all().order_by('-created_at')
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request, view=self)

            if page is not None:
                serializer = OurResultSerializer(page, many=True, context={"request": request})
                meta = {
                    "count": paginator.page.paginator.count,
                    "next": paginator.get_next_link(),
                    "previous": paginator.get_previous_link(),
                }

                return self.success_response(
                    message="Our Results retrieved successfully",
                    data=serializer.data,
                    meta=meta,
                )
            else:
                # Return empty list if no pagination page
                serializer = OurResultSerializer(queryset, many=True, context={"request": request})
                return self.success_response(
                    message="Our Results retrieved successfully",
                    data=serializer.data,
                    meta={"count": queryset.count(), "next": None, "previous": None},
                )
        except ValidationError as e:
            logger.error(f"Validation error while retrieving our results: {str(e)}")
            return self.error_response(
                message="Invalid data provided",
                errors=e.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Error while retrieving our results: {str(e)}")
            return self.error_response(
                message="Internal server error",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

# --- Request Quote API view-----------------------------------------
class RequestQuoteAPIView(APIView):
    """
    POST /api/request-quote/
    Creates a new quote request and notifies the admin via email.
    """
    def post(self, request, *args, **kwargs):
        serializer = RequestQuoteSerializer(data=request.data)

        if not serializer.is_valid():
            return APIResponse.error_response(
                errors=serializer.errors,
                message="Validation failed. Please check your input.",
            )

        serializer.save()
        self._send_admin_notification(serializer.validated_data)

        return APIResponse.success_response(
            data=serializer.data,
            message="Quote request submitted successfully.",
            status_code=201,
        )

    def _send_admin_notification(self, data):
        name          = data.get('name', '')
        profession    = data.get('profession', '')
        email         = data.get('email', '')
        business_name = data.get('business_name', '')
        location      = data.get('location', '')
        phone         = data.get('phone', '')
        description   = data.get('description', '')

        context = {
            'name':          name,
            'profession':    profession,
            'email':         email,
            'business_name': business_name,
            'location':      location,
            'phone':         phone,
            'description':   description,
        }

        subject = f"New Quote Request — {name}"

        text_message = (
            f"New Quote Request\n\n"
            f"Name:          {name}\n"
            f"Profession:    {profession}\n"
            f"Email:         {email}\n"
            f"Phone:         {phone}\n"
            f"Business Name: {business_name}\n"
            f"Location:      {location}\n\n"
            f"Description:\n{description}\n"
        )

        html_message = render_to_string('emails/quote_request.html', context)

        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.ADMIN_EMAIL],
            reply_to=[email],
        )
        email_msg.attach_alternative(html_message, "text/html")
        email_msg.send(fail_silently=False)