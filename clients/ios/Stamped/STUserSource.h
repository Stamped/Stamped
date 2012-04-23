//
//  STUserSource.h
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampsViewSource.h"
#import "STUser.h"

@interface STUserSource : STStampsViewSource

@property (nonatomic, readwrite, retain) id<STUser> user;

@end
