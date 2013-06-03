
AWS_ACCESS_KEY_ID = 'AKIAIZXJFA4AWUHES4OA'
AWS_SECRET_KEY    = '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'

if __name__ == '__main__':
    from boto.ec2.elb import ELBConnection
    conn = ELBConnection(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)

