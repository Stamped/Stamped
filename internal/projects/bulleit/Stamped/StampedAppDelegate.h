//
//  StampedAppDelegate.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

@interface StampedAppDelegate : NSObject <UIApplicationDelegate, RKRequestDelegate>

@property (nonatomic, retain) IBOutlet UIWindow* window;
@property (nonatomic, retain) IBOutlet UINavigationController* navigationController;

@end
