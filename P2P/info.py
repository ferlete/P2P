
class Info(object):

    def __init__(self, author, email, appname):
        self.author = author
        self.email = email
        self.appname = appname

    def get_authors(self):
        return self.author

    def get_app_name(self):
        return self.appname + " "
