import psycopg2


def showAll():
    mydb2 = psycopg2.connect(
        host="ec2-34-233-214-228.compute-1.amazonaws.com",
        database="dadrqp9b62mj0q",
        user="gtwiaeahsyqzcd",
        password="a9e3dfe1b8125c85b56bde84f33d845d9ca029c29104d3af78911d9eb04bd215"
    )

    mycursor2 = mydb2.cursor()

    sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
    mycursor2.execute(sql)
    out = mycursor2.fetchall()
    print(out)
    mydb2.commit()


def add_movie_time(screen, show, id):
    mydb2 = psycopg2.connect(
        host="ec2-34-233-214-228.compute-1.amazonaws.com",
        database="dadrqp9b62mj0q",
        user="gtwiaeahsyqzcd",
        password="a9e3dfe1b8125c85b56bde84f33d845d9ca029c29104d3af78911d9eb04bd215"
    )

    mycursor2 = mydb2.cursor()

    # sql = "INSERT INTO movie_movie_time(screen, time1, screen_id) VALUES  ('Screen 1', 'Show 1 - 9.00 AM', 1);"
    sql = "INSERT INTO movie_movie_time(screen, time1, screen_id) VALUES  ('" + str(screen) + "', '" + str(
        show) + "', " + str(id) + ");"
    mycursor2.execute(sql)
    mydb2.commit()


def start_add_movie_time():
    screens = ["Screen 1", "Screen 2", "Screen 3", "Screen 4", "Screen 5"]
    timings = ["Show 1 - 9.00 AM", "Show 2 - 12.00 PM", "Show 3 - 3.00 PM", "Show 4 - 6.00 PM", "Show 5 - 9.00 PM"]

    for i in screens:
        for j in timings:
            print(i, " for ", j, "and id = ", screens.index(i) + 1)
            add_movie_time(i, j, screens.index(i) + 1)

# showAll() #  ('movie_booking',), ('movie_cats_seat',), ('movie_movie',), ('movie_movie_time',), ('movie_pending',), ('movie_set_timing')
