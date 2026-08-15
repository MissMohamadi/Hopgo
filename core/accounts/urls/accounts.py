from django.urls import path, include
from .. import views



urlpatterns = [
     # template base authentication
     # path('', include('django.contrib.auth.urls')),

     # Base urls for authentication
     path('signup/', views.RegistrationView.as_view(), name='signup'),
     path('login/', views.LoginView.as_view(), name='login'),
     path('logout/', views.LogoutView.as_view(), name='logout'),

     # email verification
     path("verify-email/", views.EmailVerificationSendView.as_view(),
          name="email_verification_send"),
     path("verify-email/<uidb64>/<token>/",
          views.AccountActivationView.as_view(), name="account_activation"),

     # password management
     path('password_change/', views.PasswordChangeView.as_view(),name='password_change'),
     path('password_change/done/', views.PasswordChangeDoneView.as_view(),name='password_change_done'),
     # path('password_reset/', views.PasswordResetView.as_view(),
     #      name='password_reset'),
     # accounts/urls.py
     path('password_reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
     path('password_reset/set/', views.PasswordResetSetView.as_view(), name='password_reset_set'),
        # path('password_reset/done/', views.PasswordResetDoneView.as_view(),
     #      name='password_reset_done'),
     # path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(),
     #      name='password_reset_confirm'),
     # path('reset/done/', views.PasswordResetCompleteView.as_view(),
     #      name='password_reset_complete'),
     #     path('password_reset/', 
     #     views.DebugPasswordResetView.as_view(
     #         template_name='password_reset_form.html',
     #         email_template_name='registration/password_reset_email.html',
     #         success_url='/accounts/password_reset/done/'
     #     ), 
     #     name='password_reset'),

     #phone verification:
     path("send_otp/", views.send_otp, name="send_otp"),
     path("verify_otp/", views.verify_otp, name="verify_otp"),


     
]


