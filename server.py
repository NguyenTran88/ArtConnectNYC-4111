"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import json
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import (
    Flask,
    request,
    render_template,
    g,
    redirect,
    Response,
    abort,
    session,
    url_for,
)

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
app = Flask(__name__, template_folder=tmpl_dir)
# app.config["SECRET_KEY"] = "dont tell anyone"

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
DATABASEURI = "postgresql://ec3365:394036@34.74.171.121/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
conn = engine.connect()

# The string needs to be wrapped around text()

# conn.execute(
#     text(
#         """CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );"""
#     )
# )
# conn.execute(
#     text(
#         """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');"""
#     )
# )

# To make the queries run, we need to add this commit line

# conn.commit()


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback

        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route("/")
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

    """

    # DEBUG: this is debugging code to see what request looks like
    # print(request.args)

    #
    # example of a database query
    #
    cursor = g.conn.execute(text("SELECT name FROM test"))
    g.conn.commit()

    # 2 ways to get results

    # Indexing result by column number
    names = []
    for result in cursor:
        names.append(result[0])

    # Indexing result by column name
    names = []
    results = cursor.mappings().all()
    for result in results:
        names.append(result["name"])
    cursor.close()
    # names  = []
    # names.append({'name':})
    #
    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    # context are the variables that are passed to the template.
    # for example, "data" key in the context variable defined below will be
    # accessible as a variable in index.html:
    #
    #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
    #     <div>{{data}}</div>
    #
    #     # creates a <div> tag for each element in data
    #     # will print:
    #     #
    #     #   <div>grace hopper</div>
    #     #   <div>alan turing</div>
    #     #   <div>ada lovelace</div>
    #     #
    #     {% for n in data %}
    #     <div>{{n}}</div>
    #     {% endfor %}
    #
    context = dict(data=names)

    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    return render_template("index.html", **context)


#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#


@app.route("/another", methods=["POST", "GET"])
def another():
    return render_template("another.html")


# Example of adding new data to the database
@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    params_dict = {"name": name}
    g.conn.execute(text("INSERT INTO test(name) VALUES (:name)"), params_dict)
    g.conn.commit()

    return redirect("/")


@app.route("/artist_login")
def login():
    abort(401)
    this_is_never_executed()


skills_mapping = {
    "DJ": 0,
    "Jazz musician": 1,
    "classical musician": 2,
    "painter": 3,
    "illustrator": 4,
    "ceramics": 5,
    "sculpture": 6,
    "portrait": 7,
    "piano": 8,
    "acrylics": 9,
    "modeling": 10,
}


@app.route("/search_artist", methods=["POST", "GET"])
def search_artist():
    # # name, skill, product, service, location
    if request.method == "GET":
        return render_template("search_artist.html")

    input_field = next(iter(request.form.keys()), None)
    user_info = []
    if input_field:
        input = request.form[input_field]

        input_list = input.split(", ")
        if input_field == "name":
            for actual_name in input_list:
                params_dict = {"actual_name": actual_name}
                cursor = g.conn.execute(
                    text(
                        """SELECT * FROM users U, artist A WHERE U.user_id = A.user_id AND U.name = :actual_name"""
                    ),
                    params_dict,
                )
                g.conn.commit()
                for result in cursor:
                    # user_info.append(result)
                    user_info.append(
                        {
                            "id1": result[0],
                            "name": result[1],
                            "location": result[2],
                            "email": result[3],
                            "bio": result[4],
                            "id2": result[5],
                            "portfolio_link": result[6],
                            "price_lower_bound": result[7],
                            "price_upper_bound": result[8],
                            "availableforhire": result[9],
                        }
                    )
                    print(result)
        elif input_field == "location":
            for actual_location in input_list:
                params_dict = {"actual_location": actual_location}
                cursor = g.conn.execute(
                    text(
                        """SELECT * FROM users U, artist A WHERE U.user_id = A.user_id AND U.location = :actual_location"""
                    ),
                    params_dict,
                )
                g.conn.commit()
                for result in cursor:
                    user_info.append(
                        {
                            "id1": result[0],
                            "name": result[1],
                            "location": result[2],
                            "email": result[3],
                            "bio": result[4],
                            "id2": result[5],
                            "portfolio_link": result[6],
                            "price_lower_bound": result[7],
                            "price_upper_bound": result[8],
                            "availableforhire": result[9],
                        }
                    )
                    print(result)

        elif input_field == "skill":
            for actual_skill in input_list:
                skill_id = skills_mapping[actual_skill]
                params_dict = {"actual_skill": skill_id}
                print("This is skill_id", skill_id)
                cursor = g.conn.execute(
                    text(
                        """SELECT * FROM users U, artist A, has H WHERE U.user_id = A.user_id AND A.user_id = H.user_id AND H.skill_id = :actual_skill"""
                    ),
                    params_dict,
                )
                g.conn.commit()
                for result in cursor:
                    user_info.append(
                        {
                            "id1": result[0],
                            "name": result[1],
                            "location": result[2],
                            "email": result[3],
                            "bio": result[4],
                            "id2": result[5],
                            "portfolio_link": result[6],
                            "price_lower_bound": result[7],
                            "price_upper_bound": result[8],
                            "availableforhire": result[9],
                            "skill_id": result[10],  # why the hell ?
                            # (8, 'Taylor', '11375', 'dummy7@gmail.com', 'for fun', 8, 'test.com', 20, 1000, True, 4, 8, 8)
                        }
                    )
                    print(result)

        elif input_field == "product":
            for actual_product in input_list:
                params_dict = {"actual_product": actual_product}
                cursor = g.conn.execute(
                    text(
                        """SELECT * FROM users U, artist A, poffers_products P WHERE U.user_id = A.user_id AND A.user_id = P.user_id AND P.medium = :actual_product"""
                    ),
                    params_dict,
                )
                g.conn.commit()
                for result in cursor:
                    user_info.append(
                        {
                            "id1": result[0],
                            "name": result[1],
                            "location": result[2],
                            "email": result[3],
                            "bio": result[4],
                            "id2": result[5],
                            "portfolio_link": result[6],
                            "price_lower_bound": result[7],
                            "price_upper_bound": result[8],
                            "availableforhire": result[9],
                            "product_id": result[11],
                            "medium": result[11],
                            "price": result[12],
                            "inStock": result[13],
                        }
                    )
                    print(result)
        elif input_field == "service":
            for actual_service in input_list:
                params_dict = {"actual_service": actual_service}
                cursor = g.conn.execute(
                    text(
                        """SELECT * FROM users U, artist A, soffers_services S WHERE U.user_id = A.user_id AND A.user_id = S.user_id AND S.service_type = :actual_service"""
                    ),
                    params_dict,
                )
                g.conn.commit()
                for result in cursor:
                    user_info.append(
                        {
                            "id1": result[0],
                            "name": result[1],
                            "location": result[2],
                            "email": result[3],
                            "bio": result[4],
                            "id2": result[5],
                            "portfolio_link": result[6],
                            "price_lower_bound": result[7],
                            "price_upper_bound": result[8],
                            "availableforhire": result[9],
                            "service_id": result[11],
                            "service_type": result[12],
                            "styles": result[13],
                            "time_needed": result[14],
                            "price": result[15],
                        }
                    )
                    print(result)
    print("my_user_info", user_info)

    return redirect(url_for("view", users=json.dumps(user_info)))


@app.route("/view/<users>", methods=["POST", "GET"])
def view(users):
    print("view print", type(users[0]))
    users = json.loads(users)
    context = dict(users=users)
    return render_template("view.html", **context)


# @app.route("/view", methods=["POST", "GET"])
# def view():
#     user_info = session.get("user_info", [])
#     return render_template("view.html", users=user_info)


@app.route("/search_customer", methods=["POST", "GET"])
def search_customer():
    if request.method == "GET":
        return render_template("search_customer.html")

    input_field = next(iter(request.form.keys()), None)
    input = request.form[input_field]

    input_list = input.split(", ")

    user_info = []
    if input_field:
        if input_field == "name":
            for actual_name in input_list:
                params_dict = {"actual_name": actual_name}
                print(params_dict, "actual_name", actual_name)
                cursor = g.conn.execute(
                    text(
                        """SELECT * FROM users U, customer C WHERE U.user_id = C.user_id AND U.name = :actual_name"""
                    ),
                    params_dict,
                )
                g.conn.commit()
                for result in cursor:
                    user_info.append(
                        {
                            "name": result[1],
                            "location": result[2],
                            "email": result[3],
                            "bio": result[4],
                            "hiring": result[6],
                        }
                    )
                    print(result)
        elif input_field == "location":
            for actual_location in input_list:
                params_dict = {"actual_location": actual_location}
                cursor = g.conn.execute(
                    text(
                        """SELECT * FROM users U, customer C WHERE U.user_id = C.user_id AND U.location = :actual_location"""
                    ),
                    params_dict,
                )
                g.conn.commit()
                for result in cursor:
                    user_info.append(
                        {
                            "name": result[1],
                            "location": result[2],
                            "email": result[3],
                            "bio": result[4],
                            "hiring": result[6],
                        }
                    )
                    print(result)

        elif input_field == "industry":
            for actual_industry in input_list:
                params_dict = {"actual_industry": actual_industry}
                cursor = g.conn.execute(
                    text(
                        """SELECT * FROM users U, customer C, owns_business B WHERE U.user_id = C.user_id AND C.user_id = B.user_id AND B.industry = :actual_industry"""
                    ),
                    params_dict,
                )
                g.conn.commit()
                for result in cursor:
                    user_info.append(
                        {
                            "name": result[1],
                            "email": result[3],
                            "location": result[2],
                            "hiring": result[6],
                            "industry": result[9],
                        }
                    )
                    print(result)

        elif input_field == "product":
            # choose products based on medium: i.e: I want to buy a painting, sculpture,...
            for actual_product in input_list:
                params_dict = {"actual_product": actual_product}
                cursor = g.conn.execute(
                    text(
                        """SELECT * FROM users U, customer C, make_request R WHERE U.user_id = C.user_id AND C.user_id = R.user_id AND R.product_name = :actual_product"""
                    ),
                    params_dict,
                )
                g.conn.commit()
                for result in cursor:
                    user_info.append(
                        {
                            "name": result[1],
                            "email": result[3],
                            "location": result[2],
                            "hiring": result[6],
                            "service_type": result[11],
                            "product_name": result[12],
                        }
                    )
                    print(result)
        elif input_field == "service":
            for actual_service in input_list:
                params_dict = {"actual_service": actual_service}
                cursor = g.conn.execute(
                    text(
                        """SELECT * FROM users U, customer C, make_request R WHERE U.user_id = C.user_id AND C.user_id = R.user_id AND R.service_type = :actual_service"""
                    ),
                    params_dict,
                )
                g.conn.commit()
                for result in cursor:
                    user_info.append(
                        {
                            "name": result[1],
                            "email": result[3],
                            "location": result[2],
                            "hiring": result[6],
                            "service_type": result[11],
                            "product_name": result[12],
                        }
                    )
                    print(result)
    print("my_user_info", user_info)
    return redirect(url_for("view", users=json.dumps(user_info)))


@app.route("/create_artist_profile", methods=["POST", "GET"])
def create_artist_profile():
    if request.method == "GET":
        return render_template("login.html")

    name_value = request.form["name"]
    email_value = request.form["email"]

    params_dict = {"actual_name": name_value, "actual_email": email_value}
    # how to make actual_email unique ?
    cursor = g.conn.execute(
        text(
            """SELECT * FROM users U where U.name = :actual_name AND U.email = :actual_email"""
        ),
        params_dict,
    )
    g.conn.commit()

    usr_id = -1
    # insert into users if there's none in users
    if cursor.rowcount == 0:
        cursor.close()
        max_cursor = g.conn.execute(text("""SELECT MAX(user_id) FROM users"""))
        max_id = max_cursor.fetchone()[0]
        params_dict["actual_user_id"] = max_id + 1
        usr_id = max_id + 1
        max_cursor.close()

        cursor = g.conn.execute(
            text(
                """INSERT INTO users(user_id, name, email) VALUES (:actual_user_id, :actual_name, :actual_email)"""
            ),
            params_dict,
        )
        g.conn.commit()
        cursor.close()
    else:
        usr_id = cursor.fetchone()[0]
        cursor.close()
    params_dict["actual_user_id"] = usr_id
    print("usr_id", usr_id)

    # insert into artist if there's none in artist, we need to fetch user_id to do this
    cursor = g.conn.execute(
        text(
            """
        SELECT * FROM users U, artist A WHERE U.user_id = A.user_id AND U.name = :actual_name AND U.email = :actual_email"""
        ),
        params_dict,
    )
    if cursor.rowcount == 0:
        cursor = g.conn.execute(
            text("""INSERT INTO artist(user_id) VALUES (:actual_user_id)"""),
            params_dict,
        )

        g.conn.commit()
        cursor.close()

    # at this point, there's a new profile

    return redirect(url_for("edit_artist_profile", usr_id=usr_id))   


@app.route("/edit_artist_profile/<usr_id>", methods=["POST", "GET"])
def edit_artist_profile(usr_id):
    if request.method == "GET":
        return render_template("edit_artist_profile.html")

    # else, we have usr_id and can manipulate stuff
    params_dict = {"user_id": usr_id}

    # update users: => form2
    if request.form["form_id"] == "form2":
        for key, val in request.form.items():
            if (
                not val or len(val) == 0 or key == "form_id"
            ):  # form_id is not a column in table
                continue
            params_dict[key] = val

        update_query = (
            "UPDATE Users SET "
            + ", ".join([f"{key} = :{key}" for key in params_dict.keys()])
            + " WHERE user_id = :user_id"
        )
        cursor = g.conn.execute(text(update_query), params_dict)
        g.conn.commit()
        cursor.close()

    # update artist: => form1
    elif request.form["form_id"] == "form1":
        for key, val in request.form.items():
            if not val or len(val) == 0 or key == "form_id":
                continue
            params_dict[key] = val

        update_query = (
            "UPDATE Artist SET "
            + ", ".join([f"{key} = :{key}" for key in params_dict.keys()])
            + " WHERE user_id = :user_id"
        )
        cursor = g.conn.execute(text(update_query), params_dict)
        g.conn.commit()
        cursor.close()

    # update product: => form3\
    elif request.form["form_id"] == "form3":
        for key, val in request.form.items():
            if not val or len(val) == 0 or key == "form_id":
                continue
            params_dict[key] = val
        
        if params_dict["medium"] == "-":
            if params_dict["price"] == "-":
                if params_dict["inStock"] == "-":
                    update_query = (
                        "DELETE FROM poffers_products P WHERE P.user_id = :user_id AND P.product_id = :product_id"
                    )
        
        else:
            #if no product_id, but other fields => add to table
            if params_dict['product_id'] == "-":
                max_cursor = g.conn.execute(text("""SELECT MAX(product_id) FROM poffers_products"""))
                max_id = max_cursor.fetchone()[0]
                params_dict["product_id"] = max_id + 1
                product_id = max_id + 1
                max_cursor.close()
                
                cursor = g.conn.execute(
                    text(
                        """INSERT INTO poffers_products(product_id, user_id) VALUES (""" + str(params_dict["product_id"]) + "," + ":user_id)"
                    ),
                    params_dict,
                )
                
            update_query = (
            "UPDATE poffers_products SET "
            + ", ".join([f"{key} = :{key}" for key in params_dict.keys()])
            + " WHERE user_id = :user_id"
        )
        
        cursor = g.conn.execute(text(update_query), params_dict)
        g.conn.commit()
        cursor.close()

    # update service: => form4\
    elif request.form["form_id"] == "form4":
        for key, val in request.form.items():
            if not val or len(val) == 0 or key == "form_id":
                continue
            params_dict[key] = val
        
        if params_dict["service_type"] == "-":
            if params_dict["styles"] == "-":
                if params_dict["time_needed"] == "-":
                    if params_dict["price"] == "-":
                        update_query = (
                            "DELETE FROM soffers_services S WHERE S.user_id = :user_id AND S.service_id = :service_id"
                        )
        
        else:
            #if no product_id, but other fields => add to table
            if params_dict['service_id'] == "-":
                max_cursor = g.conn.execute(text("""SELECT MAX(service_id) FROM soffers_services"""))
                max_id = max_cursor.fetchone()[0]
                params_dict["service_id"] = max_id + 1
                product_id = max_id + 1
                max_cursor.close()
                
                cursor = g.conn.execute(
                    text(
                        """INSERT INTO soffers_services(service_id, user_id) VALUES (""" + str(params_dict["service_id"]) + "," + ":user_id)"
                    ),
                    params_dict,
                )
                
            update_query = (
            "UPDATE soffers_services SET "
            + ", ".join([f"{key} = :{key}" for key in params_dict.keys()])
            + " WHERE user_id = :user_id"
        )
        
        cursor = g.conn.execute(text(update_query), params_dict)
        g.conn.commit()
        cursor.close()

    #TODO: redirect to View
    return redirect(url_for("index"))

@app.route("/create_customer_profile", methods=["POST", "GET"])
def create_customer_profile():
    if request.method == "GET":
        return render_template("login.html")

    name_value = request.form["name"]
    email_value = request.form["email"]

    params_dict = {"actual_name": name_value, "actual_email": email_value}
    # how to make actual_email unique ?
    cursor = g.conn.execute(
        text(
            """SELECT * FROM users U where U.name = :actual_name AND U.email = :actual_email"""
        ),
        params_dict,
    )
    g.conn.commit()

    usr_id = -1
    # insert into users if there's none in users
    if cursor.rowcount == 0:
        cursor.close()
        max_cursor = g.conn.execute(text("""SELECT MAX(user_id) FROM users"""))
        max_id = max_cursor.fetchone()[0]
        params_dict["actual_user_id"] = max_id + 1
        usr_id = max_id + 1
        max_cursor.close()

        cursor = g.conn.execute(
            text(
                """INSERT INTO users(user_id, name, email) VALUES (:actual_user_id, :actual_name, :actual_email)"""
            ),
            params_dict,
        )
        g.conn.commit()
        cursor.close()
    else:
        usr_id = cursor.fetchone()[0]
        cursor.close()
    params_dict["actual_user_id"] = usr_id
    print("usr_id", usr_id)

    # insert into customer if there's none in customer, we need to fetch user_id to do this
    cursor = g.conn.execute(
        text(
            """
        SELECT * FROM users U, customer C WHERE U.user_id = C.user_id AND U.name = :actual_name AND U.email = :actual_email"""
        ),
        params_dict,
    )
    if cursor.rowcount == 0:
        cursor = g.conn.execute(
            text("""INSERT INTO customer(user_id) VALUES (:actual_user_id)"""),
            params_dict,
        )

        g.conn.commit()
        cursor.close()

    # at this point, there's a new profile

    return redirect(url_for("edit_customer_profile", usr_id=usr_id))   


@app.route("/edit_customer_profile/<usr_id>", methods=["POST", "GET"])
def edit_customer_profile(usr_id):
    if request.method == "GET":
        return render_template("edit_customer_profile.html")

    # else, we have usr_id and can manipulate stuff
    params_dict = {"user_id": usr_id}

    # update users: => form2
    if request.form["form_id"] == "form2":
        for key, val in request.form.items():
            if (
                not val or len(val) == 0 or key == "form_id"
            ):  # form_id is not a column in table
                continue
            params_dict[key] = val

        update_query = (
            "UPDATE Users SET "
            + ", ".join([f"{key} = :{key}" for key in params_dict.keys()])
            + " WHERE user_id = :user_id"
        )
        cursor = g.conn.execute(text(update_query), params_dict)
        g.conn.commit()
        cursor.close()

    # update customer: => form1
    elif request.form["form_id"] == "form1":
        for key, val in request.form.items():
            if not val or len(val) == 0 or key == "form_id":
                continue
            params_dict[key] = val

        update_query = (
            "UPDATE customer SET "
            + ", ".join([f"{key} = :{key}" for key in params_dict.keys()])
            + " WHERE user_id = :user_id"
        )
        cursor = g.conn.execute(text(update_query), params_dict)
        g.conn.commit()
        cursor.close()

    # update business: => form3\
    elif request.form["form_id"] == "form3":
        for key, val in request.form.items():
            if not val or len(val) == 0 or key == "form_id":
                continue
            params_dict[key] = val
        if params_dict["bName"] == "-":
            if params_dict["industry"] == "-":
                if params_dict["website"] == "-":
                    update_query = (
                        "DELETE FROM owns_business B WHERE B.user_id = :user_id AND B.business_id = :business_id"
                    )
        
        else:
            #if no business_id, but other fields => add to table
            if params_dict['business_id'] == "-":
                max_cursor = g.conn.execute(text("""SELECT MAX(business_id) FROM owns_business"""))
                max_id = max_cursor.fetchone()[0]
                params_dict["business_id"] = max_id + 1
                business_id = max_id + 1
                max_cursor.close()
                
                cursor = g.conn.execute(
                    text(
                        """INSERT INTO owns_business(business_id, user_id) VALUES (""" + str(params_dict["business_id"]) + "," + ":user_id)"
                    ),
                    params_dict,
                )
                
            update_query = (
            "UPDATE owns_business SET "
            + ", ".join([f"{key} = :{key}" for key in params_dict.keys()])
            + " WHERE user_id = :user_id"
        )
        
        cursor = g.conn.execute(text(update_query), params_dict)
        g.conn.commit()
        cursor.close()

    # update service: => form4\
    elif request.form["form_id"] == "form4":
        for key, val in request.form.items():
            if not val or len(val) == 0 or key == "form_id":
                continue
            params_dict[key] = val
        
        if params_dict["time_frame_day"] == "-":
            if params_dict["max_budget"] == "-":
                if params_dict["service_type"] == "-":
                    if params_dict["product_name"] == "-":
                        update_query = (
                            "DELETE FROM make_request R WHERE R.user_id = :user_id AND R.request_id = :request_id"
                        )
        
        else:
            #if no request_id, but other fields => add to table
            if params_dict['request_id'] == "-":
                max_cursor = g.conn.execute(text("""SELECT MAX(request_id) FROM make_request"""))
                max_id = max_cursor.fetchone()[0]
                params_dict["request_id"] = max_id + 1
                request_id = max_id + 1
                max_cursor.close()
                
                cursor = g.conn.execute(
                    text(
                        """INSERT INTO make_request(request_id, user_id) VALUES (""" + str(params_dict["request_id"]) + "," + ":user_id)"
                    ),
                    params_dict,
                )
                
            update_query = (
            "UPDATE make_request SET "
            + ", ".join([f"{key} = :{key}" for key in params_dict.keys()])
            + " WHERE user_id = :user_id"
        )
        
        cursor = g.conn.execute(text(update_query), params_dict)
        g.conn.commit()
        cursor.close()

    #TODO: redirect to View
    return redirect(url_for("index"))


def getUsrId(name, email):
    params_dict = {"actual_name": name, "actual_email": email}
    cursor = g.conn.execute(
        text(
            """SELECT U.user_id FROM users U where U.name = :actual_name AND U.email = :actual_email"""
        ),
        params_dict,
    )
    g.conn.commit()
    row = cursor.fetchone()
    cursor.close()
    if not row:
        return -1
    else:
        return row[0]


if __name__ == "__main__":
    import click

    @click.command()
    @click.option("--debug", is_flag=True)
    @click.option("--threaded", is_flag=True)
    @click.argument("HOST", default="0.0.0.0")
    @click.argument("PORT", default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

            python3 server.py

        Show the help text using:

            python3 server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()