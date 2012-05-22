//
//  STSimpleMention.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STMention.h"

@interface STSimpleMention : NSObject <STMention, NSCoding>

@property (nonatomic, readwrite, copy) NSString* screenName;
@property (nonatomic, readwrite, copy) NSString* userID;
@property (nonatomic, readwrite, copy) NSArray* indices;

+ (RKObjectMapping*)mapping;

@end
