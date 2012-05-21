//
//  STSliderScopeView.h
//  Stamped
//
//  Created by Devin Doty on 5/15/12.
//
//

#import <UIKit/UIKit.h>
#import "STStampedAPI.h"

@protocol STSliderScopeViewDelegate;
@class STTextPopoverView;

@interface STSliderScopeView : UIView {
    STTextPopoverView *_textPopover;
    BOOL _dragging;
    NSTimeInterval _dragBeginTime;
    UIImageView *_draggingView;
    CGPoint _beginPress;
    BOOL _firstPan;
    BOOL _firstPress;
    UIImageView *_userImageView;
    STStampedAPIScope _prevScope;
}

@property (nonatomic,assign) STStampedAPIScope scope; // default STStampedAPIScopeYou
@property (nonatomic,readonly) UILongPressGestureRecognizer *longPress;
@property (nonatomic,assign) id <STSliderScopeViewDelegate> delegate;

- (void)setScope:(STStampedAPIScope)scope animated:(BOOL)animated;

@end

@protocol STSliderScopeViewDelegate
- (void)sliderScopeView:(STSliderScopeView*)slider didChangeScope:(STStampedAPIScope)scope;
@end
