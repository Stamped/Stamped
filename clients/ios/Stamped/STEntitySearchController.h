//
//  STEntitySearchController.h
//  Stamped
//
//  Created by Landon Judkins on 4/17/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STRestViewController.h"

@interface STEntitySearchController : STRestViewController

- (id)initWithCategory:(NSString*)category andQuery:(NSString*)query;

@end
