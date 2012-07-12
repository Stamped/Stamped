//
//  STComment.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STUser.h"
#import "STActivityReference.h"

@protocol STComment <NSObject>

@property (nonatomic, readonly, copy) NSString* blurb;
@property (nonatomic, readonly, copy) NSArray<STActivityReference>* blurbReferences;
@property (nonatomic, readonly, copy) NSString* commentID;
@property (nonatomic, readonly, copy) NSString* stampID;
@property (nonatomic, readonly, copy) NSDate* created;
@property (nonatomic, readonly, retain) id<STUser> user;

@end
