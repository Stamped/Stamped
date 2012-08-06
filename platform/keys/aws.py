from __future__ import absolute_import

AWS_ACCESS_KEY_ID = 'AKIAIXLZZZT4DMTKZBDQ'
AWS_SECRET_KEY    = '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'

if __name__ == '__main__':
    from boto.ec2.elb import ELBConnection
    conn = ELBConnection(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)

