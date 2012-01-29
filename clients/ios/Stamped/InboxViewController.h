//
//  InboxViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STTableViewController.h"

@interface InboxViewController : STTableViewController <RKObjectLoaderDelegate,
                                                        NSFetchedResultsControllerDelegate>
@end
