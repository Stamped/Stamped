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
  CALayer* containerLayer_;
  CALayer* mapLayer_;
  CALayer* whiteLayer_;
  BOOL listButtonShown_;
  BOOL potentialButtonTap_;
  BOOL buttonFlipped_;
}

- (void)setButtonFlipped:(BOOL)flipped animated:(BOOL)animated;

@property (nonatomic, assign) BOOL hideLogo;
@end
