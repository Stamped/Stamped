//
//  StampCustomizeViewController.h
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import <UIKit/UIKit.h>

@class StampColorPickerSliderView;
@protocol StampCustomizeViewControllerDelegate;
@interface StampCustomizeViewController : UIViewController {
    StampColorPickerSliderView *_sliderView;
    UIView *_stampView;
}

- (id)initWithColors:(NSArray*)colors;

@property(nonatomic,assign) id <StampCustomizeViewControllerDelegate> delegate;
@end
@protocol StampCustomizeViewControllerDelegate
- (void)stampCustomizeViewControllerCancelled:(StampCustomizeViewController*)controller;
- (void)stampCustomizeViewController:(StampCustomizeViewController*)controller doneWithColors:(NSArray*)colors;
@end