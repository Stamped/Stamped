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
@property (nonatomic, retain) IBOutlet UISwitch* creditPushSwitch;
@property (nonatomic, retain) IBOutlet UISwitch* likePushSwitch;
@property (nonatomic, retain) IBOutlet UISwitch* favoritePushSwitch;
@property (nonatomic, retain) IBOutlet UISwitch* mentionPushSwitch;
@property (nonatomic, retain) IBOutlet UISwitch* commentPushSwitch;
@property (nonatomic, retain) IBOutlet UISwitch* replyPushSwitch;
@property (nonatomic, retain) IBOutlet UISwitch* followPushSwitch;


- (IBAction)settingsButtomPressed:(id)sender;
- (IBAction)syncPrefsFromInterface:(id)sender;

@end
