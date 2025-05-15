from .models import SupportThread,SupportMessage
from .serializers import SupportThreadSerializer,SupportMessageSerializer,CreateSupportThreadAndMessageSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsStuffUser
from rest_framework.exceptions import PermissionDenied,ValidationError
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q,F
from django.db import transaction
from .permissions import CanAccessSupportThreadDetails

# Thread views
class SupportThreadCreateAPIView(generics.CreateAPIView):
    serializer_class=SupportThreadSerializer
    permission_classes=[IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method=='POST':
            return CreateSupportThreadAndMessageSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        create_serializer = self.get_serializer(data=request.data)
        try:
            create_serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response(e.detail,status=status.HTTP_400_BAD_REQUEST)
        
        validated_data=create_serializer.validated_data
        subject=validated_data['subject']
        message_text=validated_data['message']

        created_thread=None

        try:
            with transaction.atomic():
                thread=SupportThread.objects.create(
                    user=request.user,
                    subject=subject,
                    status=SupportThread.ThreadStatus.OPEN
                )

                SupportMessage.objects.create(
                    thread=thread,
                    sender=request.user,
                    message=message_text
                )

                created_thread=thread
        except Exception as e:
            return Response(
                {"detail": "An error occurred while creating the support request. Please try again."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        context=self.get_serializer_context()
        response_serializer=SupportThreadSerializer(created_thread,context=context)
        headers=self.get_success_headers(response_serializer.data) 
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OpenThreadsAPIView(generics.ListAPIView):
    serializer_class=SupportThreadSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return SupportThread.objects.filter(
            status=SupportThread.ThreadStatus.OPEN,
            staff__isnull=True
        ).select_related('user','staff','last_message'
        ).order_by(F('last_message__sent_at').desc(nulls_last=True))
    

    
class MyThreadsAPIView(generics.ListAPIView):
    serializer_class=SupportThreadSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return SupportThread.objects.filter(Q(user=self.request.user) | Q(staff=self.request.user)
        ).select_related('user','staff','last_message'
        ).order_by(F('last_message__sent_at').desc(nulls_last=True))
    

class ClosedThreadsAPIView(generics.ListAPIView):
    serializer_class=SupportThreadSerializer
    permission_classes=[IsStuffUser]

    def get_queryset(self):
        return SupportThread.objects.filter(status="closed",staff__isnull=True)


class SupportThreadRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=SupportThread.objects.all()
    serializer_class=SupportThreadSerializer
    permission_classes=[IsAuthenticated,CanAccessSupportThreadDetails]


class ChangeThreadStatusAPIView(APIView):
    permission_classes=[IsStuffUser]

    def patch(self,request,pk):
        new_status=request.data.get("status")

        valid_statuses = [choice.value for choice in SupportThread.ThreadStatus]
        if new_status not in valid_statuses:
            return Response({'detail':'Invalid status'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            thread=SupportThread.objects.get(pk=pk)
        except SupportThread.DoesNotExist:
            return Response({"detail": "Thread not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if new_status==SupportThread.ThreadStatus.IN_PROGRESS:
            if thread.staff is not None:
                return Response({"detail": "Thread already claimed."}, status=status.HTTP_400_BAD_REQUEST)
            thread.staff=request.user
        
        elif new_status in [SupportThread.ThreadStatus.OPEN, SupportThread.ThreadStatus.CLOSED]:
            thread.staff=None

        thread.status=new_status 
        thread.save()
        
        serializer=SupportThreadSerializer(thread)
        return Response(serializer.data,status=status.HTTP_200_OK)


class SupportThreadSearchAPIView(generics.ListAPIView):
    serializer_class=SupportThreadSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        user=self.request.user
        search=self.request.query_params.get('search')

        if not search:
            return SupportThread.objects.none()
        
        base_queryset=SupportThread.objects.none()

        if user.is_staff:
            staff_search_scope=(
                Q(status=SupportThread.ThreadStatus.OPEN,staff__isnull=True) |
                Q(status=SupportThread.ThreadStatus.CLOSED) |
                Q(status=SupportThread.ThreadStatus.IN_PROGRESS,staff=user)
            )

            base_queryset=SupportThread.objects.filter(staff_search_scope)
        else:
            base_queryset=SupportThread.objects.filter(user=user)

        search_filters=Q()

        search_filters|=Q(subject__icontains=search)
        search_filters|=Q(user__username__icontains=search)

        final_queryset=base_queryset.filter(search_filters).select_related(
            'user','staff','last_message'
        ).distinct().order_by(F('last_message__sent_at'))

        return final_queryset

        

#Message views
class SupportMessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class=SupportMessageSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        thread_id=self.kwargs["thread_id"]
        thread=SupportThread.objects.get(id=thread_id)

        if thread.status==SupportThread.ThreadStatus.OPEN and self.request.user.is_staff:
            return SupportMessage.objects.filter(thread=thread)

        if self.request.user!=thread.user and self.request.user!=thread.staff:
            raise PermissionDenied("You do not have access to this thread.")
        
        return SupportMessage.objects.filter(thread=thread)

    def perform_create(self,serializer):
        thread=SupportThread.objects.get(id=self.kwargs['thread_id'])

        if self.request.user!=thread.user and self.request.user!=thread.staff:
            raise PermissionDenied("You do not have access to this thread.")
        
        if thread.status!=SupportThread.ThreadStatus.IN_PROGRESS:
             raise PermissionDenied("Cannot send messages unless thread is in progress.")
        
        serializer.save(sender=self.request.user,thread=thread)


    