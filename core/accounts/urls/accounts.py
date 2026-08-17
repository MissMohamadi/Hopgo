from django.urls import path
from .. import views



urlpatterns = [
   
     # Base urls for authentication
     path('signup/', views.RegistrationView.as_view(), name='signup'),
     path('login/', views.LoginView.as_view(), name='login'),
     path('logout/', views.LogoutView.as_view(), name='logout'),


      # ثبت‌نام/ورود با OTP (ویوهای کلاس‌بیس جدید)
    path('send_otp/', views.SendOtpView.as_view(), name='send_otp'),
    path('verify_otp/', views.VerifyOtpView.as_view(), name='verify_otp'),  

    # بازیابی رمز عبور (سه مرحله‌ای)
    path('password_reset/', views.SendResetOtpView.as_view(), name='password_reset'),
    path('password_reset/verify/', views.VerifyResetOtpView.as_view(), name='verify_reset_otp'),
    path('password_reset/set/', views.PasswordResetSetView.as_view(), name='password_reset_set'),

    #انتخاب نقش توسط کاربر
    path("select-role/", views.RoleSelectView.as_view(), name="select_role"),
  

]


