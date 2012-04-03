//
//  STComment.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STComment <NSObject>

@property (nonatomic, retain) NSString* blurb;
@property (nonatomic, retain) NSString* commentID;
@property (nonatomic, retain) NSString* stampID;
@property (nonatomic, retain) NSDate* created;
@property (nonatomic, retain) NSString* userID;

@end
