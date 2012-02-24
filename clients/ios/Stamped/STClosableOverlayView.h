//
//  STClosableOverlayView.h
//  Stamped
//
//  Created by Andrew Bonventre on 2/22/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STClosableOverlayView : UIView

- (void)show;
- (void)showWithOnCloseHandler:(void (^)(void))block;

@property (nonatomic, readonly) UIView* contentView;

@end
