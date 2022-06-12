from django.db import models
from django.contrib.auth.models import User


class Movie_Time(models.Model):
    screen = models.CharField(max_length=100, null=True)
    time1 = models.CharField(max_length=100, null=True)
    screen_id = models.IntegerField(null=True)

    def __str__(self):
        return str(self.screen) + " $ " + str(self.time1)


class Movie(models.Model):
    name=models.CharField(max_length=1000, null=True)
    screen = models.CharField(max_length=1000, null=True)
    shows = models.CharField(max_length=1000, default="")
    from_date = models.DateField(null=True)
    to_date = models.DateField(null=True)

    def __str__(self):
        return self.name


class Set_Timing(models.Model):
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE, null=True)
    date1 = models.CharField(max_length=100, null=True)
    # time1 = models.CharField(max_length=100, null=True)
    # screen = models.CharField(max_length=100, null=True)
    screen = models.ForeignKey(Movie_Time, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.movie.name + " " + self.screen.screen + " " + self.screen.time1 + " " + self.date1


class Booking(models.Model):
    set_time = models.ForeignKey(Set_Timing, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=100, null=True)
    time = models.CharField(max_length=100, null=True)
    seat = models.CharField(max_length=100, null=True)
    price = models.CharField(max_length=100, null=True)
    ticket = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.set_time.movie.name+" "


class Pending(models.Model):
    set_time = models.ForeignKey(Set_Timing, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=100, null=True)
    time = models.CharField(max_length=100, null=True)
    seat = models.CharField(max_length=100, null=True)
    price = models.CharField(max_length=100, null=True)
    ticket = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.set_time.movie.name+" "


class cats_seat(models.Model):
    cats_name = models.CharField(max_length=1000, null=True)
    seats_list = models.CharField(max_length=1000, null=True, default="[[],[],[],[],[]]")
    seats_count = models.CharField(max_length=1000, null=True, default=0)
    amount = models.IntegerField(null=True)
    color = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return str(self.cats_name) + " - " + str(self.amount)


# class Screen1(models.Model):
#     gold = models.IntegerField()
#
#
# class Screen2(models.Model):
#     gold = models.IntegerField()
#     platinum = models.IntegerField()
#
#
# class Screen3(models.Model):
#     gold = models.IntegerField()
#     platinum = models.IntegerField()
#
#
# class Screen4(models.Model):
#     gold = models.IntegerField()
#
#
# class Screen5(models.Model):
#     gold = models.IntegerField()
