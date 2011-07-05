//
//  StampsListViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>


@interface StampsListViewController : UITableViewController {
  UITableViewCell* stampCell_;
}

@property (nonatomic, assign) IBOutlet UITableViewCell* stampCell;

@end
