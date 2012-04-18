//
//  STActivityRange.h
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STAction.h"

@protocol STActivityRange <NSObject>

@property (nonatomic, readonly, copy) NSArray* indices;
@property (nonatomic, readonly, copy) id<STAction> action;
@property (nonatomic, readonly, copy) NSDictionary* format;

@end
