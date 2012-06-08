//
//  STEntityAnnotation.m
//  Stamped
//
//  Created by Landon Judkins on 6/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STEntityAnnotation.h"

@implementation STEntityAnnotation

@synthesize entityDetail = _entityDetail;
@synthesize coordinate = _coordinate;

- (id)initWithEntityDetail:(id<STEntityDetail>)entityDetail {
    self = [super init];
    if (self) {
        _entityDetail = [entityDetail retain];
        NSArray* coordinates = [self.entityDetail.coordinates componentsSeparatedByString:@","];
        CGFloat latitude = [(NSString*)[coordinates objectAtIndex:0] floatValue];
        CGFloat longitude = [(NSString*)[coordinates objectAtIndex:1] floatValue];
        _coordinate = CLLocationCoordinate2DMake(latitude, longitude);
    }
    return self;
}

- (id)initWithCoder:(NSCoder *)aDecoder {
    id<STEntityDetail> detail = [aDecoder decodeObjectForKey:@"entityDetail"];
    return [self initWithEntityDetail:detail];
}

- (void)dealloc
{
    [_entityDetail release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.entityDetail forKey:@"entityDetail"];
}

- (NSString *)title {
    return self.entityDetail.title;
}

- (NSString *)subtitle {
    if (self.entityDetail) {
        return self.entityDetail.subtitle;
    }
    return nil;
}


@end
