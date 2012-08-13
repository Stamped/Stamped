//
//  STLeftMenuViewController.h
//  Stamped
//
//  Created by Landon Judkins on 4/21/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

/*
 The left hand root menu for accessing The Feed, The Guide, Activity, etc.
 
 Notes:
 This class is extremely hacky. It was originally written by me (Landon), then
 re-written in place by Devin, then re-configured in place by me to accomodate the
 new design changes. The two cells classes involved are copy-and-paste forked copies (sigh...).
 Both contain unnecessary complexity for the current design spec, including an image based
 highlight state that extends beyond the cell. 
 
 Also, the selection state mechanism is very fragile and somewhat broken. There were some 11th hour
 changes to it for v2 launch. Ideally, this class should include support for context jumps to any
 of the root views so that selection state is consistent (i.e. opened from APNS).
 
 I strongly recommend a complete re-write.
 
 2012-08-10
 -Landon
 */

#import <UIKit/UIKit.h>

@interface STLeftMenuViewController : UIViewController

- (void)reloadDataSource;

+ (void)setupConfigurations;

- (void)clearSelection;

@end
