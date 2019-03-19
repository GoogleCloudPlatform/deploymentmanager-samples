
def generate_config(context):

    # Using some global values from an external config file.
    # Hardcoded for this example.

    global_prefic = "acc "

    # Manipulate context.properties #

    for folder in context.properties["folders"]:
        folder["displayName"] = global_prefic + folder["displayName"]

    # Passing values forward to CFT template

    return {
        'resources': [{
            'type': "cft-folder.py",
            'name': context.env['name'],
            'properties': context.properties}]
    }
