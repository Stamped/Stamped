//
//  STLeftMenuViewController.h
//  Stamped
//
//  Created by Landon Judkins on 4/21/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STLeftMenuViewController : UIViewController {
    NSArray *_dataSource;
    NSDictionary *_controllerStore;
}

@property(nonatomic,retain) UITableView *tableView;

@end
