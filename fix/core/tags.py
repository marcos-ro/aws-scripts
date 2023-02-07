from fuzzywuzzy import fuzz

import boto3
import functools
import re
import logging

class Fix:
    def __init__(self, profile_name):
        self.__profile_name = profile_name

    def __configure_client(self):
        session = boto3.session.Session(profile_name=self.__profile_name)
        return session

    def __parse_to_user_names(self, response):
        users = [user['UserName'] for user in response['Users']]
        return users

    def __fetch_user_tags(self, client, user_name):
        response = client.list_user_tags(UserName=user_name)
        return {"user_name": user_name, "tags": response['Tags']}

    def __list_only_user_tags(self):
        client = self.__configure_client().client('iam')
        fetch_user_tags = functools.partial(self.__fetch_user_tags, client)
        user_names = self.__parse_to_user_names(client.list_users())
        return map(fetch_user_tags, user_names)

    def __is_email(self, string):
        match = re.search('^.+@.+(\..+)+$', string)
        return match != None

    def __fix_email(self, value):
        option = Option.none()
        if(self.__is_email(value.strip())):
            option = Option.some({"Key": "Email", "Value": value.strip()})

        return option

    def __fix_area(self, value):
        option = Option.some({"Key": "Area", "Value": value.strip()})
        return option

    def __fix_dept(self, value):
        option = Option.some({"Key": "Dept", "Value": value.strip()})
        return option

    def __fix_name(self, value):
        option = Option.some({"Key": "Name", "Value": value.strip()})
        return option

    def fix(self):
        client = self.__configure_client().client("iam")

        for user_tag in self.__list_only_user_tags():
            tags = list()
            for tag in user_tag['tags']:
                key = tag['Key']
                value = tag['Value']
                option = Option.none()

                if(fuzz.token_set_ratio(key, "Email") > 50 or fuzz.token_set_ratio(key, "Correo") > 50):
                    option = self.__fix_email(value)
                elif(fuzz.token_set_ratio(key, "Area") > 50):
                    option = self.__fix_area(value)
                elif(fuzz.token_set_ratio(key, "Dept") > 50):
                    option = self.__fix_dept(value)
                elif(fuzz.token_set_ratio(key, "Name") > 50):
                    option = self.__fix_name(value)

                if(not option.is_none() and option.get_value() not in tags):
                    tags.append(option.get_value())

            user_name = user_tag['user_name']
            logging.info(f"[usuario {user_name}] Cambiando las viejas tags: {user_tag['tags']} por: {tags}")

            try:
                untag = [item['Key'] for item in user_tag['tags']]
                client.untag_user(UserName=user_name, TagKeys=untag)
            except Exception as error:
                logging.error(f"Ocurrio un error al untagear al usuario {user_name}, detalle: {error}")
                break

            try:
                client.tag_user(UserName=user_name, Tags=tags)
            except Exception as error:
                logging.error(f"Ocurrio un error al tagear al usuario {user_name}, detalle: {error}")
                break

