//
//  RootTabBarViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>


@interface RootTabBarViewController : UIViewController <UITabBarDelegate> {

}

@property (nonatomic, retain) NSArray* viewControllers;
@property (nonatomic, retain) UIViewController* selectedViewController;
@property (nonatomic, retain) IBOutlet UIButton* addStampButton;
@property (nonatomic, retain) IBOutlet UITabBar* tabBar;
@property (nonatomic, retain) IBOutlet UITabBarItem* stampsTabBarItem;
@property (nonatomic, retain) IBOutlet UITabBarItem* activityTabBarItem;
@property (nonatomic, retain) IBOutlet UITabBarItem* mustDoTabBarItem;
@property (nonatomic, retain) IBOutlet UITabBarItem* peopleTabBarItem;

@end
