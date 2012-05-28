//
//  STSimpleEntityAutoCompleteResult.h
//  Stamped
//
//  Created by Landon Judkins on 5/25/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STEntityAutoCompleteResult.h"

@interface STSimpleEntityAutoCompleteResult : NSObject <STEntityAutoCompleteResult, NSCoding>

@property (nonatomic, readwrite, copy) NSString* completion;

+ (RKObjectMapping*)mapping;

@end
