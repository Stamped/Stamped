//
//  STAppDelegate.h
//  Stamped
//
//  Created by Landon Judkins on 4/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

/*
 NEEDSDOC
 */

#import <Foundation/Foundation.h>

@class DDMenuController, STMenuController;
@interface STAppDelegate : UIResponder <UIApplicationDelegate>

@property (strong, nonatomic) UIWindow *window;
@property (strong, nonatomic) STMenuController *menuController;
@property (nonatomic, readonly, retain) UIImageView* grid;

@end
