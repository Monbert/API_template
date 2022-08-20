import logging
import json
from datetime import datetime
import azure.functions as func
from . import user_status_functions


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f"API: user_status")
    logging.info(f"Timestamp: {datetime.utcnow()}")
    logging.info(f"URL: {req.url}")
    logging.info(f"Method: {req.method}")

    '''
    200 - OK
    201 - Created [POST]
    204 - No Content [DELETE/PUT] if succeed
    404 - Not found [GET/DELETE/PUT]
    400 - Bad request - due to validation issue (Missing required fields, etc) [POST/PUT]
    409 - Conflict (POST request with same ID) [POST]
    500 - Internal Server Error (Should be only in exception block) [ALL]
    '''

    if "GET" == req.method:
        try:
            domain_rhonda_id = req.route_params.get("domain_rhonda_id")
            url_prefix = req.route_params.get("url_prefix")
            page_size = int(req.params.get("page_size", 20))
            page = int(req.params.get("page", 1))

            # GET data for for specific domain_rhonda_id
            if url_prefix == "user-id":
                try:
                    result = user_status_functions.get_user_status_by_domain_rhonda_id(domain_rhonda_id)
                    if not result:
                        return func.HttpResponse(
                            body=json.dumps({"message": f"{domain_rhonda_id} does not exist!"}),
                            status_code=404,
                            charset="utf-8",
                            mimetype="application/json",
                        )
                    return func.HttpResponse(
                        body=json.dumps(result), status_code=200, charset="utf-8", mimetype="application/json"
                    )
                except Exception as error:
                    logging.error(f"Error: {error}")
                    return func.HttpResponse(
                        body=json.dumps({"message": f"{error}"}),
                        status_code=404, #HY - Should be 500 Internal Server Error
                        charset="utf-8",
                        mimetype="application/json",
                    )
            # GET all data with manager added
            if url_prefix == "user-status-hr":
                count = user_status_functions.count_user_status_rows()
                max_page = user_status_functions.user_status_max_page(page_size)
                status_param = req.params.get("status", "%")
                employee_environment_param = req.params.get("environment", "%")
                if page:
                    user_status_dat = user_status_functions.get_all_user_status_with_manager(
                        status_param, employee_environment_param, page_size, page
                    )
                    previous_page = None
                    if int(page) > 1 and int(page) <= int(max_page):
                        previous_page = page - 1
                    else:
                        previous_page = None

                    if int(page) >= 0 and int(page) < int(max_page):
                        next_page = page + 1
                    else:
                        next_page = None
                    result = {
                        "count": count,
                        "max_page": max_page,
                        "previous": {"page": previous_page, "page_size": page_size},
                        "next": {"page": next_page, "page_size": page_size},
                        "results": user_status_dat,
                    }

                return func.HttpResponse(
                    body=json.dumps(result), status_code=200, charset="utf-8", mimetype="application/json"
                )

            # GET all data
            count = user_status_functions.count_user_status_rows()
            max_page = user_status_functions.user_status_max_page(page_size)
            if page:
                user_status_dat = user_status_functions.get_all_user_status(page_size, page)
                previous_page = None
                if int(page) > 1 and int(page) <= int(max_page):
                    previous_page = page - 1
                else:
                    previous_page = None

                if int(page) >= 0 and int(page) < int(max_page):
                    next_page = page + 1
                else:
                    next_page = None
                result = {
                    "count": count,
                    "max_page": max_page,
                    "previous": {"page": previous_page, "page_size": page_size},
                    "next": {"page": next_page, "page_size": page_size},
                    "results": user_status_dat,
                }

            return func.HttpResponse(
                body=json.dumps(result), status_code=200, charset="utf-8", mimetype="application/json"
            )

        except Exception as error:
            logging.error(f"Error:{error}")
            return func.HttpResponse(
                body=json.dumps({"message": f"{error}"}), status_code=404, charset="utf-8", mimetype="application/json"
            )

    # PUT data
    elif "PUT" == req.method:
        try:
            req_body = req.get_json()
            domain_rhonda_id = req.route_params.get("domain_rhonda_id", None)

            # Check if UUID is passed            
            if domain_rhonda_id:

                ''' -----
                HY
                Need a validation right here
                1. Check if field type is correct
                2. Check if Null/None/Empty field ---> Return 4xx request
                3. Check field length (Make sure does not exceed the max length allowed in the db)
                4. so on ....
                ------ '''

                status = req_body.get("status")
                employee_environment = req_body.get("employee_environment")
                department = req_body.get("department")
                work_type = req_body.get("work_type")
                manager_id = req_body.get("manager_id")
                work_location = req_body.get("work_location")
                gender = req_body.get("gender")
                birth_date = req_body.get("birth_date")
                start_date = req_body.get("start_date")
                end_date = req_body.get("end_date")

                put_data = user_status_functions.update_user_status(
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
                )

                return func.HttpResponse(put_data)
            else:
                # Return 404 if UUID is not passed in the URL
                return func.HttpResponse(
                    body=json.dumps({"message": f"Update failed! Check body parameters and if {domain_rhonda_id} exists!"}), #HY - Please check the appropriate message
                    status_code=404,
                    charset="utf-8",
                    mimetype="application/json",
                )

        except Exception as error:
            #HY - Highly recommend to use exception to throw error related to Internal Server Error issue.
            # 500 error code should be return in the exception block
            # If error related to missing domain_rhonda_id should be handled in the if/else statement
            logging.error(f"Error:{error}")
            return func.HttpResponse(
                body=json.dumps({"message": f"Update failed! Check body parameters and if {domain_rhonda_id} exists!"}),
                status_code=404,
                charset="utf-8",
                mimetype="application/json",
            )

    # DELETE data
    elif "DELETE" == req.method:
        try:
            domain_rhonda_id = req.route_params.get("domain_rhonda_id", None)

            if domain_rhonda_id:
                delete_data = user_status_functions.delete_user_status(domain_rhonda_id)
                return func.HttpResponse(delete_data, status_code=204)
            else:
                # If no UUID is passed
                return func.HttpResponse(
                    body=json.dumps({"message": f"Update failed! Check body parameters and if {domain_rhonda_id} exists!"}), #HY - Please check the appropriate message
                    status_code=404,
                    charset="utf-8",
                    mimetype="application/json",
                )
        except Exception as error:
            #HY - Highly recommend to use exception to throw error related to Internal Server Error issue.
            # 500 error code should be return in the exception block
            # If error related to missing domain_rhonda_id should be handled in the if/else statement

            logging.error(f"Error:{error}")
            return func.HttpResponse(
                body=json.dumps({"message": f"Delete failed! Check if {domain_rhonda_id} exists!"}),
                status_code=404,
                charset="utf-8",
                mimetype="application/json",
            )

    else:
        # POST data
        try:
            req_body = req.get_json()
            #HY - Need to handle duplication 
            #HY - Return appropriate message if request failed

            ''' -----
            HY
            Need a validation right here
            1. Check if all required fields are passed, else return 400 with error message containing what fields are missing
            2. Check field type
            3. Check field length (Make sure does not exceed the max length allowed in the db)
            4. So on ....
            ------ '''

            domain_rhonda_id = req_body.get("domain_rhonda_id", None) # .get('', None)

            #HY Check if domain_rhonda_id
            if domain_rhonda_id:
                ## Run some function to execute SQL query for checking if resource with the UUID exists
                ## Return 409 if there is a conflict
                pass

            status = req_body.get("status")
            employee_environment = req_body.get("employee_environment")
            department = req_body.get("department")
            work_type = req_body.get("work_type")
            manager_id = req_body.get("manager_id")
            work_location = req_body.get("work_location")
            gender = req_body.get("gender")
            birth_date = req_body.get("birth_date")
            start_date = req_body.get("start_date")
            end_date = req_body.get("end_date")

            post_data = user_status_functions.add_user_status(
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
            )
            return func.HttpResponse(post_data, status_code=201)
        except Exception as error:
            #HY - Error code 500

            logging.error(f"Error:{error}")
            return func.HttpResponse(
                body=json.dumps(
                    {"message": f"POST failed! Check body parameters and if {domain_rhonda_id} already exist!"}
                ),
                status_code=404,
                charset="utf-8",
                mimetype="application/json",
            )
