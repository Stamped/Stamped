//
//  STProfileSource.h
//  Stamped
//
//  Created by Landon Judkins on 4/23/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STUserSource.h"
#import "STUserDetail.h"

@interface STProfileSource : STUserSource

- (id)initWithUserDetail:(id<STUserDetail>)userDetail;

@end
