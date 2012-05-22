//
//  STSimpleStampMini.h
//  Stamped
//
//  Created by Landon Judkins on 5/21/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STStamp.h"

@interface STStampMini : NSObject <NSCoding>

- (id)initWithStamp:(id<STStamp>)stamp;

@property (nonatomic, readwrite, copy) NSString* stampID;
@property (nonatomic, readwrite, copy) NSDate* created;
@property (nonatomic, readwrite, copy) NSDate* stamped;
@property (nonatomic, readwrite, copy) NSDate* modified;
@property (nonatomic, readwrite, copy) NSDate* updated;

@end
