from django.urls import path
from .views import UserMeView, GoogleFitAuthView, StepSyncView, UserCreateView

app_name = 'users'

urlpatterns = [
    path('me/', UserMeView.as_view(), name='user_me'),
    path('signup/', UserCreateView.as_view(), name='signup'),

    # GoogleFit連携
    path('fit-auth/', GoogleFitAuthView.as_view(), name='fit_auth'),
    path('sync-steps/', StepSyncView.as_view(), name='sync_steps'),
]