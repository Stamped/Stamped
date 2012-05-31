//
//  StampColorPickerSliderView.h
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import <UIKit/UIKit.h>


@protocol StampColorPickerSliderDelegate;
@class StampColorPickerColorView;
@interface StampColorPickerSliderView : UIView {
   
    UISlider *_hueSlider;
    UISlider *_brightnessSlider;
    UIImageView *_arrowView;

    StampColorPickerColorView *_firstColorView;
    StampColorPickerColorView *_secondColorView;
    
}

@property(nonatomic,assign) id <StampColorPickerSliderDelegate> delegate;
@property(nonatomic,assign) NSArray *colors;

@end
@protocol StampColorPickerSliderDelegate
- (void)stampColorPickerSliderView:(StampColorPickerSliderView*)view pickedColors:(NSArray*)colors;
@end
