//
//  STAccountParameters.m
//  Stamped
//
//  Created by Landon Judkins on 6/6/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STAccountParameters.h"

@implementation STAccountParameters

@synthesize screenName = _screenName;
@synthesize name = _name;
@synthesize email = _email;
@synthesize phone = _phone;
@synthesize tempImageURL = _tempImageURL;
@synthesize bio = _bio;
@synthesize website = _website;
@synthesize location = _location;
@synthesize colorPrimary = _colorPrimary;
@synthesize colorSecondary = _colorSecondary;

- (void)dealloc
{
    [_screenName release];
    [_name release];
    [_email release];
    [_phone release];
    [_tempImageURL release];
    [_bio release];
    [_website release];
    [_location release];
    [_location release];
    [_colorPrimary release];
    [_colorSecondary release];
    [super dealloc];
}

- (NSMutableDictionary *)asDictionaryParams {
    NSMutableDictionary* params = [NSMutableDictionary dictionary];
    NSDictionary* mapping = [NSDictionary dictionaryWithObjectsAndKeys:
                             @"screenName", @"screenName",
                             @"name", @"name",
                             @"email", @"email",
                             @"phone", @"phone",
                             @"temp_image_url", @"tempImageURL",
                             @"bio", @"bio",
                             @"website", @"website",
                             @"location", @"location",
                             @"color_primary", @"colorPrimary",
                             @"color_secondary", @"colorSecondary",
                             nil];
    for (NSString* key in mapping.allKeys) {
        id object = [self valueForKey:key];
        if (object) {
            [params setObject:object forKey:[mapping objectForKey:key]];
        }
    }
    return params;
}

@end
