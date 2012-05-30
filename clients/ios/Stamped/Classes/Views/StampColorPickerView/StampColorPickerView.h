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

@end
@protocol StampColorPickerDelegate

@end