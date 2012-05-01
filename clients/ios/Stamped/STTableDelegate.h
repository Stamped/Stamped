//
//  STTableDelegate.h
//  Stamped
//
//  Created by Landon Judkins on 4/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@protocol STTableDelegate <UITableViewDelegate, UITableViewDataSource>

- (void)reloadStampedData;

@optional
@property (nonatomic, readwrite, copy) void (^tableShouldReloadCallback)(id<STTableDelegate> tableDelegate);

@end
