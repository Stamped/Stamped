//
//  STNavigationBar.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

extern NSString* const kSettingsButtonPressedNotification;

@interface STNavigationBar : UINavigationBar {
 @private
  CALayer* ripplesLayer_;
  BOOL potentialButtonTap_;
  BOOL settingsButtonShown_;
  NSString* string;
}

- (void)setSettingsButtonShown:(BOOL)shown;

@property (nonatomic, assign) BOOL black;
@property (nonatomic, assign) BOOL hideLogo;
@property (nonatomic, retain) NSString* string;
@end
