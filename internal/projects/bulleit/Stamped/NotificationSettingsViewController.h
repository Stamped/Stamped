//
//  NotificationSettingsViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/2/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface NotificationSettingsViewController : UIViewController

@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;

- (IBAction)settingsButtomPressed:(id)sender;

@end
