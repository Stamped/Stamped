//
//  STSimpleBadge.h
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STBadge.h"
#import <RestKit/RestKit.h>

@interface STSimpleBadge : NSObject <STBadge, NSCoding>

@property (nonatomic, readwrite, copy) NSString* genre;
@property (nonatomic, readwrite, copy) NSString* userID;

+ (RKObjectMapping*)mapping;

@end
