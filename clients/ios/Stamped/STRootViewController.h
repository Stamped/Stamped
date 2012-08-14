//
//  STRootViewController.h
//  Stamped
//
//  Created by Landon Judkins on 4/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

/*
 Our custom navigation controller used across the project
 
 This class has a few purposes but mostly it uses our custom STNavigationBar.
 Aside from that, it also provides iOS 4.3 support for some view life cycle callbacks
 that are supported by default on iOS 5. It also, supports a hidden design grid overlay feature.
 
 TODOs:
 Disable design feature for normal users (whitelist or Dev only)
 
 2012-08-10
 -Landon
 */

#import <UIKit/UIKit.h>

@interface STRootViewController : UINavigationController

@end
