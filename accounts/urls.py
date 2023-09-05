from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .import views,admin_views,client_views,users_views
from django.contrib.auth import views as auth_views
from .forms import MyPasswordResetform,MySetPasswordForm



urlpatterns = [
    path("success",views.success_page,name='success_page'),
    path("invalid",views.invalid,name='invalid_page'),

    
    # login and logout 
    path('loginpage', views.ShowLoginPage, name='loginpage'),
    path('dologin',views.doLogin,name='dologin'),
    path("dologout",views.doLogout,name='dologout'),

    #  end login and logout 
    # this for admin 
    path("success-admin",admin_views.success_page,name='success_page_admin'),
    path("admindashboard",admin_views.dashboard,name="admin_dashborad"),
    path("adminhome",admin_views.adminhome,name="adminhome"),
    path('customers-admin/', admin_views.customer_list_admin, name='customer_list_admin'),
    path('delete_customer_admin/<int:customer_id>/', admin_views.delete_customer_admin, name='delete_customer_admin'),
    path("addclient",admin_views.add_client,name="addclient"),
    path("addclientsave",admin_views.add_client_save,name="add_client_save"),
    path("deleteclient/<int:id>",admin_views.delete_client,name="delete_client"),
    path('block_client/<int:user_id>/', admin_views.block_client, name='block_client'),
    path('client/blocked_clients/', admin_views.blocked_clients, name='blocked_clients'),
    path('unblock/<int:user_id>/', admin_views.unblock_client, name='unblock_client'),
    path('add_place/', admin_views.add_place, name='add_place'),
    path('delete/<int:place_id>/', admin_views.delete_place, name='delete_place'),
    path("add_turf",admin_views.add_turf,name="add_turf_page"),
    path('add-turf_save/', admin_views.add_turf_save, name='add_turf_save'),
    path('add-ground-page/', admin_views.add_ground_page, name='add_ground_page_admin'),
    path('ground_details/<int:turf_id>/', admin_views.ground_details_page, name='ground_details_page'),
    path('delete_ground/<int:ground_id>/', admin_views.delete_ground, name='delete_ground_admin'),
    path('save_ground/', admin_views.add_ground_page_admin, name='save_ground_admin'),
    path('list-turf-details/', admin_views.list_turf_details, name='list_turf_details'),
    path('delete-turf/<int:turf_id>/', admin_views.delete_turf_admin, name='delete_turf_admin'),
    path('add_time_slot-page/', admin_views.add_time_slot, name='add_timeslot_page_admin'),
    path('admin/add_time_slot/', admin_views.add_time_slot_admin, name='add_time_slot_admin'),
    path('get-ground-names/<int:turf_id>/', admin_views.get_ground_names, name='get_ground_names'),
    path('turf-list/', admin_views.turf_list_timeslot, name='turf_list_timeslot'),
    path('turf/<int:turf_id>/grounds/', admin_views.ground_list, name='groundlist_timeslot_admin'),
    path('ground/<int:ground_id>/timeslots/', admin_views.timeslot_list, name='timeslot_list_admin'),
    path('admin/timeslot/<int:timeslot_id>/delete/', admin_views.delete_timeslot_admin, name='delete_timeslot_admin'),
    path('timeslots/<int:timeslot_id>/block/', admin_views.block_timeslot, name='block_timeslot_admin'),
    path('timeslots/<int:timeslot_id>/unblock/', admin_views.unblock_timeslot, name='unblock_timeslot_admin'),
    path('turf-list-reservation/', admin_views.turf_list_reservation, name='turf_list_reservation_admin'),
    path('turf-reservation/<int:turf_id>/grounds/', admin_views.ground_list_reservation, name='groundlist_reservation_admin'),
    path('admin/select_date_and_reservations/<int:ground_id>/', admin_views.select_date_and_reservations, name='select_date_and_reservations'),
    path('admin/bookings/',admin_views.booking_page,name='bookings_page_admin'),
     path('sort-by-turf/', admin_views.sort_by_turf, name='sort-by-turf'),
    path('sort-by-date/', admin_views.sort_by_date, name='sort-by-date'),
    path('payments-admin/', admin_views.payments_admin, name='payments-admin'),
    path('payments_admin_only/', admin_views.admins_only_payments, name='payments_admin_only'),
    path('update-payment-status/', admin_views.update_payment_status, name='update-payment-status'),
    path('enquiry-list/', admin_views.enquiry_list, name='enquiry_list'),
    path('enquiries/<int:pk>/delete/', admin_views.delete_enquiry, name='delete-enquiry'),
    
    

    # client section
    path("success-client",client_views.success_page_client,name='success_page_client'),
    path('clienthome', client_views.clienthome, name='clienthome'),
    path('change-password/', client_views.change_password_view, name='change_password'),
    path('customers-client/', client_views.customer_list_client, name='customer_list_client'),
    path('delete_customer_client/<int:customer_id>/', client_views.delete_customer_client, name='delete_customer_client'),
    path('addturfclient', client_views.add_turf_client, name='add_turf_client'),
    path('turfsaveclient', client_views.add_turf_save_client, name='save_turf_client'),
    path('client-turf-list', client_views.client_turf_list, name='client_turf_list'),
    path('delete-turf-confirmation/<int:turf_id>/', client_views.delete_turf_confirmation_page, name='delete_turf_confirmation_page'),
    path('delete-turf-client/<int:turf_id>/', client_views.delete_turf_confirmation, name='delete_turf_confirmation'),
    path('ground-page-client/', client_views.add_ground_client, name='add_ground_clent_page'),
    path('save_ground_client/', client_views.save_ground_client, name='save_ground_client'),
    path('client/ground-list-by-turf/<int:turf_id>/', client_views.ground_list_by_turf, name='ground_list_by_turf'),
    path('client/delete-ground/<int:ground_id>/', client_views.delete_ground, name='delete_ground_client'),
    path('turf_list_timeslot/', client_views.client_turf_list_timeslot, name='turf_list_timeslot_client'),
    path('client/addtimeslot-client/', client_views.add_time_slot_client, name='add_time_slot_client'),
    path('turf_list_fortimeslot/', client_views.turf_list_timeslot, name='turf_list_for_timeslot_client'),
    path('turf/<int:turf_id>/groundstimeslot/', client_views.ground_list, name='groundlist_timeslot_client'),
    path('ground/<int:ground_id>/timeslots-client/', client_views.timeslot_list, name='timeslot_list_client'),
    path('client/timeslot-client/<int:timeslot_id>/delete/', client_views.delete_timeslot_client, name='delete_timeslot_client'),
    path('turf-list-reservationclient/', client_views.turf_list_reservation, name='turf_list_reservation_client'),
    path('turf-reservation-client/<int:turf_id>/grounds/', client_views.ground_list_reservation, name='groundlist_reservation_client'),
    path('client/select_date_and_reservations_client/<int:ground_id>/', client_views.select_date_and_reservations, name='select_date_and_reservations_client'),
    path('client/bookings/', client_views.bookings_client, name='client_bookings'),
    path('client/paymentlist/', client_views.paymentlist_client, name='paymentlist_client'),
    path('payment-history/', client_views.payment_history, name='payment-history'),
    path('payment-history/pending/', client_views.pending_payments, name='sort-pending-bookings'),
    path('payment-history/completed/', client_views.completed_payments, name='sort-completed-bookings'),
    


    

    
    
    
    # users section
    path("",users_views.home,name='home'),
    path('about/', users_views.about,name="about"),
    path('registeruser/', views.show_register,name="showregisterpage"),
    path('saveuser/', users_views.add_user_save,name="saveuserdetails"),
   
    path('turf-list-user/', users_views.turf_list,name="turf_list_user"),
    path('turf-details/<int:turf_id>/', users_views.turf_details_user, name='turf_details_user'),
    path('available_time_slots/<int:ground_id>/', users_views.available_time_slots, name='available_time_slots'),
    path('timeslot-list-user/', users_views.timeslot_list_user, name='timeslot_list_user'),
    path('reserve-timeslots/', users_views.reserve_timeslots, name='reserve_timeslots'),
    path('reservation-success-user/', users_views.reservation_success_user, name='success_page_user'),
    path('save_payment/', users_views.save_payment, name='save_payment'),
    path('payment_done/', users_views.payment_done, name='payment_done'),
    path('booking_history/', users_views.booking_history, name='booking_history'),
    path('submit-enquiry/', users_views.enquiry_view, name='enquiry-view'),
    path('profile/', users_views.profile, name='profile'),
    path('profile/change_password/', users_views.change_password, name='change_password'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name = 'user/password_reset.html',form_class= MyPasswordResetform),name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name = 'user/password_reset_done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html', form_class=MySetPasswordForm), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name = 'user/password_reset_complete.html'),name='password_reset_complete'),


    
   
    


    
    


    
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
