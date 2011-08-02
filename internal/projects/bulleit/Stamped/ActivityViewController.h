//
//  ActivityViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/31/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

@interface ActivityViewController : UITableViewController <UIScrollViewDelegate, RKObjectLoaderDelegate> {
 @private
  BOOL shouldReload_;
  BOOL isLoading_;
}

@property (nonatomic, retain) IBOutlet UILabel* reloadLabel;

@end
