//
//  STEndpointResponse.h
//  Stamped
//
//  Created by Landon Judkins on 5/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STAction.h"

@protocol STEndpointResponse <NSObject>

@property (nonatomic, readonly, retain) id<STAction> action;

@end
