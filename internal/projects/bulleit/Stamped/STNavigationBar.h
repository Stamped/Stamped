//
//  STNavigationBar.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

extern NSString* const kMapViewButtonPressedNotification;
extern NSString* const kListViewButtonPressedNotification;
extern NSString* const kSettingsButtonPressedNotification;

@interface STNavigationBar : UINavigationBar {
 @private
  CALayer* mapLayer_;
  CALayer* ripplesLayer_;
  BOOL listButtonShown_;
  BOOL potentialButtonTap_;
  BOOL buttonShown_;
  BOOL settingsButtonShown_;
  NSString* string;
}

- (void)setListButtonShown:(BOOL)shown;
- (void)setButtonShown:(BOOL)shown;
- (void)setSettingsButtonShown:(BOOL)shown;

@property (nonatomic, assign) BOOL black;
@property (nonatomic, assign) BOOL hideLogo;
@property (nonatomic, retain) NSString* string;
@end
