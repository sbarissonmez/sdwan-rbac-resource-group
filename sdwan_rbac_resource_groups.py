#!/usr/bin/env python3

import requests
import sys
import json
import os
import click
import tabulate
import time
import yaml

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings()


vmanage_host = os.environ.get("vmanage_host")
vmanage_port = os.environ.get("vmanage_port")
vmanage_username = os.environ.get("vmanage_username")
vmanage_password = os.environ.get("vmanage_password")

if vmanage_host is None or vmanage_port is None or \
   vmanage_username is None or vmanage_password is None:
    click.echo("\n  vManage details must be set using environment variables.")
    click.echo("    For Windows:")
    click.echo("      Exmaple:")
    click.echo("        set vmanage_host=198.18.1.10")
    click.echo("        set vmanage_port=8443")
    click.echo("        set vmanage_username=admin")
    click.echo("        set vmanage_password=admin")
    click.echo("    For MAC/Unix/Linux:")
    click.echo("      Example:")
    click.echo("        export vmanage_host=sdwan.cisco.com")
    click.echo("        export vmanage_port=8443")
    click.echo("        export vmanage_username=admin")
    click.echo("        export vmanage_password=admin")
    click.echo("")
    exit()




class Authentication:

    @staticmethod
    def get_jsessionid(vmanage_host, vmanage_port, vmanage_username, vmanage_password):
        api = "/j_security_check"
        base_url = "https://%s:%s"%(vmanage_host, vmanage_port)
        url = base_url + api
        payload = {'j_username' : vmanage_username, 'j_password' : vmanage_password}
        
        response = requests.post(url=url, data=payload, verify=False)
        try:
            cookies = response.headers["Set-Cookie"]
            jsessionid = cookies.split(";")
            return(jsessionid[0])
        except:
            print("No valid JSESSION ID returned\n")
            exit()
       
    @staticmethod
    def get_token(vmanage_host, vmanage_port, jsessionid):
        headers = {'Cookie': jsessionid}
        base_url = "https://%s:%s"%(vmanage_host, vmanage_port)
        api = "/dataservice/client/token"
        url = base_url + api      
        response = requests.get(url=url, headers=headers, verify=False)
        if response.status_code == 200:
            return(response.text)
        else:
            return None


@click.group()
def cli():
    """Command line tool for monitoring Cisco SD-WAN solution components.
    """
    pass


@click.command()
def get_device_list():
    """ Get network devices list for global admin.
        \n Example command: ./filename.py get-device-list
    """
    click.echo("\nRetrieving the devices for global admin.\n")

    # Login
    Auth = Authentication()
    jsessionid = Auth.get_jsessionid(vmanage_host,vmanage_port,vmanage_username,vmanage_password)
    token = Auth.get_token(vmanage_host,vmanage_port,jsessionid)
    if token is not None:
        header = {'Content-Type': "application/json",'Cookie': jsessionid, 
                  'X-XSRF-TOKEN': token}
    else:
        header = {'Content-Type': "application/json",'Cookie': jsessionid}
    base_url = "https://%s:%s/dataservice"%(vmanage_host,vmanage_port)


    # Perform function
    url = base_url + "/device"

    click.echo("GET\n" + str(url) + "\n")
    response = requests.get(url=url, headers=header,verify=False)
    if response.status_code == 200:
        items = response.json()['data']
    else:
        click.echo("Failed to get list of devices " + str(response.text))
        exit()

    headers = ["Host-Name", "Device Type", "Device ID", 
               "System IP", "Site ID", "Device Model"]
    table = list()

    for item in items:
        tr = [item.get('host-name'), item.get('device-type'), item.get('uuid'), 
              item.get('system-ip'), item.get('site-id'), item.get('device-model')]
        table.append(tr)
    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))

    # Logout
    click.echo("\n")
    api_url = "/logout?nocache=1234"
    base_url2 = "https://%s:%s"%(vmanage_host, vmanage_port)
    url = base_url2 + api_url
    response = requests.get(url=url, headers=header, verify=False,
                            allow_redirects=False)


@click.command()
def get_user_list():
    """ Get user list for global admin.
        \n Example command: ./filename.py get-user-list
    """
    click.echo("\nRetrieving the user list for global admin.\n")

    # Login
    Auth = Authentication()
    jsessionid = Auth.get_jsessionid(vmanage_host,vmanage_port,vmanage_username,vmanage_password)
    token = Auth.get_token(vmanage_host,vmanage_port,jsessionid)
    if token is not None:
        header = {'Content-Type': "application/json",'Cookie': jsessionid, 
                  'X-XSRF-TOKEN': token}
    else:
        header = {'Content-Type': "application/json",'Cookie': jsessionid}
    base_url = "https://%s:%s/dataservice"%(vmanage_host,vmanage_port)


    # Perform function
    url = base_url + "/admin/user"

    click.echo("GET\n" + str(url) + "\n")
    response = requests.get(url=url, headers=header,verify=False)
    if response.status_code == 200:
        items = response.json()['data']
    else:
        click.echo("Failed to get list of users " + str(response.text))
        exit()

    headers = ["User-Name", "User Group", "Resource Group", "Description"]
    table = list()

    for item in items:
        tr = [item.get('userName'), item.get('group'),
              item.get('resGroupName'), item.get('description')]
        table.append(tr)
    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))

    # Logout
    click.echo("\n")
    api_url = "/logout?nocache=1234"
    base_url2 = "https://%s:%s"%(vmanage_host, vmanage_port)
    url = base_url2 + api_url
    response = requests.get(url=url, headers=header, verify=False,
                            allow_redirects=False)


@click.command()
def get_rg_list():
    """ Get Resource Group list for global admin.
        \n Example command: ./filename.py get-rg-list
    """
    click.echo("\nRetrieving the Resource Group list for global admin.\n")

    # Login
    Auth = Authentication()
    jsessionid = Auth.get_jsessionid(vmanage_host,vmanage_port,vmanage_username,vmanage_password)
    token = Auth.get_token(vmanage_host,vmanage_port,jsessionid)
    if token is not None:
        header = {'Content-Type': "application/json",'Cookie': jsessionid, 
                  'X-XSRF-TOKEN': token}
    else:
        header = {'Content-Type': "application/json",'Cookie': jsessionid}
    base_url = "https://%s:%s/dataservice"%(vmanage_host,vmanage_port)


    # Perform function
    url = base_url + "/admin/resourcegroup"

    click.echo("GET\n" + str(url) + "\n")
    response = requests.get(url=url, headers=header,verify=False)
    if response.status_code == 200:
        items = response.json()
    else:
        click.echo("Failed to get list of Resource Groups " + str(response.text))
        exit()

    headers = ["ID", "Resource Group", "Site IDs", "Description"]
    table = list()

    for item in items:
        tr = [item.get('id'), item.get('name'), 
              item.get('siteIds'), (item.get('desc'))[:32]]
        table.append(tr)
    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))

    # Logout
    click.echo("\n")
    api_url = "/logout?nocache=1234"
    base_url2 = "https://%s:%s"%(vmanage_host, vmanage_port)
    url = base_url2 + api_url
    response = requests.get(url=url, headers=header, verify=False,
                            allow_redirects=False)


@click.command()
@click.option("--rg_name", help="Resource Group name")
@click.option("--rg_desc", help="Resource Group description")
@click.option("--site_ids", help="Resource Group site IDs")
def create_resource_group(rg_name, rg_desc, site_ids):
    """ Create Resource Group.
        \n Example command: ./filename.py create-resource-group --rg_name "apjc"
                                                                --rg_desc "RG for apjc"
                                                                --site_ids "100, 200" 
    """
    click.echo("\nCreate Resource Group.\n")

    # Login
    Auth = Authentication()
    jsessionid = Auth.get_jsessionid(vmanage_host,vmanage_port,vmanage_username,vmanage_password)
    token = Auth.get_token(vmanage_host,vmanage_port,jsessionid)
    if token is not None:
        header = {'Content-Type': "application/json",'Cookie': jsessionid, 
                  'X-XSRF-TOKEN': token}
    else:
        header = {'Content-Type': "application/json",'Cookie': jsessionid}
    base_url = "https://%s:%s/dataservice"%(vmanage_host,vmanage_port)


    # Perform function
    url = base_url + "/admin/resourcegroup"

    payload = {
                "name": format(rg_name),
                "desc": format(rg_desc),
                "siteIds": [format(site_ids)]
              }
 
    click.echo("POST\n" + str(url) + "\n")
    click.echo("Payload\n" + str(payload) + "\n")
    response = requests.post(url=url, headers=header, 
                             data=json.dumps(payload), verify=False)

    if response.status_code == 200:
        click.echo("\nSuccessfully created resource group (" + 
              str(response.status_code) + ")\n")
    else:
        click.echo("Failed to create Resource Group " + str(response.text))
        exit()

    # Logout
    click.echo("\n")
    api_url = "/logout?nocache=1234"
    base_url2 = "https://%s:%s"%(vmanage_host, vmanage_port)
    url = base_url2 + api_url
    response = requests.get(url=url, headers=header, verify=False,
                            allow_redirects=False)


@click.command()
@click.option("--rg_id", help="Resource Group ID")
def delete_resource_group(rg_id):
    """ Delete Resource Group.
        \n Example command: ./filename.py delete-resource-group --rg_id "0:RESOURCE_GROUPNode:1615229358903:2"
    """
    click.echo("\nDelete Resource Group.\n")

    # Login
    Auth = Authentication()
    jsessionid = Auth.get_jsessionid(vmanage_host,vmanage_port,vmanage_username,vmanage_password)
    token = Auth.get_token(vmanage_host,vmanage_port,jsessionid)
    if token is not None:
        header = {'Content-Type': "application/json",'Cookie': jsessionid, 
                  'X-XSRF-TOKEN': token}
    else:
        header = {'Content-Type': "application/json",'Cookie': jsessionid}
    base_url = "https://%s:%s/dataservice"%(vmanage_host,vmanage_port)


    # Perform function
    url = base_url + "/admin/resourcegroup/" + format(rg_id)
 
    click.echo("DELETE\n" + str(url) + "\n")
    response = requests.delete(url=url, headers=header, verify=False)

    if response.status_code == 200:
        click.echo("\nSuccessfully deleted resource group (" + 
              str(response.status_code) + ")\n")
    else:
        click.echo("Failed to delete Resource Group " + str(response.text))
        exit()

    # Logout
    click.echo("\n")
    api_url = "/logout?nocache=1234"
    base_url2 = "https://%s:%s"%(vmanage_host, vmanage_port)
    url = base_url2 + api_url
    response = requests.get(url=url, headers=header, verify=False,
                            allow_redirects=False)


@click.command()
@click.option("--u_name", help="User name")
@click.option("--u_pass", help="User password")
@click.option("--u_desc", help="User description")
@click.option("--u_group", help="User Group asscoicated with User")
@click.option("--r_group", help="Resource Group asscoicated with User")
def create_user(u_name, u_pass, u_desc, u_group, r_group):
    """ Create User.
        \n Example command: ./filename.py create-user --u_name  "admin_rg_apjc"
                                                      --u_pass  "admin_rg_apjc"
                                                      --u_desc  "RG admin for apjc"
                                                      --u_group "resource_group_admin"
                                                      --r_group "rg_apjc" 
    """
    click.echo("\nCreate User.\n")

    # Login
    Auth = Authentication()
    jsessionid = Auth.get_jsessionid(vmanage_host,vmanage_port,vmanage_username,vmanage_password)
    token = Auth.get_token(vmanage_host,vmanage_port,jsessionid)
    if token is not None:
        header = {'Content-Type': "application/json",'Cookie': jsessionid, 
                  'X-XSRF-TOKEN': token}
    else:
        header = {'Content-Type': "application/json",'Cookie': jsessionid}
    base_url = "https://%s:%s/dataservice"%(vmanage_host,vmanage_port)


    # Perform function
    url = base_url + "/admin/user"

    payload = {
                "userName": format(u_name),
                "password": format(u_pass),
                "description": format(u_desc),
                "resGroupName": format(r_group),
                "group": [format(u_group)]
              }
 
    click.echo("POST\n" + str(url) + "\n")
    click.echo("Payload\n" + str(payload) + "\n")
    response = requests.post(url=url, headers=header, 
                             data=json.dumps(payload), verify=False)

    if response.status_code == 200:
        click.echo("\nSuccessfully created user (" + 
              str(response.status_code) + ")\n")
    else:
        click.echo("Failed to create Resource Group " + str(response.text))
        exit()

    # Logout
    click.echo("\n")
    api_url = "/logout?nocache=1234"
    base_url2 = "https://%s:%s"%(vmanage_host, vmanage_port)
    url = base_url2 + api_url
    response = requests.get(url=url, headers=header, verify=False,
                            allow_redirects=False)


@click.command()
@click.option("--u_name", help="User name")
def delete_user(u_name):
    """ Delete User.
        \n Example command: ./filename.py delete-user --u_name  "admin_rg_apjc"
    """
    click.echo("\nDelete User.\n")

    # Login
    Auth = Authentication()
    jsessionid = Auth.get_jsessionid(vmanage_host,vmanage_port,vmanage_username,vmanage_password)
    token = Auth.get_token(vmanage_host,vmanage_port,jsessionid)
    if token is not None:
        header = {'Content-Type': "application/json",'Cookie': jsessionid, 
                  'X-XSRF-TOKEN': token}
    else:
        header = {'Content-Type': "application/json",'Cookie': jsessionid}
    base_url = "https://%s:%s/dataservice"%(vmanage_host,vmanage_port)


    # Perform function
    url = base_url + "/admin/user/" + format(u_name)

    click.echo("DELETE\n" + str(url) + "\n")
    response = requests.delete(url=url, headers=header, verify=False)

    if response.status_code == 200:
        click.echo("\nSuccessfully deleted user (" + 
              str(response.status_code) + ")\n")
    else:
        click.echo("Failed to delete Resource Group " + str(response.text))
        exit()

    # Logout
    click.echo("\n")
    api_url = "/logout?nocache=1234"
    base_url2 = "https://%s:%s"%(vmanage_host, vmanage_port)
    url = base_url2 + api_url
    response = requests.get(url=url, headers=header, verify=False,
                            allow_redirects=False)


@click.command()
@click.option("--username", help="Resource Group admin user name")
@click.option("--password", help="Resource Group admin password")
def device_list_user(username, password):
    """ Get network devices list for RG admin.
        \n Example command: ./filename.py device-list-user --username user_rg_apjc
                                                           --password 12345678
    """
    click.echo("\nRetrieving the devices for specified user.\n")

    # Login
    Auth = Authentication()
    jsessionid = Auth.get_jsessionid(vmanage_host,vmanage_port,
                                     format(username),format(password))
    token = Auth.get_token(vmanage_host,vmanage_port,jsessionid)
    if token is not None:
        header = {'Content-Type': "application/json",'Cookie': jsessionid, 
                  'X-XSRF-TOKEN': token}
    else:
        header = {'Content-Type': "application/json",'Cookie': jsessionid}
    base_url = "https://%s:%s/dataservice"%(vmanage_host,vmanage_port)


    # Perform function
    url = base_url + "/device"

    click.echo("GET\n" + str(url) + "\n")
    response = requests.get(url=url, headers=header,verify=False)
    if response.status_code == 200:
        items = response.json()['data']
    else:
        click.echo("Failed to get list of devices " + str(response.text))
        exit()

    headers = ["Host-Name", "Device Type", "Device ID", 
               "System IP", "Site ID", "Device Model"]
    table = list()

    for item in items:
        tr = [item.get('host-name'), item.get('device-type'), item.get('uuid'), 
              item.get('system-ip'), item.get('site-id'), item.get('device-model')]
        table.append(tr)
    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))

    # Logout
    click.echo("\n")
    api_url = "/logout?nocache=1234"
    base_url2 = "https://%s:%s"%(vmanage_host, vmanage_port)
    url = base_url2 + api_url
    response = requests.get(url=url, headers=header, verify=False,
                            allow_redirects=False)





@click.command()
@click.option("--username", help="user name")
@click.option("--password", help="user password")
def get_nd_ft_user(username, password):
    """ Get non-default feature templates list for user.
        \n Example command: ./filename.py get-nd-ft-user --username user_rg_apjc
                                                         --password 12345678
    """
    click.echo("\nRetrieving the non-default feature templates for specified user.\n")

    # Login
    Auth = Authentication()
    jsessionid = Auth.get_jsessionid(vmanage_host,vmanage_port,
                                     format(username),format(password))
    token = Auth.get_token(vmanage_host,vmanage_port,jsessionid)
    if token is not None:
        header = {'Content-Type': "application/json",'Cookie': jsessionid, 
                  'X-XSRF-TOKEN': token}
    else:
        header = {'Content-Type': "application/json",'Cookie': jsessionid}
    base_url = "https://%s:%s/dataservice"%(vmanage_host,vmanage_port)


    # Perform function
    url = base_url + "/template/feature"

    click.echo("GET\n" + str(url) + "\n")
    response = requests.get(url=url, headers=header,verify=False)
    if response.status_code == 200:
        items = response.json()['data']
    else:
        click.echo("Failed to get list of feature templates" + str(response.text))
        exit()

    headers = ["templateName", "templateId", "devicesAttached",
               "resourceGroup", "createdBy", "lastUpdatedBy"]
    table = list()

    for item in items:
        if item.get('createdBy') != "system":
            tr = [item.get('templateName'), item.get('templateId'), item.get('devicesAttached'),
                  item.get('resourceGroup'), item.get('createdBy'), item.get('lastUpdateBy')]
            table.append(tr)
    try:
        click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
    except UnicodeEncodeError:
        click.echo(tabulate.tabulate(table, headers, tablefmt="grid"))

    # Logout
    click.echo("\n")
    api_url = "/logout?nocache=1234"
    base_url2 = "https://%s:%s"%(vmanage_host, vmanage_port)
    url = base_url2 + api_url
    response = requests.get(url=url, headers=header, verify=False,
                            allow_redirects=False)



@click.command()
@click.option("--username", help="user name")
@click.option("--password", help="user password")
@click.option("--file", help="YAML file with template data")
def create_banner_ft_user(file, username, password):
    """create banner feature template for user.
        Provide all template parameters and their values as arguments.
        Example command:
          ./vmanage_apis.py create-banner-ft-user --file template.yaml --username user -- password pass
    """
    click.secho("\nCreating banner feature template based on yaml file details\n")

    # Login
    Auth = Authentication()
    jsessionid = Auth.get_jsessionid(vmanage_host,vmanage_port,
                                     format(username),format(password))
    token = Auth.get_token(vmanage_host,vmanage_port,jsessionid)
    if token is not None:
        header = {'Content-Type': "application/json",'Cookie': jsessionid, 
                  'X-XSRF-TOKEN': token}
    else:
        header = {'Content-Type': "application/json",'Cookie': jsessionid}
    base_url = "https://%s:%s/dataservice"%(vmanage_host,vmanage_port)


    # Perform function
    url = base_url + "/template/feature"

    with open(format(file)) as f:
        config = yaml.safe_load(f.read())

    payload = {
    "templateName": config["template_name"],
    "templateMinVersion": "15.0.0",
    "templateDescription": config["template_description"],
    "templateType": "banner",
    "templateDefinition": {
        "login": {
            "vipObjectType": "object",
            "vipType": "constant",
            "vipValue": config["login_banner"],  # using the values defined for login banner in yaml file
            "vipVariableName": "banner_login"
        },
        "motd": {
            "vipObjectType": "object",
            "vipType": "constant",
            "vipValue": config["motd_banner"],  # using the values defined for motd banner in yaml file
            "vipVariableName": "banner_motd"
        }
    },
    "deviceType": [
        config["device_type"]
    ],
    "deviceModels": [
        {
            "name": "vedge-cloud",
            "displayName": "vEdge Cloud",
            "deviceType": "vedge",
            "isCliSupported": True,
            "isCiscoDeviceModel": False
        }
    ],
    "factoryDefault": False
    }

    response = requests.post(url=url, headers=header, 
                             data=json.dumps(payload), verify=False)
    if response.status_code == 200:
        click.echo("\nCreated banner template ID: " + str(response.json()))
    else:
        click.echo("\nFailed to create banner feature template: " + str(response.text))
        exit()

    # Logout
    click.echo("\n")
    api_url = "/logout?nocache=1234"
    base_url2 = "https://%s:%s"%(vmanage_host, vmanage_port)
    url = base_url2 + api_url
    response = requests.get(url=url, headers=header, verify=False,
                            allow_redirects=False)



@click.command()
@click.option("--ft_id", help="Feature template ID")
@click.option("--r_group", help="New Resource Group for the template")
def modify_ft_resource_group(ft_id, r_group):
    """ Modify Feature template resource group.
        \n Example command: ./filename.py modify-ft-resource-group --ft_id "4fa86c32-f4e8-46c2-82a6-63ee8106400f"
                                                                   --r_group "rg_apjc" 
    """
    click.echo("\nChanging Resource Group for specified Feature Template.\n")

    # Login
    Auth = Authentication()
    jsessionid = Auth.get_jsessionid(vmanage_host,vmanage_port,vmanage_username,vmanage_password)
    token = Auth.get_token(vmanage_host,vmanage_port,jsessionid)
    if token is not None:
        header = {'Content-Type': "application/json",'Cookie': jsessionid, 
                  'X-XSRF-TOKEN': token}
    else:
        header = {'Content-Type': "application/json",'Cookie': jsessionid}
    base_url = "https://%s:%s/dataservice"%(vmanage_host,vmanage_port)


    # Perform function
    url = base_url + "/template/feature/resource-group/" + format(r_group) + "/" + format(ft_id)

    click.echo("POST\n" + str(url) + "\n")
    response = requests.post(url=url, headers=header, verify=False)

    if response.status_code == 200:
        click.echo("\nSuccessfully changed Resource Group for template (" + 
              str(response.status_code) + ")\n")
    else:
        click.echo("Failed to change Resource Group " + str(response.text))
        exit()

    # Logout
    click.echo("\n")
    api_url = "/logout?nocache=1234"
    base_url2 = "https://%s:%s"%(vmanage_host, vmanage_port)
    url = base_url2 + api_url
    response = requests.get(url=url, headers=header, verify=False,
                            allow_redirects=False)




cli.add_command(get_device_list)
cli.add_command(get_user_list)
cli.add_command(get_rg_list)
cli.add_command(create_resource_group)
cli.add_command(delete_resource_group)
cli.add_command(create_user)
cli.add_command(delete_user)
cli.add_command(modify_ft_resource_group)

cli.add_command(device_list_user)
cli.add_command(get_nd_ft_user)
cli.add_command(create_banner_ft_user)




if __name__ == '__main__':
    cli()



