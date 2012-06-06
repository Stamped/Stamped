//
//  StampColorPickerView.h
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import <UIKit/UIKit.h>

@protocol StampColorPickerDelegate;
@interface StampColorPickerView : UIView {
    NSMutableArray *_views;
}

@property(nonatomic,assign) id <StampColorPickerDelegate> delegate;

- (NSArray*)colors;
- (void)setSelectedColors:(NSArray*)colors;

@end
@protocol StampColorPickerDelegate
- (void)stampColorPickerViewSelectedCustomize:(StampColorPickerView*)view;
- (void)stampColorPickerView:(StampColorPickerView*)view selectedColors:(NSArray*)color;
@end