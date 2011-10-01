//
//  SettingsViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/1/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface SettingsViewController : UIViewController

@property (nonatomic, retain) IBOutlet UINavigationController* navigationController;

- (IBAction)doneButtonPressed:(id)sender;

@end
