//
//  STTextPopoverView.h
//  Stamped
//
//  Created by Devin Doty on 5/15/12.
//
//

#import <UIKit/UIKit.h>

@interface STTextPopoverView : UIView {
    CGFloat _arrowLocation;
}

@property(nonatomic,copy) NSString *title;

- (void)showFromView:(UIView*)view position:(CGPoint)point animated:(BOOL)animated;
- (void)hide;
- (void)hideDelayed:(float)delay;

@end
