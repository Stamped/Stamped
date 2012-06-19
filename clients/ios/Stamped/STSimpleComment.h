//
//  STSimpleComment.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STComment.h"

@interface STSimpleComment : NSObject <STComment, NSCoding>

@property (nonatomic, readwrite, copy) NSString* blurb;
@property (nonatomic, readwrite, copy) NSString* commentID;
@property (nonatomic, readwrite, copy) NSString* stampID;
@property (nonatomic, readwrite, copy) NSDate* created;
@property (nonatomic, readwrite, retain) id<STUser> user;

+ (RKObjectMapping*)mapping;

+ (STSimpleComment*)commentWithBlurb:(NSString*)blurb user:(id<STUser>)user andStampID:(NSString*)stampID;

@end
