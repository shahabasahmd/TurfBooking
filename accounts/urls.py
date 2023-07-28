from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .import views,admin_views,client_views,users_views



urlpatterns = [
    path("success",views.success_page,name='success_page'),
    
    # login and logout 
    path('loginpage', views.ShowLoginPage, name='loginpage'),
    path('dologin',views.doLogin,name='dologin'),
    path("dologout",views.doLogout,name='dologout'),
    #  end login and logout 
    # this for admin 
    path("adminhome",admin_views.adminhome,name="adminhome"),
    path('customers-admin/', admin_views.customer_list_admin, name='customer_list_admin'),
    path('delete_customer_admin/<int:customer_id>/', admin_views.delete_customer_admin, name='delete_customer_admin'),
    path("addclient",admin_views.add_client,name="addclient"),
    path("addclientsave",admin_views.add_client_save,name="add_client_save"),
    path("deleteclient/<int:id>",admin_views.delete_client,name="delete_client"),
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
    path('timeslot/<int:timeslot_id>/delete/', admin_views.delete_timeslot, name='delete_timeslot_admin'),
    # path('timeslot-details/<int:turf_id>/', admin_views.timeslot_details_admin, name='timeslot_details_admin'),
    # path('delete-timeslot/<int:timeslot_id>/', admin_views.delete_timeslot_admin, name='delete_timeslot_admin'),
    # path('reservation-list-admin/', admin_views.reservation_list, name='reservation_list_admin'),
    
    
    

    # client section
    path('clienthome', client_views.clienthome, name='clienthome'),
    path('change-password/', client_views.change_password_view, name='change_password'),
    path('customers-client/', client_views.customer_list_client, name='customer_list_client'),
    path('delete_customer_client/<int:customer_id>/', client_views.delete_customer_client, name='delete_customer_client'),
    path('addturfclient', client_views.add_turf_client, name='add_turf_client'),
    path('turfsaveclient', client_views.add_turf_save_client, name='save_turf_client'),
    path('client-turf-list', client_views.client_turf_list, name='client_turf_list'),
    path('ground-page-client/', client_views.add_ground_client, name='add_ground_clent_page'),
    path('save_ground_client/', client_views.save_ground_client, name='save_ground_client'),
    path('client/ground-list-by-turf/<int:turf_id>/', client_views.ground_list_by_turf, name='ground_list_by_turf'),
    path('client/delete-ground/<int:ground_id>/', client_views.delete_ground, name='delete_ground_client'),
    # path('delete-turf-client/<int:turf_id>/', client_views.delete_turf_confirmation_page, name='delete_turf_client'),
    # path('delete-confirmation/<int:turf_id>/', client_views.delete_turf_confirmation, name='delete_turf_confirmation'),
    # path('turf-list-timeslot/', client_views.client_turf_list_timeslot, name='turf_list_timeslot_client'),
    # path('timeslot-list-details/<int:turf_id>/', client_views.timeslot_list_client, name='timeslot_list_client'),
    # path('timeslot-page-forclient/', client_views.timeslot_page_client, name='timeslot_page_client'),
    # path('timeslot-list-client/<int:turf_id>/<int:timeslot_id>/delete/', client_views.delete_timeslot_client, name='delete_timeslot_client'),
    

    
    
    
    # users section
    path("",users_views.home,name='home'),
    path('about/', users_views.about,name="about"),
    path('registeruser/', views.show_register,name="showregisterpage"),
    path('saveuser/', users_views.add_user_save,name="saveuserdetails"),
    path('turf-list-user/', users_views.turf_list,name="turf_list_user"),
    path('turf-details/<int:turf_id>/', users_views.turf_details_user, name='turf_details_user'),
    path('available_time_slots/<int:ground_id>/', users_views.available_time_slots, name='available_time_slots'),
    #  path('show_time_slots/', users_views.show_time_slot_details, name='show_time_slots'),
    # path('timeslot-details-user/<int:turf_id>/', users_views.timeslot_details_user, name='timeslot_details_user'),
    path('timeslot-list-user/', users_views.timeslot_list_user, name='timeslot_list_user'),
    path('reserve-timeslots/', users_views.reserve_timeslots, name='reserve_timeslots'),

    # path('reserve_timeslots/', users_views.reserve_timeslots, name='reserve_timeslots'),
    path('reservation-success-user/', users_views.reservation_success_user, name='success_page_user'),
    
    
    
    

    
   
    


    
    


    
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
