//
//  STContentItem.h
//  Stamped
//
//  Created by Landon Judkins on 4/24/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STContentItem <NSObject>

@property (nonatomic, readonly, copy) NSDate* modified;
@property (nonatomic, readonly, copy) NSString* blurb;
@property (nonatomic, readonly, copy) NSDate* created;

@end