//
//  STComment.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STComment <NSObject>

@property (nonatomic, readonly, copy) NSString* blurb;
@property (nonatomic, readonly, copy) NSString* commentID;
@property (nonatomic, readonly, copy) NSString* stampID;
@property (nonatomic, readonly, copy) NSDate* created;
@property (nonatomic, readonly, copy) NSString* userID;

@end
