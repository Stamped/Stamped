//
//  STStampSwitch.h
//  Stamped
//
//  Created by Devin Doty on 6/13/12.
//
//

#import <UIKit/UIKit.h>

@interface STStampSwitch : UIControl {
    UIImageView *_handle;
    UIImageView *_handleIcon;
    CGFloat _panDiff;
}
@property(nonatomic,assign,getter = isOn) BOOL on;

- (void)setOn:(BOOL)on animated:(BOOL)animated;

@end
