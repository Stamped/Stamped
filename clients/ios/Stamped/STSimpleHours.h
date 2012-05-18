//
//  STSimpleHours.h
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STHours.h"

@interface STSimpleHours : NSObject <STHours, NSCoding>

@property (nonatomic, readwrite, retain) NSString* open;
@property (nonatomic, readwrite, retain) NSString* close;
@property (nonatomic, readwrite, retain) NSString* desc;

+ (RKObjectMapping*)mapping;

@end
