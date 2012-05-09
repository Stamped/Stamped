//
//  STMusicViewController.h
//  Stamped
//
//  Created by Landon Judkins on 4/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STTableViewController.h"

@interface STConsumptionViewController : STTableViewController

- (id)initWithCategory:(NSString*)category;

+ (void)setupConfigurations;

@end
