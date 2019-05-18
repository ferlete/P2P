
class Info(object):

    def __init__(self, author, email, appname):
        self.author = author
        self.email = email
        self.appname = appname

    def get_authors(self):
        """
             get suthors

            this function returns the name of authors

            Parameters
            ----------
                nothing

            Returns
            -------
            str
                authors names

        """

        return self.author

    def get_app_name(self):
        """
             get app name

            this function returns the name of the application

            Parameters
            ----------
                nothing

            Returns
            -------
            str
                application name

        """
        return self.appname + " "
