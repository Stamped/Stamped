//
//  StampColorPickerSliderView.h
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import <UIKit/UIKit.h>

@protocol StampColorPickerSliderView;
@interface StampColorPickerSliderView : UIView {
    UISlider *_hueSlider;
    UISlider *_brightnessSlider;
}

@property(nonatomic,assign) id <StampColorPickerSliderView> delegate;
@property(nonatomic,retain) UIColor *color1;
@property(nonatomic,retain) UIColor *color2;

- (NSArray*)colors;

@end
@protocol StampColorPickerSliderView
- (void)stampColorPickerSliderView:(StampColorPickerSliderView*)view pickedColors:(NSArray*)colors;
@end
