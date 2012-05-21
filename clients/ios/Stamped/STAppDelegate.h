//
//  STAppDelegate.h
//  Stamped
//
//  Created by Landon Judkins on 4/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@class DDMenuController;
@interface STAppDelegate : UIResponder <UIApplicationDelegate>

@property (strong, nonatomic) UIWindow *window;
@property (strong, nonatomic) DDMenuController *menuController;
@property (nonatomic, retain) UINavigationController* navigationController;
@property (nonatomic, readonly, retain) UIImageView* grid;

@end
