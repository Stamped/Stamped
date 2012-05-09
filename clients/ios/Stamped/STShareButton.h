//
//  STShareButton.h
//  Stamped
//
//  Created by Landon Judkins on 5/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STToolbarButton.h"

@interface STShareButton : STToolbarButton

- (id)initWithCallback:(void (^)(void))block;

@property (nonatomic, readwrite, copy) void (^block)(void);

@end
