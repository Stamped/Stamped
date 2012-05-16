//
//  STCreateStampViewController.h
//  Stamped
//
//  Created by Landon Judkins on 4/19/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STContainerViewController.h"

@interface STCreateStampViewController : STContainerViewController

- (id)initWithEntity:(id<STEntity>)entity;

+ (void)setupConfigurations;

@end
