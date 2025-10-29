from MiniProject.wsgi import application

def handler(request, context):
    return application(request)
