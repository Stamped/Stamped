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

@interface STNavigationBar : UINavigationBar {
 @private
  CALayer* mapLayer_;
  BOOL listButtonShown_;
  BOOL potentialButtonTap_;
  BOOL buttonShown_;
}

- (void)setButtonShown:(BOOL)shown;

@property (nonatomic, assign) BOOL hideLogo;
@end
