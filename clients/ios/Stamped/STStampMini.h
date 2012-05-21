//
//  STStampMini.h
//  Stamped
//
//  Created by Landon Judkins on 5/21/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STStampMini <NSObject>

@property (nonatomic, readonly, copy) NSString* stampID;
@property (nonatomic, readonly, copy) NSDate* created;
@property (nonatomic, readonly, copy) NSDate* stamped;
@property (nonatomic, readonly, copy) NSDate* modified;
@property (nonatomic, readonly, copy) NSDate* updated;

@end
