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
    NSArray *_anchorDataSource;
    
    NSDictionary *_controllerStore;
    NSDictionary *_anchorControllerStore;
    
    NSInteger _unreadCount;
    NSIndexPath *_selectedIndexPath;
}

+ (void)setupConfigurations;

@property(nonatomic,retain) UITableView *tableView;
@property(nonatomic,retain) UITableView *anchorTableView;

@end
