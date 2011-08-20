//
//  TodoViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/19/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STReloadableTableViewController.h"

@interface TodoViewController : STReloadableTableViewController <RKObjectLoaderDelegate>

@end
