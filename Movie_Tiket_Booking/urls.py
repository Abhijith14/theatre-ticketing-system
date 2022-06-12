from django.contrib import admin
from django.urls import path
from movie.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Home,name="home"),
    path('admin_home', Admin_Home,name="admin_home"),
    path('login_admin', login_admin, name="login_admin"),
    path('add_movie', Add_Movie,name="add_movie"),
    path('add_screen', Add_Screen,name="add_screen"),
    path('add_cat', Add_category,name="add_cat"),
    path('edit_cat', edit_category,name="edit_cat"),
    path('del_cat', delete_category,name="del_cat"),
    path('all_booking', All_Booking,name="all_booking"),
    path('delete_movie<int:pid>', delete_movie,name="delete_movie"),
    path('movie_detail<int:pid>', Movie_detail,name="movie_detail"),
    path('delete_booking<int:pid>', delete_booking,name="delete_booking"),
    path('book_movie<int:pid>', book_movie,name="book_movie"),
    path('edit_seat<int:pid>', edit_seat,name="edit_seat"),
    path('free_tk<int:pid>', free_tickets,name="free_tk"),
    path('remove_seats', remove_seats,name="remove_seats"),
    path('save_pending', update_pending,name="save_pending"),
    path('seats_update', ret_seats,name="seats_update"),
    path('tk<int:pid>', download_file, name="tk"),
    path('collection', collection_report, name="collection"),
    path('setshow', set_show, name="setshow"),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
