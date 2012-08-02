//
//  UIImage+Stamped.m
//  Stamped
//
//  Created by Landon Judkins on 7/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "UIImage+Stamped.h"

#define kEncodingKey        @"UIImage"

@implementation UIImage(Stamped)

// TODO fix for iOS 5

- (id)initWithCoder:(NSCoder *)decoder
{
    if ((self = [super init]))
    {
        NSData *data = [decoder decodeObjectForKey:kEncodingKey];
        self = [self initWithData:data];
    }
    
    return self;
}

- (void)encodeWithCoder:(NSCoder *)encoder
{
    NSData *data = UIImagePNGRepresentation(self);
    [encoder encodeObject:data forKey:kEncodingKey];
}

@end