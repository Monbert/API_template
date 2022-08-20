#!/usr/bin/python
import azure.functions as func
import psycopg2
from datetime import datetime, date
import logging
import os


# DB Queries
# GET data
GET_ALL_USER_STATUS = "SELECT * FROM user_status LIMIT %s OFFSET %s;"
GET_ALL_USER_STATUS_WITH_MANAGER = """
SELECT 
us.user_status_id,
us.domain_rhonda_id, 
CONCAT_WS(' ',u.first_name, u.last_name) AS employee, 
CONCAT_WS(' ', u2.first_name, u2.last_name) AS manager,
us.status, 
us.employee_environment, 
us.department, 
us.work_type, 
us.work_location, 
us.gender, 
us.birth_date, 
us.start_date, 
us.end_date 
FROM user_status us 
LEFT JOIN public.user u
ON us.domain_rhonda_id = u.domain_rhonda_id
LEFT JOIN public.user u2
ON us.manager_id = u2.domain_rhonda_id
LEFT JOIN user_info ui 
ON us.manager_id = ui.domain_rhonda_id 
WHERE us.status LIKE %s and us.employee_environment LIKE %s
LIMIT %s OFFSET %s;"""
GET_USER_STATUS_BY_DOMAIN_RHONDA_ID = """SELECT * FROM user_status
WHERE user_status.domain_rhonda_id = %s;"""
COUNT_USER_STATUS_ROWS = "SELECT COUNT(*) FROM user_status;"

# INSERT data
INSERT_USER_STATUS = """INSERT INTO user_status (domain_rhonda_id, status, employee_environment, department, work_type, manager_id, work_location, gender, birth_date, start_date, end_date)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (domain_rhonda_id) DO NOTHING
RETURNING domain_rhonda_id;"""

# UPDATE data
UPDATE_USER_STATUS = """UPDATE user_status
SET status = %s,
employee_environment = %s,
department = %s,
work_type = %s,
manager_id = %s,
work_location = %s,
gender = %s,
birth_date = %s,
start_date = %s,
end_date = %s
WHERE domain_rhonda_id = %s
RETURNING domain_rhonda_id;
"""

# DELETE data
DELETE_USER_STATUS = """DELETE FROM user_status
WHERE domain_rhonda_id = %s
RETURNING domain_rhonda_id;
"""


# DB Connection
def connection():
    """Connect to the PostgreSQL database server"""
    try:

        HOST = os.environ["RP_HOST"]
        DATABASE = os.environ["RP_DATABASE"]
        USERNAME = os.environ["RP_USERNAME"]
        PASSWORD = os.environ["RP_PASSWORD"]

        conn = psycopg2.connect(host=HOST, database=DATABASE, user=USERNAME, password=PASSWORD)
        return conn

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error("DB Connection Exception:")
        logging.error(error)
        return None


connection = connection()

# Functions


def date_converter(obj):
    """Transform date to str. If there is no date it will return 1900-01-01

    Args:
        obj ([date]): date

    Returns:
        [str]: date as string
    """
    if isinstance(obj, date):
        return obj.strftime("%Y-%m-%d")
    return "1900-01-01"


def datetime_converter(obj):
    """Transform datetime to str. If there is no date it will return 1900-01-01T00:00:00

    Args:
        obj ([datetime]): datetime

    Returns:
        [str]: datetime as string
    """
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%dT%H:%M:%S")
    return "1900-01-01T00:00:00"


def get_all_user_status(page_size, page):
    """This function will return data from user_status table.
    Size will be defined by page_size and it will depen on page number.

    Returns:
        [list]: user_status data depending on page and page_size.
    """
    try:
        user_status_data = []

        page = int(page) - 1
        offset = int(page_size) * int(page)

        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_ALL_USER_STATUS, (page_size, offset))
                results = cursor.fetchall()
                if not results:
                    logging.info(f"message: There is no results for all users status.")
                    return {}
                for row in results:
                    user_status = {
                        "user_status_id": row[0],
                        "domain_rhonda_id": row[1],
                        "status": row[2],
                        "employee_environment": row[3],
                        "department": row[4],
                        "work_type": row[5],
                        "manager_id": row[6],
                        "work_location": row[7],
                        "gender": row[8],
                        "birth_date": date_converter(row[9]),
                        "start_date": date_converter(row[10]),
                        "end_date": date_converter(row[11]),
                        "created_at": datetime_converter(row[12]),
                        "updated_at": datetime_converter(row[13]),
                    }
                    user_status_data.append(user_status)
                return user_status_data
    except Exception as error:
        logging.error("Error: SELECT all user_status exception!")
        logging.error(error)
        logging.error("Error: SELECT all user_status exception end")
        return func.HttpResponse(f"{error}")


def get_user_status_by_domain_rhonda_id(domain_rhonda_id):
    """This function will return all data from user_status table filtered by domain_rhonda_id.

    Returns:
        [list]: All user_status data filtered by domain_rhonda_id.
    """
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_USER_STATUS_BY_DOMAIN_RHONDA_ID, (domain_rhonda_id,))
                results = cursor.fetchall()
                if not results:
                    logging.info(f"message: There is no result for domain_rhonda_id: {domain_rhonda_id}")
                    return {}
                for row in results:
                    user_status = {
                        "user_status_id": row[0],
                        "domain_rhonda_id": row[1],
                        "status": row[2],
                        "employee_environment": row[3],
                        "department": row[4],
                        "work_type": row[5],
                        "manager_id": row[6],
                        "work_location": row[7],
                        "gender": row[8],
                        "birth_date": date_converter(row[9]),
                        "start_date": date_converter(row[10]),
                        "end_date": date_converter(row[11]),
                        "created_at": datetime_converter(row[12]),
                        "updated_at": datetime_converter(row[13]),
                    }
                return user_status
    except Exception as error:
        logging.error("Error: SELECT user_status by domain_rhonda_id exception!")
        logging.error(error)
        logging.error("Error: SELECT user_status by domain_rhonda_id exception end")
        return func.HttpResponse(f"{error}")


def get_all_user_status_with_manager(status_param, employee_environment_param, page_size, page):
    """This function will return data from user_status table with manager name.
    Size will be defined by page_size and it will depen on page number.

    Returns:
        [list]: user_status data depending on page and page_size.
    """
    try:
        user_status_manager_data = []

        page = int(page) - 1
        offset = int(page_size) * int(page)

        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    GET_ALL_USER_STATUS_WITH_MANAGER, (status_param, employee_environment_param, page_size, offset)
                )
                results = cursor.fetchall()
                if not results:
                    logging.info(f"message: There is no results for all users status with manager.")
                    return {}
                for row in results:
                    user_status_with_manager = {
                        "user_status_id": row[0],
                        "domain_rhonda_id": row[1],
                        "employee": row[2],
                        "manager": row[3],
                        "status": row[4],
                        "employee_environment": row[5],
                        "department": row[6],
                        "work_type": row[7],
                        "work_location": row[8],
                        "gender": row[9],
                        "birth_date": date_converter(row[10]),
                        "start_date": date_converter(row[11]),
                        "end_date": date_converter(row[12]),
                    }
                    user_status_manager_data.append(user_status_with_manager)
                return user_status_manager_data
    except Exception as error:
        logging.error("Error: SELECT all user_status with manager exception!")
        logging.error(error)
        logging.error("Error: SELECT all user_status with manager exception end")
        return func.HttpResponse(f"{error}")


def add_user_status(
    domain_rhonda_id,
    status,
    employee_environment,
    department,
    work_type,
    manager_id,
    work_location,
    gender,
    birth_date,
    start_date,
    end_date,
):
    """This function will insert new data in user_status table in DB if not already exists. If alredy exists it won't do anything.

    Args:
        domain_rhonda_id ([str]): unique domain_rhonda_id
        status ([str]): It can be only Active or Termiated
        employee_environment ([str]): It can be only Internal, External or Other(defualt).
        department ([str]): Any string value, it can be null
        work_type ([str]): It can be only Permanent(default), Temporary or Contract.
        manager_id([str]): It can be null. This is domain_rhonda_id.
        work_location ([str]): It can null but only be Canada, USA or EU.
        gender ([str]): It can be null but only Male, Female or Intersex.
        birth_date ([str]): "YYYY-MM-DD" format, it can be null
        start_date ([str]): "YYYY-MM-DD" format, it can be null
        end_date ([str]): "YYYY-MM-DD" format, it can be null
    """
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    INSERT_USER_STATUS,
                    (
                        domain_rhonda_id,
                        status,
                        employee_environment,
                        department,
                        work_type,
                        manager_id,
                        work_location,
                        gender,
                        birth_date,
                        start_date,
                        end_date,
                    ),
                )
                return f"{cursor.fetchone()[0]} has been added successfully!"
    except Exception as error:
        logging.error("Error: INSERT user_status exception!")
        logging.error(error)
        logging.error("Error: INSERT user_status exception end")
        return func.HttpResponse(f"{error}")


def update_user_status(
    status,
    employee_environment,
    department,
    work_type,
    manager_id,
    work_location,
    gender,
    birth_date,
    start_date,
    end_date,
    domain_rhonda_id,
):
    """This function will update data in user_status table in DB by domain_rhonda_id.

    Args:
        domain_rhonda_id ([str]): unique domain_rhonda_id
        status ([str]): It can be only Active or Termiated
        employee_environment ([str]): It can be only Internal, External or Other(defualt).
        department ([str]): Any string value, it can be null
        work_type ([str]): It can be only Permanent(default), Temporary or Contract.
        manager_id([str]): It can be null. This is domain_rhonda_id.
        work_location ([str]): It can null but only be Canada, USA or EU.
        gender ([str]): It can be null but only Male, Female or Intersex.
        birth_date ([str]): "YYYY-MM-DD" format, it can be null
        start_date ([str]): "YYYY-MM-DD" format, it can be null
        end_date ([str]): "YYYY-MM-DD" format, it can be null
    """
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    UPDATE_USER_STATUS,
                    (
                        status,
                        employee_environment,
                        department,
                        work_type,
                        manager_id,
                        work_location,
                        gender,
                        birth_date,
                        start_date,
                        end_date,
                        domain_rhonda_id,
                    ),
                )

                return f"{cursor.fetchone()[0]} has been updated successfully!"
    except Exception as error:
        logging.error("Error: UPDATE user_status exception!")
        logging.error(error)
        logging.error("Error: UPDATE user_status exception end")
        return func.HttpResponse(f"{error}")


def count_user_status_rows():
    """Count rows in DB.

    Returns:
        [int]: Number of rows in db.
    """
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(COUNT_USER_STATUS_ROWS)
                return cursor.fetchall()[0][0]
    except Exception as error:
        logging.error("Error: count_user_status_rows exception!")
        logging.error(error)
        logging.error("Error: count_user_status_rows exception end")
        return func.HttpResponse(f"{error}")


def user_status_max_page(page_size):
    """Depending on page_size we will get number of pages.

    Args:
        page_size ([int]): Number of rows per page.

    Returns:
        [int]: Number of pages
    """
    try:
        total_rows = int(count_user_status_rows())
        if total_rows % int(page_size) != 0:
            max_page = int(total_rows / int(page_size)) + 1
        else:
            max_page = int(total_rows / int(page_size))

        return max_page
    except Exception as error:
        logging.error("Error: user_status_max_page exception!")
        logging.error(error)
        logging.error("Error: user_status_max_page exception end")
        return func.HttpResponse(f"{error}")


def delete_user_status(domain_rhonda_id):
    """This will delete user_status by domain_rhonda_id

    Args:
        domain_rhonda_id ([str]): domain_rhonda_id

    Returns:
        [str]: domain_rhonda_id that has been deleted.
    """
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(DELETE_USER_STATUS, (domain_rhonda_id,))
                print(f"Delete cursor: {cursor.fetchone()[0]}")
    except Exception as error:
        logging.error("Error: DELETE user_status by domain_rhonda_id exception!")
        logging.error(error)
        logging.error("Error: DELETE user_status by domain_rhonda_id exception end")
        return func.HttpResponse(f"{error}")
