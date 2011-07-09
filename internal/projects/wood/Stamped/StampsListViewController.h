//
//  StampsListViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>


@interface StampsListViewController : UITableViewController<UIScrollViewDelegate> {
 @private
  NSMutableArray* stampsArray_;
  BOOL userDidScroll_;
}

- (IBAction)filterButtonPushed:(id)sender;

@property (nonatomic, assign) IBOutlet UIView* filterView;

@end
