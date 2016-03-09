#! /usr/bin/env python

import logging
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5  # Python < 2.5
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, ThrottledDTPHandler
from pyftpdlib.servers import FTPServer

password = 'ChangeMe'


class DummyMD5Authorizer(DummyAuthorizer):

    def validate_authentication(self, username, password, handler):
        return self.user_table[username]['pwd'] == md5(password).hexdigest()


def main(port, users, anonymous_home):
    # Instantiate a dummy authorizer for managing 'virtual' users
    # authorizer = DummyAuthorizer()
    # authorizer.add_user('user', '12345', '.', perm='elradfmwM')

    authorizer = DummyMD5Authorizer()
    # Define a new user having full r/w permissions
    for user_name, user_pass, user_home, user_perm in users:
        authorizer.add_user(
            user_name, md5(user_pass).hexdigest(),
            user_home,
            perm=user_perm
        )

    # add a read-onlyanonymous user
    if anonymous_home:
        authorizer.add_anonymous(anonymous_home)

    # Instantiate FTP handler class
    handler = FTPHandler
    handler.authorizer = authorizer
    logging.basicConfig(filename='/var/log/pyftpd.log', level=logging.INFO)
    logging.basicConfig(level=logging.DEBUG)
    handler.log_prefix = '[%(username)s]@%(remote_ip)s'
    dtp_handler = ThrottledDTPHandler
    dtp_handler.read_limit = 30720  # 30 Kb/sec (30 * 1024)
    dtp_handler.write_limit = 30720  # 30 Kb/sec (30 * 1024)
    handler.dtp_handler = dtp_handler

    # Define a customized banner (string returned when client connects)
    handler.banner = "pftpd ready."

    # Specify a masquerade address and the range of ports to use for
    # passive connections.  Decomment in case you're behind a NAT.
    # handler.masquerade_address = '151.25.42.11'
    handler.passive_ports = range(9000, 9009)

    # Instantiate FTP server class and listen on 0.0.0.0:2121
    address = ('', port)
    server = FTPServer(address, handler)

    # set a limit for connections
    server.max_cons = 256
    server.max_cons_per_ip = 5

    # start ftp server
    server.serve_forever()

if __name__ == '__main__':
    port = 21
    users = (
        ('admin', password, '/var/www/htdocs', 'elradfmw'),
    )
    main(port, users, None)
