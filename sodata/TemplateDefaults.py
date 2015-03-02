from sodata.forms import ResourceForm

def get_base_default():
    new_resource_form = ResourceForm()
    return {'new_resource_form':new_resource_form, 'resource':None}

base = get_base_default()