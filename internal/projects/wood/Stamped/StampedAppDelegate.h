//
//  StampedAppDelegate.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class CustomUITabBarController;

@interface StampedAppDelegate : NSObject <UIApplicationDelegate,
                                          UITabBarControllerDelegate> {

}

@property (nonatomic, retain) IBOutlet UIWindow* window;
@property (nonatomic, retain) IBOutlet CustomUITabBarController* tabBarController;

@end
