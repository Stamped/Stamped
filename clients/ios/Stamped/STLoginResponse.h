//
//  STLoginResponse.h
//  Stamped
//
//  Created by Landon Judkins on 5/22/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STUserDetail.h"

@protocol STLoginResponse <NSObject>

@property (nonatomic, readonly, retain) id<STUserDetail> user;
@property (nonatomic, readonly, copy) NSString* token;

@end
