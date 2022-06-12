import json
import os
from datetime import timedelta
import datetime
import random
import numpy as np
import copy
import pytz

import collections
from wsgiref.util import FileWrapper

from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import *

# image processing
from PIL import Image, ImageDraw, ImageFont
import cv2
import pytesseract
from pytesseract import Output
import img2pdf

ocr_dir = r"static\printer\Tesseract-OCR\tesseract.exe"

admin_userid, admin_userpass = "admin", "SMBadmin"

# layouts
from .seat_layouts.screen1 import seats as seats_1
from .seat_layouts.screen1 import row as row_1
from .seat_layouts.screen2 import seats as seats_2
from .seat_layouts.screen2 import row as row_2
from .seat_layouts.screen3 import seats as seats_3
from .seat_layouts.screen3 import row as row_3
from .seat_layouts.screen4 import seats as seats_4
from .seat_layouts.screen4 import row as row_4
from .seat_layouts.screen5 import seats as seats_5
from .seat_layouts.screen5 import row as row_5


# Create your views here.
def Home(request):
    # printing_all_tk()

    data = Movie.objects.all()
    d = {'data': data}
    return render(request, 'index.html', d)


def login_admin(request):

    global admin_userid, admin_userpass
    context = {}
    error = False
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        if username == admin_userid and password == admin_userpass:
            return redirect(Admin_Home)

        else:
            error = True

    context['error'] = error

    return render(request, 'admin.html', context)


def Admin_Home(request):
    total_user = 0
    total_movie = 0
    total_booking = 0
    for i in Movie.objects.all():
        total_movie += 1
    for i in Booking.objects.all():
        total_booking += 1
    d = {'total_user': total_user, 'total_movie': total_movie, 'total_booking': total_booking}
    return render(request, 'admin_dash.html', d)


def Add_Screen(request):
    main_obj = Movie_Time.objects.all()
    context = {}
    context["data"] = main_obj

    if request.GET:
        new_screen = request.GET['new_data']
        # Todo check if max screen count = 5

        pid = request.GET['id']

        obj = Movie_Time.objects.filter(id=pid)

        obj.update(screen=new_screen)

    return render(request, 'add_screen.html', context)


def edit_category(request):
    context = {}
    success, error = False, False

    obj = cats_seat.objects.all()
    context['data'] = obj

    if request.POST:
        category_selected = request.POST['cat_selected']
        category_name = request.POST['ncat']
        category_amt = request.POST['namt']

        obj_main = cats_seat.objects.filter(cats_name=category_selected)
        obj_check = cats_seat.objects.filter(cats_name=category_name)

        if len(obj_main) != 0 and len(obj_check) == 0:
            obj_main.update(cats_name=category_name, amount=category_amt)
            success = True
        else:
            error = True

    context['success'] = success
    context['error'] = error

    return render(request, "add_cat.html", context)


def rgb2hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def Add_category(request):
    context = {}
    success, error = False, False

    obj = cats_seat.objects.all()
    context['data'] = obj

    if request.POST:
        category_name = request.POST['cat_name']
        category_amt = request.POST['amt_n']

        obj_check = cats_seat.objects.filter(cats_name=category_name)
        if len(obj_check) == 0:

            random_color = list(np.random.choice(range(255), size=3))
            # random_color = random_color + [1]

            obj = cats_seat.objects.create(cats_name=category_name, amount=category_amt,
                                           color=rgb2hex(random_color[0], random_color[1], random_color[2]))
            obj.save()
            success = True
        else:
            error = True

    context['success'] = success
    context['error'] = error

    return render(request, "add_cat.html", context)


def delete_category(request):
    try:
        obj = cats_seat.objects.get(id=request.GET['id'])
        obj.delete()

        return HttpResponse(True)
    except:
        return HttpResponse(False)


def return_shows_list(screen_name):
    ret_list = []
    main_data = Movie_Time.objects.filter(screen=screen_name)
    for j in main_data:
        ret_list.append(j.time1)

    return ret_list


def start_variables():
    main_data = Movie_Time.objects.all()

    screens_list = []
    for i in main_data:
        splitting = str(i).split(" $ ")
        screens_list.append(splitting[0])

    screens_list = list(set(screens_list))
    screens_list.sort()

    main_dict = {}
    for i in screens_list:
        main_dict[i] = return_shows_list(i)

    return main_dict, screens_list


def Add_Movie(request):
    error = False

    context = {}

    main_d, screens_l = start_variables()

    context["screens_list"] = screens_l

    context["selected_screen"] = main_d[screens_l[0]]

    if request.GET:
        selected_screen = request.GET['new_data']
        return JsonResponse(main_d[selected_screen], safe=False)

    if request.POST:
        movie_name = request.POST['name']
        screen_selected = request.POST['screen']
        shows_selected = request.POST.getlist('show_select')
        from_date_selected = request.POST['fromdate']
        to_date_selected = request.POST['todate']

        obj = Movie.objects.create(
            name=movie_name,
            screen=screen_selected,
            shows=shows_selected,
            from_date=from_date_selected,
            to_date=to_date_selected
        )

        obj.save()

        from_date_selected = datetime.datetime.strptime(from_date_selected, "%Y-%m-%d")
        to_date_selected = datetime.datetime.strptime(to_date_selected, "%Y-%m-%d")

        delta = to_date_selected - from_date_selected  # as timedelta
        print(type(from_date_selected))

        for i in range(delta.days + 1):
            day = from_date_selected + timedelta(days=i)
            print(day)
            day = datetime.datetime.strptime(str(day), "%Y-%m-%d %H:%M:%S").strftime("%a, %d %B %Y")

            for j in shows_selected:
                show_obj = Movie_Time.objects.filter(screen=screen_selected, time1=j)[0].id
                show_obj = Movie_Time.objects.get(id=show_obj)
                meh = Set_Timing.objects.create(
                    movie=obj,
                    date1=day,
                    screen=show_obj
                )
                meh.save()

        error = True

    context['error'] = error

    return render(request, 'add_movie.html', context)


def delete_movie(request, pid):
    data = Movie.objects.get(id=pid)
    data.delete()
    return redirect('home')


def Movie_detail(request, pid):
    data = Movie.objects.get(id=pid)
    time1 = Movie_Time.objects.all()
    if request.method == "POST":
        t = request.POST['time']
        d = request.POST['date']
        if request.user:
            data1 = Set_Timing.objects.create(
                time1=t,
                date1=d,
                movie=data
            )
        else:
            return redirect('home')
        return redirect('book_ticket', data1.id)
    d = {'data': data, 'time1': time1}
    return render(request, 'movie_detail.html', d)


def All_Booking(request):
    data = Booking.objects.all()
    d = {'data': data}
    return render(request, 'all_booking.html', d)


def delete_booking(request, pid):
    data = Booking.objects.get(id=pid)
    data.delete()
    return redirect('all_booking')


def check_seat_exists(obj, selected, screen):
    seats = eval(obj.seats_list)
    screen = int(screen)

    seats_1 = seats[screen - 1]
    selected = selected[screen - 1]

    # print(seats)
    # print(selected)

    del_ele = []
    for i in seats_1:
        for j in selected:
            if i == j:
                del_ele.append(j)
    if del_ele:
        new_seats = list(set(seats_1) - set(del_ele))
        new_seats.sort()
        # print(del_ele, obj.cats_name, new_seats)
        seats[screen - 1] = new_seats
        s_count = []
        for i in seats:
            if i:
                s_count.append(len(i))
            else:
                s_count.append(0)
        obj_remove = cats_seat.objects.filter(id=obj.id)
        obj_remove.update(
            seats_list=seats,
            seats_count=s_count
        )


def add_seats_matrix(seats, obj, screen):
    print(seats)
    old_seats = eval(obj[0].seats_list)
    print(old_seats)

    old_seats[screen - 1] = seats[screen - 1] + old_seats[screen - 1]

    return old_seats


def edit_seat(request, pid):
    error = False
    all_screens = []
    all_screens_obj = Movie_Time.objects.all()

    for i in range(len(all_screens_obj)):
        all_screens.append(all_screens_obj[i].screen)

    all_screens = list(set(all_screens))
    all_screens.sort()

    cat_obj = cats_seat.objects.all()

    if request.GET:
        cat_name = request.GET['category']
        seat_sel = request.GET['seats']
        screen = request.GET['screen']

        main_seats, main_count = [], []

        obj = cats_seat.objects.filter(id=cat_name)

        curr_list = obj[0].seats_list

        main_seats = eval(curr_list)

        main_seats[int(screen) - 1] = seat_sel.split(",")

        # emptying the list
        for i in range(len(main_seats)):
            if main_seats[i] == ['']:
                main_seats[i] = []

        final_seats = add_seats_matrix(main_seats, obj, int(screen))

        # seats counting
        for i in final_seats:
            if i:
                main_count.append(len(i))
            else:
                main_count.append(0)

        # checking duplicate seats in diff categories
        obj_check = cats_seat.objects.all()
        for i in obj_check:
            check_seat_exists(i, final_seats, screen)

        # save
        obj.update(
            seats_list=final_seats,
            seats_count=main_count
        )

        return HttpResponse("Success!")

    seats_curr = ""
    rows_curr = ""

    if pid == 1:
        seats_curr = seats_1
        rows_curr = row_1

    elif pid == 2:
        seats_curr = seats_2
        rows_curr = row_2
    elif pid == 3:
        seats_curr = seats_3
        rows_curr = row_3
    elif pid == 4:
        seats_curr = seats_4
        rows_curr = row_4
    elif pid == 5:
        seats_curr = seats_5
        rows_curr = row_5

    d = {
        'pid': pid,
        'error': error,
        'screens': all_screens,
        'category': cat_obj,
        'seats': seats_curr,
        'row': rows_curr
    }

    return render(request, 'edit_seat.html', d)


def remove_seats(request):
    if request.GET:
        cat_name = request.GET['category']
        seat_sel = request.GET['seats']
        screen = int(request.GET['screen'])

        obj = cats_seat.objects.filter(id=cat_name)
        seats = eval(obj[0].seats_list)
        seats_rem = [seat_sel]
        seats[screen - 1] = list(set(seats[screen - 1]) - set(seats_rem))

        s_count = []
        # seats counting
        for i in seats:
            if i:
                s_count.append(len(i))
            else:
                s_count.append(0)

        # save
        obj.update(
            seats_list=seats,
            seats_count=s_count
        )

    return HttpResponse("Success")


def get_movie_book_status(s_time, s_date):
    s_time = s_time.split(" - ")[1]

    movie_time = s_date + " " + s_time

    movie_time = datetime.datetime.strptime(movie_time, "%a, %d %B %Y %I:%M %p")

    tz_AS = pytz.timezone("Asia/Calcutta")
    datetime_AS = datetime.datetime.now(tz_AS)
    current_time = datetime_AS.strftime("%a, %d %B %Y %I:%M %p")

    current_time = datetime.datetime.strptime(str(current_time), "%a, %d %B %Y %I:%M %p")

    time_limit = movie_time - timedelta(hours=1)

    if current_time > time_limit:
        status = "CONFIRMED"
    else:
        status = "RESERVED"

    return status


def book_movie(request, pid):

    context = {}

    error = False
    movies = {}
    all_screens = []
    all_screens_obj = Movie_Time.objects.all()
    # print(all_screens[0].screen)
    for i in range(len(all_screens_obj)):
        all_screens.append(all_screens_obj[i].screen)

    all_screens = list(set(all_screens))
    all_screens.sort()

    scr_obj = Movie_Time.objects.filter(screen_id=pid)[0].screen

    movies["name"] = Movie.objects.filter(screen=str(scr_obj))

    if request.GET:
        movie_name_ajax = request.GET['movie']
        screen_ajax = request.GET['screen']

        print("Screen : ", screen_ajax)

        scr_obj_get = Movie_Time.objects.filter(screen_id=screen_ajax)[0].screen
        shows_list_ajax = Movie.objects.filter(screen=str(scr_obj_get), name=movie_name_ajax)[0].shows

        print(shows_list_ajax)

        date_list_ajax = []
        date_1 = Movie.objects.filter(screen=str(scr_obj_get), name=movie_name_ajax)[0].from_date
        date_2 = Movie.objects.filter(screen=str(scr_obj_get), name=movie_name_ajax)[0].to_date

        delta = date_2 - date_1  # as timedelta
        for i in range(delta.days + 1):
            day = date_1 + timedelta(days=i)
            day = datetime.datetime.strptime(str(day), "%Y-%m-%d").strftime("%a, %d %B %Y")
            date_list_ajax.append(day)

        shows_list_ajax = str(shows_list_ajax).replace("'", '"')

        ajax_data = {
            "shows_list": shows_list_ajax,
            "date_list": date_list_ajax
        }

        return JsonResponse(ajax_data)

    if request.POST:
        seat_num = request.POST['num']
        seat_list = request.POST['seat']
        pending_num = request.POST['num_pending']
        pending_list = request.POST['seat_pending']
        movie_name = request.POST['movie_name_sub']
        show_time = request.POST['show_time_sub']
        show_date = request.POST['show_date_sub']

        time_obj = Movie_Time.objects.filter(screen_id=pid, time1=show_time)[0].id

        mov_obj = Movie.objects.filter(name=movie_name, screen=str(scr_obj))[0].id

        curr_id = Set_Timing.objects.filter(date1=show_date, screen=time_obj, movie=mov_obj)[0].id

        obj_main = Set_Timing.objects.get(id=curr_id)

        seat_list_cat = seat_list.split(",")

        obj_cats = cats_seat.objects.all()
        payment_list = []
        for i in obj_cats:
            seats_cat = eval(i.seats_list)
            seats_cat_1 = seats_cat[pid - 1]
            for j in seats_cat_1:
                # print(j, "-")
                for k in seat_list_cat:
                    # print(j, "-", k)
                    if j == k:
                        # print(i.amount)
                        payment_list.append(i.amount)

        # print(seat_list_cat)
        # print(payment_list)
        tk_cost = float(sum(payment_list))

        status = get_movie_book_status(show_time, show_date)

        obj = Booking.objects.create(
            set_time=obj_main,
            status=status,
            time=show_time + " " + show_date,
            seat=seat_list,
            price=tk_cost,
            ticket=seat_num
        )
        obj.save()

        tk_name = print_movie_tk(obj)

        context['ticket'] = tk_name

        error = True

    seats_curr = ""
    rows_curr = ""

    if pid == 1:
        seats_curr = seats_1
        rows_curr = row_1

    elif pid == 2:
        seats_curr = seats_2
        rows_curr = row_2
    elif pid == 3:
        seats_curr = seats_3
        rows_curr = row_3
    elif pid == 4:
        seats_curr = seats_4
        rows_curr = row_4
    elif pid == 5:
        seats_curr = seats_5
        rows_curr = row_5

    context['pid'] = pid
    context['error'] = error
    context['movies'] = movies
    context['screens'] = all_screens
    context['seats'] = seats_curr
    context['row'] = rows_curr

    if "ticket" in context.keys():
        return render(request, 'printer.html', context)
    else:
        return render(request, 'booking.html', context)


def free_tickets(request, pid):
    context = {}
    error = False
    movies = {}
    all_screens = []
    all_screens_obj = Movie_Time.objects.all()
    for i in range(len(all_screens_obj)):
        all_screens.append(all_screens_obj[i].screen)

    all_screens = list(set(all_screens))
    all_screens.sort()

    scr_obj = Movie_Time.objects.filter(screen_id=pid)[0].screen

    movies["name"] = Movie.objects.filter(screen=str(scr_obj))

    if request.POST:
        seat_num = request.POST['num']
        seat_list = request.POST['seat']
        pending_num = request.POST['num_pending']
        pending_list = request.POST['seat_pending']
        movie_name = request.POST['movie_name_sub']
        show_time = request.POST['show_time_sub']
        show_date = request.POST['show_date_sub']

        time_obj = Movie_Time.objects.filter(screen_id=pid, time1=show_time)[0].id

        mov_obj = Movie.objects.filter(name=movie_name, screen=str(scr_obj))[0].id

        curr_id = Set_Timing.objects.filter(date1=show_date, screen=time_obj, movie=mov_obj)[0].id

        obj_main = Set_Timing.objects.get(id=curr_id)

        seat_list_cat = seat_list.split(",")

        obj_cats = cats_seat.objects.all()

        tk_cost = 0.00

        status = get_movie_book_status(show_time, show_date)

        obj = Booking.objects.create(
            set_time=obj_main,
            status=status,
            time=show_time + " " + show_date,
            seat=seat_list,
            price=tk_cost,
            ticket=seat_num
        )
        obj.save()

        tk_name = print_movie_tk(obj)

        context['ticket'] = tk_name

        error = True

    seats_curr = ""
    rows_curr = ""

    if pid == 1:
        seats_curr = seats_1
        rows_curr = row_1
    elif pid == 2:
        seats_curr = seats_2
        rows_curr = row_2
    elif pid == 3:
        seats_curr = seats_3
        rows_curr = row_3
    elif pid == 4:
        seats_curr = seats_4
        rows_curr = row_4
    elif pid == 5:
        seats_curr = seats_5
        rows_curr = row_5

    context['pid'] = pid
    context['error'] = error
    context['movies'] = movies
    context['screens'] = all_screens
    context['seats'] = seats_curr
    context['row'] = rows_curr

    if "ticket" in context.keys():
        return render(request, 'printer.html', context)
    else:
        return render(request, 'booking.html', context)


def update_pending(request):
    if request.GET:
        movie_name_ajax = request.GET['movie']
        screen_ajax = request.GET['screen']
        time_ajax = request.GET['time']
        date_ajax = request.GET['date']
        seats_ajax = request.GET['seats_a']
        seats_count = request.GET['seats_count']

        scr_obj_get = Movie_Time.objects.filter(screen_id=screen_ajax)[0].screen

        time_obj = Movie_Time.objects.filter(screen_id=screen_ajax, time1=time_ajax)[0].id
        mov_obj = Movie.objects.filter(name=movie_name_ajax, screen=str(scr_obj_get))[0].id
        curr_id = Set_Timing.objects.filter(date1=date_ajax, screen=time_obj, movie=mov_obj)[0].id

        obj_main = Set_Timing.objects.get(id=curr_id)

        obj_pend2 = Pending.objects.filter(set_time=obj_main)

        print(seats_count)

        if int(seats_count) == 0:
            if len(obj_pend2) > 0:
                obj_pend2.delete()
        else:
            if len(obj_pend2) == 0:
                obj_pend = Pending.objects.create(
                    set_time=obj_main,
                    status="Pending",
                    time=time_ajax + " " + date_ajax,
                    seat=seats_ajax,
                    price=0.00,
                    ticket=seats_count
                )
                obj_pend.save()
            else:
                obj_pend2.update(
                    seat=seats_ajax,
                    price=0.00,
                    ticket=seats_count
                )
    return HttpResponse("Success !!")


def ret_seats(request):
    seats_pending = ""
    seats_confirmed = ""
    if request.GET:
        date_ajax = request.GET['shows_date']
        time_ajax = request.GET['shows_time']
        movie_name = request.GET['movie_name']
        screen = request.GET['screen']

        if time_ajax != "--------------":

            scr_obj_get = Movie_Time.objects.filter(screen_id=screen)[0].screen

            time_obj = Movie_Time.objects.filter(screen_id=screen, time1=time_ajax)[0].id

            mov_obj = Movie.objects.filter(name=movie_name, screen=str(scr_obj_get))[0].id

            curr_id = Set_Timing.objects.filter(date1=date_ajax, screen=time_obj, movie=mov_obj)[0].id

            obj_main = Set_Timing.objects.get(id=curr_id)

            obj_pend2 = Pending.objects.filter(set_time=obj_main)
            obj_conf2 = Booking.objects.filter(set_time=obj_main)

            if len(obj_pend2) > 0:
                for i in obj_pend2:
                    if seats_pending:
                        seats_pending += "," + i.seat
                    else:
                        seats_pending = i.seat
                print(seats_pending)

            if len(obj_conf2) > 0:
                for i in obj_conf2:
                    if seats_confirmed:
                        seats_confirmed += "," + i.seat
                    else:
                        seats_confirmed = i.seat
                print(seats_confirmed)

    context = {
        "seats_c": seats_confirmed,
        "seats_p": seats_pending
    }

    return JsonResponse(context)


def print_date_week(img, day, week):
    # day
    font = ImageFont.truetype('movie/static/printer/fonts/Open_Sans/static/OpenSans/OpenSans-ExtraBold.ttf', 40)
    draw = ImageDraw.Draw(img)
    x, y = 230, 180
    draw.text(xy=(x, y), text=day, fill=(0, 74, 173), font=font)

    # week
    font = ImageFont.truetype('movie/static/printer/fonts/Anonymous_Pro/AnonymousPro-Bold.ttf', 30)
    draw = ImageDraw.Draw(img)
    if len(week) > 7:
        x, y = 250, 230
    else:
        x, y = 270, 230
    draw.text(xy=(x, y), text=week, fill=(0, 74, 173), font=font)


def print_shows(img, show):
    show = show.split(" - ")

    # time
    font = ImageFont.truetype('movie/static/printer/fonts/Open_Sans/static/OpenSans/OpenSans-ExtraBold.ttf', 40)
    draw = ImageDraw.Draw(img)
    x, y = 230, 360
    draw.text(xy=(x, y), text=show[1], fill=(0, 74, 173), font=font)

    # show name
    font = ImageFont.truetype('movie/static/printer/fonts/Anonymous_Pro/AnonymousPro-Bold.ttf', 30)
    draw = ImageDraw.Draw(img)
    x, y = 270, 410
    draw.text(xy=(x, y), text=show[0], fill=(0, 74, 173), font=font)


def print_seat_details(img, seat, category, ticket, reservation=0):
    # seat number
    print_i = seat[0] + "-" + seat[1:]
    font = ImageFont.truetype('movie/static/printer/fonts/Open_Sans/static/OpenSans/OpenSans-ExtraBold.ttf', 40)
    draw = ImageDraw.Draw(img)
    x, y = 280, 550
    draw.text(xy=(x, y), text=print_i, fill=(0, 74, 173), font=font)

    # seat count
    font = ImageFont.truetype('movie/static/printer/fonts/Open_Sans/static/OpenSans/OpenSans-ExtraBold.ttf', 40)
    draw = ImageDraw.Draw(img)
    x, y = 300, 730
    draw.text(xy=(x, y), text="1", fill=(0, 74, 173), font=font)

    # category
    font = ImageFont.truetype('movie/static/printer/fonts/Open_Sans/static/OpenSans/OpenSans-ExtraBold.ttf', 60)
    draw = ImageDraw.Draw(img)
    x, y = 700, 180
    draw.text(xy=(x, y), text=category, fill=(0, 74, 173), font=font)

    # ticket price
    total = float(ticket)
    ticket = str(ticket) + " x 1 = " + str(ticket)
    font = ImageFont.truetype('movie/static/printer/fonts/Anonymous_Pro/AnonymousPro-Bold.ttf', 30)
    draw = ImageDraw.Draw(img)
    x, y = 1020, 642
    draw.text(xy=(x, y), text=str(ticket), fill=(0, 74, 173), font=font)

    # reservation
    if reservation != 0:
        total = total + float(reservation)
        reservation_c = str(reservation) + " x 1    = " + str(reservation)
        draw = ImageDraw.Draw(img)
        x, y = 1020, 690
        draw.text(xy=(x, y), text=str(reservation_c), fill=(0, 74, 173), font=font)

    # total
    font = ImageFont.truetype('movie/static/printer/fonts/Open_Sans/static/OpenSans/OpenSans-SemiBold.ttf', 45)
    draw = ImageDraw.Draw(img)
    x, y = 1215, 760
    draw.text(xy=(x, y), text=str(total), fill=(0, 74, 173), font=font)


def print_movie_name(img, name):
    # movie name
    if len(name) > 40:
        font = ImageFont.truetype('movie/static/printer/fonts/Open_Sans/static/OpenSans/OpenSans-ExtraBold.ttf', 23)
    else:
        font = ImageFont.truetype('movie/static/printer/fonts/Open_Sans/static/OpenSans/OpenSans-ExtraBold.ttf', 30)
    draw = ImageDraw.Draw(img)
    x, y = 630, 490
    draw.text(xy=(x, y), text=name, fill=(0, 74, 173), font=font)


def print_screen(img, screen):
    # screen name
    screen = "SMB Cinemas " + screen
    font = ImageFont.truetype('movie/static/printer/fonts/Open_Sans/static/OpenSans/OpenSans-ExtraBold.ttf', 60)
    draw = ImageDraw.Draw(img)
    x, y = 600, 100
    draw.text(xy=(x, y), text=screen, fill=(0, 74, 173), font=font)


def print_movie_tk(bookid):
    layout = "movie/static/printer/ticket/layout.png"
    img = Image.open(layout)

    # getting the date and week
    date_alone = bookid.set_time.date1
    day = datetime.datetime.strptime(str(date_alone), "%a, %d %B %Y").strftime("%d/%m/%y")
    week = datetime.datetime.strptime(str(date_alone), "%a, %d %B %Y").strftime("%A")
    print_date_week(img, day, week)

    # getting the show and time
    shows = bookid.set_time.screen.time1
    print_shows(img, shows)

    # getting movie name
    print_movie_name(img, str(bookid.set_time.movie))

    # printing screen
    screen = str(bookid.set_time.screen.screen)
    print_screen(img, str(bookid.set_time.screen.screen))

    # seats number, seat count, category, ticket amount and reservation
    seats_temp = str(bookid.seat).split(",")
    screen_curr = int(bookid.set_time.screen.screen_id) - 1

    cat_obj = cats_seat.objects.all()

    c = 0
    files_list = []
    for seat in seats_temp:
        img2 = copy.deepcopy(img)
        curr_cat, curr_amt = "", 0.00
        for i in cat_obj:
            seat_list = eval(i.seats_list)
            if seat in seat_list[screen_curr]:
                curr_cat = i.cats_name
                curr_amt = i.amount

        if bookid.status == "RESERVED":
            print_seat_details(img2, seat, curr_cat, curr_amt, 10)
        else:
            print_seat_details(img2, seat, curr_cat, curr_amt)

        # printing the id
        font = ImageFont.truetype('movie/static/printer/fonts/Anonymous_Pro/AnonymousPro-Bold.ttf', 25)
        draw = ImageDraw.Draw(img2)
        x, y = 955, 836
        draw.text(xy=(x, y), text=str(bookid.id), fill=(0, 74, 173), font=font)

        c = c + 1
        img_filename = "temp/tempfile" + str(c) + ".png"
        save_img = img2.save(img_filename)

        files_list.append(img_filename)

    image1 = Image.open(files_list[0]).convert('RGB')

    imagelist = []

    for i in files_list[1:]:
        imagelist.append(Image.open(i).convert('RGB'))

    image1.save("movie/static/tickets/" + str(bookid.id) + ".pdf", save_all=True, append_images=imagelist)

    clear_temp()

    return "static/tickets/" + str(bookid.id) + ".pdf"


def clear_temp():
    dir = 'temp/'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))


def download_file(request):
    file = "movie/static/tickets/31.pdf"
    filename = "ticket.pdf"
    f = open(file, "rb")
    response = HttpResponse(FileWrapper(f), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=' + filename
    f.close()
    return response


def return_booking_details_collectionreport(obj):
    main_obj = Booking.objects.filter(set_time=obj)
    sum = 0
    for i in main_obj:
        sum = sum + int(float(i.price))

    return len(main_obj), str(sum)


def collection_report(request):
    context = {}
    obj = Set_Timing.objects.all()

    tz_AS = pytz.timezone("Asia/Calcutta")
    datetime_AS = datetime.datetime.now(tz_AS)
    current_time = datetime_AS.strftime("%a, %d %B %Y %I:%M %p")

    current_time = datetime.datetime.strptime(str(current_time), "%a, %d %B %Y %I:%M %p")
    send_movies = []

    for i in obj:
        main_string = str(i.screen).split(" $ ")[1]
        s_time = main_string.split(" - ")[1]

        movie_time = i.date1 + " " + s_time
        movie_time = datetime.datetime.strptime(movie_time, "%a, %d %B %Y %I:%M %p") # changed : to .

        diff = movie_time-current_time

        days, seconds = diff.days, diff.seconds
        hours = days * 24 + seconds // 3600

        if hours < 0:
            send_movies.append(i)

    context["movies_list"] = send_movies

    if request.POST:
        movie_obj = request.POST['movie_select']

        obj_check = Set_Timing.objects.all()
        for i in obj_check:
            if str(i) == str(movie_obj):
                nts, ta = return_booking_details_collectionreport(i)
                print_collection_report(i.id, i.screen.screen, i.movie.name, i.date1, i.screen.time1, nts, ta)

    return render(request, "collection.html", context)


def print_collection_report(id, screen, movie, date, show, nts, ta):
    layout = "movie/static/printer/collection/layout.png"
    img = Image.open(layout)

    # Show Date
    day = datetime.datetime.strptime(str(date), "%a, %d %B %Y").strftime("%d/%m/%y")
    week = datetime.datetime.strptime(str(date), "%a, %d %B %Y").strftime("%A")

    font = ImageFont.truetype('movie/static/printer/fonts/Open_Sans/static/OpenSans/OpenSans-ExtraBold.ttf', 40)
    draw = ImageDraw.Draw(img)
    x, y = 400, 300
    draw.text(xy=(x, y), text=day, fill=(0, 74, 173), font=font)

    font = ImageFont.truetype('movie/static/printer/fonts/Anonymous_Pro/AnonymousPro-Bold.ttf', 30)
    draw = ImageDraw.Draw(img)
    if len(week) > 7:
        x, y = 420, 350
    else:
        x, y = 440, 350
    draw.text(xy=(x, y), text=week, fill=(0, 74, 173), font=font)


    # show time
    show = show.split(" - ")

    # time
    font = ImageFont.truetype('movie/static/printer/fonts/Open_Sans/static/OpenSans/OpenSans-ExtraBold.ttf', 40)
    draw = ImageDraw.Draw(img)
    x, y = 840, 300
    draw.text(xy=(x, y), text=show[1], fill=(0, 74, 173), font=font)

    # show name
    font = ImageFont.truetype('movie/static/printer/fonts/Anonymous_Pro/AnonymousPro-Bold.ttf', 30)
    draw = ImageDraw.Draw(img)
    x, y = 880, 350
    draw.text(xy=(x, y), text=show[0], fill=(0, 74, 173), font=font)

    # Screen
    font = ImageFont.truetype('movie/static/printer/fonts/Open_Sans/static/OpenSans/OpenSans-ExtraBold.ttf', 60)
    draw = ImageDraw.Draw(img)
    x, y = 550, 100
    draw.text(xy=(x, y), text=str(screen), fill=(0, 74, 173), font=font)


    # movie
    if len(movie) > 40:
        font = ImageFont.truetype('movie/static/printer/fonts/Open_Sans/static/OpenSans/OpenSans-ExtraBold.ttf', 23)
    else:
        font = ImageFont.truetype('movie/static/printer/fonts/Open_Sans/static/OpenSans/OpenSans-ExtraBold.ttf', 30)
    draw = ImageDraw.Draw(img)
    x, y = 430, 470
    draw.text(xy=(x, y), text=movie, fill=(0, 74, 173), font=font)

    # nts
    font = ImageFont.truetype('movie/static/printer/fonts/Anonymous_Pro/AnonymousPro-Bold.ttf', 60)
    draw = ImageDraw.Draw(img)
    x, y = 510, 690
    draw.text(xy=(x, y), text=str(nts), fill=(0, 74, 173), font=font)

    # ta
    font = ImageFont.truetype('movie/static/printer/fonts/Anonymous_Pro/AnonymousPro-Bold.ttf', 60)
    draw = ImageDraw.Draw(img)
    x, y = 780, 690
    draw.text(xy=(x, y), text=str(ta), fill=(0, 74, 173), font=font)

    # printing the id
    font = ImageFont.truetype('movie/static/printer/fonts/Anonymous_Pro/AnonymousPro-Bold.ttf', 25)
    draw = ImageDraw.Draw(img)
    x, y = 955, 836
    draw.text(xy=(x, y), text=str(id), fill=(0, 74, 173), font=font)

    img.show()


def set_show(request):
    context = {}
    main_d, screens_l = start_variables()
    context['screens'] = screens_l

    context["selected_screen"] = main_d[screens_l[0]]

    if request.GET:
        selected_screen = request.GET['new_data']
        return JsonResponse(main_d[selected_screen], safe=False)

    if request.POST:
        selected_screen = request.POST['screen']

        post_query = str(request.POST).split("'selected_show': ")[-1]

        show_timings = eval(post_query[:-2])
        print(selected_screen)

        for i in range(len(show_timings)):
            show_timings[i] = "Show " + str(i+1) + " - " + show_timings[i]

        print(show_timings)

        obj = Movie_Time.objects.filter(screen=selected_screen)

        c = 0
        for i in obj:
            c = c + 1
            change_obj = Movie_Time.objects.filter(id=i.id)
            change_obj.update(time1=show_timings[c])

    return render(request, "setshow.html", context)

# Conditions:
# 1. Screen name length <= 8
# 2. Enable pop-up from every links
# 3. Add movie_movie_time datas before adding a movie

