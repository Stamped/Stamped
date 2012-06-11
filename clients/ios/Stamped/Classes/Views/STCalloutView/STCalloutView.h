//
//  STCalloutView.h
//  Stamped
//
//  Created by Devin Doty on 6/6/12.
//
//

#import <UIKit/UIKit.h>

@interface STCalloutView : UIView {
    UIImageView *_left;
    UIImageView *_right;
    UIImageView *_mid;
}

- (void)showFromPosition:(CGPoint)position animated:(BOOL)animated;
- (void)hide:(BOOL)animated;

@end
