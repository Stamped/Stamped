//
//  STReloadableTableViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/7/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STReloadableTableViewController : UITableViewController <UIScrollViewDelegate> {
 @protected
  BOOL shouldReload_;
  BOOL isLoading_;
  CGPoint scrollPosition_;
  CGFloat previousOffset_;
  UILabel* reloadLabel_;
  UIImageView* arrowImageView_;
  UIActivityIndicatorView* spinnerView_;
}

- (void)userPulledToReload;
- (void)setIsLoading:(BOOL)loading;
- (void)reloadData;

@end
