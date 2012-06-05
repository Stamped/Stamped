//
//  STStampedBy.h
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STStampedByGroup.h"

@protocol STStampedBy <NSObject>

@property (nonatomic, readonly, retain) id<STStampedByGroup> friends;
@property (nonatomic, readonly, retain) id<STStampedByGroup> everyone;

@end
