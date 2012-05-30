//
//  STDetailTextCallout.h
//  Stamped
//
//  Created by Devin Doty on 5/29/12.
//
//

#import <UIKit/UIKit.h>
#import "QuartzUtils.h"

typedef enum {
    STDetailTextCalloutArrowDirectionUp = 0,
    STDetailTextCalloutArrowDirectionDown,
} STDetailTextCalloutArrowDirection;

typedef void (^STDetailTextCompletionHandler) (void);

@interface STDetailTextCallout : UIView {
    CGFloat _arrowLocation;
}

- (id)initWithFrame:(CGRect)frame arrowDirection:(STDetailTextCalloutArrowDirection)direction;

@property(nonatomic,readonly) STDetailTextCalloutArrowDirection arrowDirection; // default FTTextCalloutArrowDirectionDown
@property(nonatomic,assign,getter = isSticky) BOOL sticky; // explicit dismissal
@property(nonatomic,copy) STDetailTextCompletionHandler completion; // used  when sticky is true

@property(nonatomic,retain) UILabel *titleLabel; // mutiple lines, default nil
@property(nonatomic,retain) UILabel *subTitleLabel; // mutiple lines, default nil
@property(nonatomic,retain) UILabel *detailTitleLabel; // single line, default nil

- (void)showCalloutFromRect:(CGRect)rect animated:(BOOL)animated;
- (void)showCalloutFromPoint:(CGPoint)point animated:(BOOL)animated;
- (void)hide;
- (void)hideDelayed:(float)delay;
@end
