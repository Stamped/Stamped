//
//  ActivityViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/31/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STReloadableTableViewController.h"

@interface ActivityViewController : STReloadableTableViewController <UIScrollViewDelegate,
                                                                     RKObjectLoaderDelegate,
                                                                     NSFetchedResultsControllerDelegate>

@end
