//
//  STSliderScopeView.h
//  Stamped
//
//  Created by Devin Doty on 5/15/12.
//
//

#import <UIKit/UIKit.h>
#import "STStampedAPI.h"

typedef enum {
    STSliderScopeStyleTwo = 0,
    STSliderScopeStyleThree,
} STSliderScopeStyle;

@protocol STSliderScopeViewDelegate;
@protocol STSliderScopeViewDataSource;

@class STTextCalloutView;
@interface STSliderScopeView : UIView

- (id)initWithStyle:(STSliderScopeStyle)style frame:(CGRect)frame;

- (void)moveToScope:(STStampedAPIScope)scope animated:(BOOL)animated duration:(CGFloat)duration completion:(void (^)(void))completion;
@property (nonatomic,assign) NSInteger selectedIndex;
@property (nonatomic,assign) STStampedAPIScope scope; // default STStampedAPIScopeYou
@property (nonatomic,assign) id <STSliderScopeViewDelegate> delegate;
@property (nonatomic,assign) id <STSliderScopeViewDataSource> dataSource;

- (void)setScope:(STStampedAPIScope)scope animated:(BOOL)animated;

@end

@protocol STSliderScopeViewDelegate
- (void)sliderScopeView:(STSliderScopeView*)slider didChangeScope:(STStampedAPIScope)scope;
@end

@protocol STSliderScopeViewDataSource
@optional
- (NSString*)sliderScopeView:(STSliderScopeView*)slider titleForScope:(STStampedAPIScope)scope;
- (NSString*)sliderScopeView:(STSliderScopeView*)slider boldTitleForScope:(STStampedAPIScope)scope;
@end
